
#[starknet::interface]
pub trait IRiskEngine<TContractState> {
    // Existing functions
    fn calculate_risk_score(
        ref self: TContractState,
        utilization: felt252,
        volatility: felt252,
        liquidity: felt252,
        audit_score: felt252,
        age_days: felt252
    ) -> felt252;
    
    fn calculate_allocation(
        ref self: TContractState,
        nostra_risk: felt252,
        zklend_risk: felt252,
        ekubo_risk: felt252,
        nostra_apy: felt252,
        zklend_apy: felt252,
        ekubo_apy: felt252
    ) -> (felt252, felt252, felt252);
    
    fn verify_constraints(
        ref self: TContractState,
        nostra_pct: felt252,
        zklend_pct: felt252,
        ekubo_pct: felt252,
        max_single: felt252,
        min_diversification: felt252
    ) -> bool;
    
    // NEW: Full orchestration function
    fn propose_and_execute_allocation(
        ref self: TContractState,
        jediswap_metrics: ProtocolMetrics,
        ekubo_metrics: ProtocolMetrics,
    ) -> AllocationDecision;
    
    // NEW: Query protocol APY on-chain
    fn query_jediswap_apy(ref self: TContractState) -> felt252;
    fn query_ekubo_apy(ref self: TContractState) -> felt252;
    
    // NEW: Update stored APY values (for keepers)
    fn update_protocol_apy(
        ref self: TContractState,
        protocol: felt252,  // 0=JediSwap, 1=Ekubo
        apy: felt252,
    );
    
    // NEW: Record performance snapshot
    fn record_performance_snapshot(
        ref self: TContractState,
        decision_id: felt252,
        total_value: u256,
        jediswap_value: u256,
        ekubo_value: u256,
    );
    
    // NEW: Get decision and performance data
    fn get_decision(ref self: TContractState, decision_id: felt252) -> AllocationDecision;
    fn get_performance_snapshot(
        ref self: TContractState,
        decision_id: felt252,
    ) -> PerformanceSnapshot;
    
    fn get_decision_count(ref self: TContractState) -> felt252;
}

#[derive(Drop, Serde, starknet::Store)]
struct ProtocolMetrics {
    utilization: felt252,
    volatility: felt252,
    liquidity: felt252,
    audit_score: felt252,
    age_days: felt252,
}

#[derive(Drop, Serde, starknet::Store)]
struct AllocationDecision {
    decision_id: felt252,
    block_number: u64,
    timestamp: u64,
    jediswap_pct: felt252,
    ekubo_pct: felt252,
    jediswap_risk: felt252,
    ekubo_risk: felt252,
    jediswap_apy: felt252,
    ekubo_apy: felt252,
    dao_constraints: DAOConstraints,
    rationale_hash: felt252,
    strategy_router_tx: felt252,
}

#[derive(Drop, Serde, starknet::Store)]
struct DAOConstraints {
    max_single: felt252,
    min_diversification: felt252,
    max_volatility: felt252,
    min_liquidity: felt252,
}

#[derive(Drop, Serde, starknet::Store)]
struct PerformanceSnapshot {
    decision_id: felt252,
    timestamp: u64,
    total_value: u256,
    jediswap_value: u256,
    ekubo_value: u256,
    jediswap_yield: u256,
    ekubo_yield: u256,
    performance_delta: u256,  // Absolute delta (sign handled separately)
    is_positive_delta: bool,  // true = positive, false = negative
}

#[starknet::contract]
mod RiskEngine {
    use super::{ProtocolMetrics, AllocationDecision, DAOConstraints, PerformanceSnapshot};
    use starknet::ContractAddress;
    use starknet::get_block_number;
    use starknet::get_block_timestamp;
    use starknet::get_caller_address;
    use starknet::storage::{StoragePointerWriteAccess, StoragePointerReadAccess};
    use core::traits::Into;
    use core::traits::TryInto;
    use core::option::OptionTrait;
    use core::num::traits::DivRem;
    
    // Import interfaces
    use super::super::strategy_router_v2::IStrategyRouterV2Dispatcher;
    use super::super::strategy_router_v2::IStrategyRouterV2DispatcherTrait;
    use super::super::dao_constraint_manager::IDAOConstraintManagerDispatcher;
    use super::super::dao_constraint_manager::IDAOConstraintManagerDispatcherTrait;
    
    #[storage]
    struct Storage {
        owner: ContractAddress,
        strategy_router: ContractAddress,
        dao_manager: ContractAddress,
        
        // Audit trail storage (simplified for MVP - full history can be added later)
        decision_counter: felt252,
        latest_decision: AllocationDecision,
        latest_decision_id: felt252,
        
        // Performance tracking
        latest_performance: PerformanceSnapshot,
        previous_performance: PerformanceSnapshot,
        
        // Stored APY values (updated by keepers)
        jediswap_apy: felt252,
        ekubo_apy: felt252,
    }
    
    #[event]
    #[derive(Drop, starknet::Event)]
    enum Event {
        AllocationProposed: AllocationProposed,
        AllocationExecuted: AllocationExecuted,
        ConstraintsValidated: ConstraintsValidated,
        ProtocolMetricsQueried: ProtocolMetricsQueried,
        PerformanceRecorded: PerformanceRecorded,
        DecisionRationale: DecisionRationale,
        APYQueried: APYQueried,
        APYUpdated: APYUpdated,
    }
    
    #[derive(Drop, starknet::Event)]
    struct AllocationProposed {
        decision_id: felt252,
        jediswap_pct: felt252,
        ekubo_pct: felt252,
        rationale_hash: felt252,
        block_number: u64,
    }
    
    #[derive(Drop, starknet::Event)]
    struct AllocationExecuted {
        decision_id: felt252,
        strategy_router_tx: felt252,
        timestamp: u64,
        block_number: u64,
    }
    
    #[derive(Drop, starknet::Event)]
    struct ConstraintsValidated {
        decision_id: felt252,
        max_single: felt252,
        min_diversification: felt252,
        passed: bool,
        jediswap_pct: felt252,
        ekubo_pct: felt252,
    }
    
    #[derive(Drop, starknet::Event)]
    struct ProtocolMetricsQueried {
        protocol: felt252,  // 0=JediSwap, 1=Ekubo
        risk_score: felt252,
        utilization: felt252,
        volatility: felt252,
        liquidity: felt252,
        audit_score: felt252,
        age_days: felt252,
        timestamp: u64,
    }
    
    #[derive(Drop, starknet::Event)]
    struct APYQueried {
        protocol: felt252,
        apy: felt252,
        source: felt252,  // 0=stored, 1=oracle, 2=protocol_contract
        timestamp: u64,
    }
    
    #[derive(Drop, starknet::Event)]
    struct APYUpdated {
        protocol: felt252,
        old_apy: felt252,
        new_apy: felt252,
        timestamp: u64,
    }
    
    #[derive(Drop, starknet::Event)]
    struct PerformanceRecorded {
        decision_id: felt252,
        total_value: u256,
        jediswap_value: u256,
        ekubo_value: u256,
        jediswap_yield: u256,
        ekubo_yield: u256,
        total_yield: u256,
        performance_delta: u256,
        is_positive_delta: bool,
        timestamp: u64,
    }
    
    #[derive(Drop, starknet::Event)]
    struct DecisionRationale {
        decision_id: felt252,
        jediswap_risk: felt252,
        ekubo_risk: felt252,
        jediswap_apy: felt252,
        ekubo_apy: felt252,
        jediswap_risk_adj_score: felt252,
        ekubo_risk_adj_score: felt252,
        jediswap_pct: felt252,
        ekubo_pct: felt252,
        calculation_hash: felt252,
    }
    
    #[constructor]
    fn constructor(
        ref self: ContractState,
        owner: ContractAddress,
        strategy_router: ContractAddress,
        dao_manager: ContractAddress,
    ) {
        self.owner.write(owner);
        self.strategy_router.write(strategy_router);
        self.dao_manager.write(dao_manager);
        self.decision_counter.write(0);
        
        // Initialize default APY values (basis points: 850 = 8.5%, 1210 = 12.1%)
        self.jediswap_apy.write(850);
        self.ekubo_apy.write(1210);
        
        // Initialize previous performance
        self.previous_performance.write(PerformanceSnapshot {
            decision_id: 0,
            timestamp: 0,
            total_value: 0_u256,
            jediswap_value: 0_u256,
            ekubo_value: 0_u256,
            jediswap_yield: 0_u256,
            ekubo_yield: 0_u256,
            performance_delta: 0_u256,
            is_positive_delta: true,
        });
    }
    
    // Helper: Convert u256 to felt252
    fn u256_to_felt252(value: u256) -> felt252 {
        value.low.try_into().unwrap()
    }
    
    // Helper: Division using u256
    fn felt252_div(lhs: felt252, rhs: felt252) -> felt252 {
        let lhs_u256: u256 = lhs.into();
        let rhs_u256: u256 = rhs.into();
        let rhs_nonzero = rhs_u256.try_into().unwrap();
        let (quotient, _) = DivRem::div_rem(lhs_u256, rhs_nonzero);
        u256_to_felt252(quotient)
    }
    
    // Helper: Comparison using u256
    fn felt252_gt(lhs: felt252, rhs: felt252) -> bool {
        let lhs_u256: u256 = lhs.into();
        let rhs_u256: u256 = rhs.into();
        lhs_u256 > rhs_u256
    }
    
    #[external(v0)]
    fn calculate_risk_score(
        ref self: ContractState,
        utilization: felt252,
        volatility: felt252,
        liquidity: felt252,
        audit_score: felt252,
        age_days: felt252
    ) -> felt252 {
        // Utilization risk: utilization * 25 / 10000
        let util_product = utilization * 25;
        let utilization_risk = felt252_div(util_product, 10000);
        
        // Volatility risk: volatility * 40 / 10000
        let vol_product = volatility * 40;
        let volatility_risk = felt252_div(vol_product, 10000);
        
        // Liquidity risk: categorical mapping (0=High, 1=Medium, 2=Low, 3=VeryLow)
        let liquidity_risk = if liquidity == 0 {
            0
        } else if liquidity == 1 {
            5
        } else if liquidity == 2 {
            15
        } else {
            30
        };
        
        // Audit risk: (100 - audit_score) * 3 / 10
        let audit_diff = 100 - audit_score;
        let audit_product = audit_diff * 3;
        let audit_risk = felt252_div(audit_product, 10);
        
        // Age risk: max(0, (730 - age_days) * 10 / 730)
        let age_days_u256: u256 = age_days.into();
        let age_risk = if age_days_u256 >= 730_u256 {
            0
        } else {
            let age_diff = 730 - age_days;
            let age_product = age_diff * 10;
            felt252_div(age_product, 730)
        };
        
        // Total score
        let total = utilization_risk + volatility_risk + liquidity_risk + audit_risk + age_risk;
        
        // Clip to 5-95 range
        let total_u256: u256 = total.into();
        if total_u256 < 5_u256 {
            5
        } else if total_u256 > 95_u256 {
            95
        } else {
            total
        }
    }
    
    #[external(v0)]
    fn calculate_allocation(
        ref self: ContractState,
        nostra_risk: felt252,
        zklend_risk: felt252,
        ekubo_risk: felt252,
        nostra_apy: felt252,
        zklend_apy: felt252,
        ekubo_apy: felt252
    ) -> (felt252, felt252, felt252) {
        // Risk-adjusted score = (APY * 10000) / (Risk + 1)
        let divisor_nostra = nostra_risk + 1;
        let divisor_zklend = zklend_risk + 1;
        let divisor_ekubo = ekubo_risk + 1;
        
        // Calculate scores with scaling
        let nostra_product = nostra_apy * 10000;
        let nostra_score = felt252_div(nostra_product, divisor_nostra);
        
        let zklend_product = zklend_apy * 10000;
        let zklend_score = felt252_div(zklend_product, divisor_zklend);
        
        let ekubo_product = ekubo_apy * 10000;
        let ekubo_score = felt252_div(ekubo_product, divisor_ekubo);
        
        let total_score = nostra_score + zklend_score + ekubo_score;
        
        // Calculate percentages (basis points, 10000 = 100%)
        let nostra_pct_product = nostra_score * 10000;
        let nostra_pct = felt252_div(nostra_pct_product, total_score);
        
        let zklend_pct_product = zklend_score * 10000;
        let zklend_pct = felt252_div(zklend_pct_product, total_score);
        
        let ekubo_pct = 10000 - nostra_pct - zklend_pct;
        
        (nostra_pct, zklend_pct, ekubo_pct)
    }
    
    #[external(v0)]
    fn verify_constraints(
        ref self: ContractState,
        nostra_pct: felt252,
        zklend_pct: felt252,
        ekubo_pct: felt252,
        max_single: felt252,
        min_diversification: felt252
    ) -> bool {
        // Find maximum allocation
        let nostra_u256: u256 = nostra_pct.into();
        let zklend_u256: u256 = zklend_pct.into();
        let ekubo_u256: u256 = ekubo_pct.into();
        
        let max_alloc = if nostra_u256 > zklend_u256 {
            if nostra_u256 > ekubo_u256 { nostra_pct } else { ekubo_pct }
        } else {
            if zklend_u256 > ekubo_u256 { zklend_pct } else { ekubo_pct }
        };
        
        // Check max single protocol constraint
        let max_alloc_u256: u256 = max_alloc.into();
        let max_single_u256: u256 = max_single.into();
        if max_alloc_u256 > max_single_u256 {
            return false;
        };
        
        // Check diversification (count protocols with >=10% = 1000 basis points)
        let threshold_u256: u256 = 1000_u256;
        let mut diversification_count = 0;
        if nostra_u256 >= threshold_u256 {
            diversification_count += 1;
        };
        if zklend_u256 >= threshold_u256 {
            diversification_count += 1;
        };
        if ekubo_u256 >= threshold_u256 {
            diversification_count += 1;
        };
        
        // Verify minimum diversification
        let min_div_u256: u256 = min_diversification.into();
        let count_u256: u256 = diversification_count.into();
        if count_u256 < min_div_u256 {
            return false;
        };
        
        true
    }
    
    /// MAIN ORCHESTRATION FUNCTION - 100% On-Chain, Fully Auditable
    #[external(v0)]
    fn propose_and_execute_allocation(
        ref self: ContractState,
        jediswap_metrics: ProtocolMetrics,
        ekubo_metrics: ProtocolMetrics,
    ) -> AllocationDecision {
        let block_number = get_block_number();
        let timestamp = get_block_timestamp();
        
        // Generate unique decision ID
        let decision_id = self.decision_counter.read() + 1;
        self.decision_counter.write(decision_id);
        
        // ============================================
        // STEP 1: Calculate Risk Scores (On-Chain)
        // ============================================
        let jediswap_risk = calculate_risk_score_internal(
            jediswap_metrics.utilization,
            jediswap_metrics.volatility,
            jediswap_metrics.liquidity,
            jediswap_metrics.audit_score,
            jediswap_metrics.age_days,
        );
        
        let ekubo_risk = calculate_risk_score_internal(
            ekubo_metrics.utilization,
            ekubo_metrics.volatility,
            ekubo_metrics.liquidity,
            ekubo_metrics.audit_score,
            ekubo_metrics.age_days,
        );
        
        // Emit: Risk scores calculated (audit trail)
        self.emit(ProtocolMetricsQueried {
            protocol: 0,  // JediSwap
            risk_score: jediswap_risk,
            utilization: jediswap_metrics.utilization,
            volatility: jediswap_metrics.volatility,
            liquidity: jediswap_metrics.liquidity,
            audit_score: jediswap_metrics.audit_score,
            age_days: jediswap_metrics.age_days,
            timestamp,
        });
        
        self.emit(ProtocolMetricsQueried {
            protocol: 1,  // Ekubo
            risk_score: ekubo_risk,
            utilization: ekubo_metrics.utilization,
            volatility: ekubo_metrics.volatility,
            liquidity: ekubo_metrics.liquidity,
            audit_score: ekubo_metrics.audit_score,
            age_days: ekubo_metrics.age_days,
            timestamp,
        });
        
        // ============================================
        // STEP 2: Query Protocol APY On-Chain
        // ============================================
        let jediswap_apy = query_jediswap_apy_internal(ref self);
        let ekubo_apy = query_ekubo_apy_internal(ref self);
        
        // Emit: APY queried (audit trail)
        self.emit(APYQueried {
            protocol: 0,
            apy: jediswap_apy,
            source: 0,  // From stored value (can be updated to 1=oracle, 2=protocol)
            timestamp,
        });
        
        self.emit(APYQueried {
            protocol: 1,
            apy: ekubo_apy,
            source: 0,
            timestamp,
        });
        
        // ============================================
        // STEP 3: Calculate Allocation (On-Chain)
        // ============================================
        // Using 2-protocol version (JediSwap + Ekubo)
        // Pass 0 for nostra/zklend as placeholders
        let (jedi_pct, ekubo_pct, _) = calculate_allocation_internal(
            jediswap_risk,
            ekubo_risk,
            0,  // placeholder for third protocol
            jediswap_apy,
            ekubo_apy,
            0,  // placeholder
        );
        
        // ============================================
        // STEP 4: Get DAO Constraints (On-Chain Read)
        // ============================================
        let dao = IDAOConstraintManagerDispatcher {
            contract_address: self.dao_manager.read()
        };
        let (max_single, min_div, max_vol, min_liq) = dao.get_constraints();
        
        let constraints = DAOConstraints {
            max_single,
            min_diversification: min_div,
            max_volatility: max_vol,
            min_liquidity: min_liq,
        };
        
        // ============================================
        // STEP 5: Validate Against DAO (On-Chain)
        // ============================================
        let is_valid = verify_constraints_2_protocol_internal(
            jedi_pct,
            ekubo_pct,
            max_single,
            min_div,
        );
        
        assert(is_valid, 'DAO constraints violated');
        
        // Emit: Constraints validated (audit trail)
        self.emit(ConstraintsValidated {
            decision_id,
            max_single,
            min_diversification: min_div,
            passed: true,
            jediswap_pct: jedi_pct,
            ekubo_pct: ekubo_pct,
        });
        
        // ============================================
        // STEP 6: Generate Decision Rationale Hash
        // ============================================
        let jedi_risk_adj = felt252_div(jediswap_apy * 10000, jediswap_risk + 1);
        let ekubo_risk_adj = felt252_div(ekubo_apy * 10000, ekubo_risk + 1);
        
        let rationale_hash = compute_rationale_hash_internal(
            jediswap_risk,
            ekubo_risk,
            jediswap_apy,
            ekubo_apy,
            jedi_pct,
            ekubo_pct,
        );
        
        // Emit: Decision rationale (audit trail)
        self.emit(DecisionRationale {
            decision_id,
            jediswap_risk,
            ekubo_risk,
            jediswap_apy,
            ekubo_apy,
            jediswap_risk_adj_score: jedi_risk_adj,
            ekubo_risk_adj_score: ekubo_risk_adj,
            jediswap_pct: jedi_pct,
            ekubo_pct: ekubo_pct,
            calculation_hash: rationale_hash,
        });
        
        // ============================================
        // STEP 7: Emit Proposal (Audit Trail)
        // ============================================
        self.emit(AllocationProposed {
            decision_id,
            jediswap_pct: jedi_pct,
            ekubo_pct: ekubo_pct,
            rationale_hash,
            block_number,
        });
        
        // ============================================
        // STEP 8: Execute on StrategyRouter (On-Chain)
        // ============================================
        let router = IStrategyRouterV2Dispatcher {
            contract_address: self.strategy_router.read()
        };
        
        // RiskEngine is authorized caller
        router.update_allocation(jedi_pct, ekubo_pct);
        
        // In real implementation, we'd get the actual tx hash from the call
        // For now, use decision_id as identifier
        let strategy_router_tx = decision_id;
        
        // ============================================
        // STEP 9: Store Decision (Audit Trail)
        // ============================================
        let decision = AllocationDecision {
            decision_id,
            block_number,
            timestamp,
            jediswap_pct: jedi_pct,
            ekubo_pct: ekubo_pct,
            jediswap_risk,
            ekubo_risk,
            jediswap_apy,
            ekubo_apy,
            dao_constraints: constraints,
            rationale_hash,
            strategy_router_tx,
        };
        
        // Store latest decision (clone for return)
        self.latest_decision.write(decision);
        self.latest_decision_id.write(decision_id);
        
        // Emit: Execution complete (audit trail)
        self.emit(AllocationExecuted {
            decision_id,
            strategy_router_tx,
            timestamp,
            block_number,
        });
        
        // Return stored decision
        self.latest_decision.read()
    }
    
    /// Query JediSwap APY On-Chain
    #[external(v0)]
    fn query_jediswap_apy(ref self: ContractState) -> felt252 {
        // For MVP: Return stored value (updated by keepers)
        // TODO: Implement actual on-chain query from JediSwap contracts
        // This would involve:
        // 1. Getting pool address from factory
        // 2. Querying pool reserves
        // 3. Calculating APY from fees/volume
        
        self.jediswap_apy.read()
    }
    
    /// Query Ekubo APY On-Chain
    #[external(v0)]
    fn query_ekubo_apy(ref self: ContractState) -> felt252 {
        // For MVP: Return stored value (updated by keepers)
        // TODO: Implement actual on-chain query from Ekubo contracts
        // This would involve:
        // 1. Querying Ekubo Price Fetcher or Oracle
        // 2. Getting position value and yield
        // 3. Calculating APY
        
        self.ekubo_apy.read()
    }
    
    /// Update stored APY values (for keepers/oracles)
    #[external(v0)]
    fn update_protocol_apy(
        ref self: ContractState,
        protocol: felt252,  // 0=JediSwap, 1=Ekubo
        apy: felt252,
    ) {
        // For MVP: Allow owner to update
        // In production: Restrict to oracle/keeper contracts
        let owner = self.owner.read();
        assert(get_caller_address() == owner, 'Unauthorized');
        
        let timestamp = get_block_timestamp();
        
        if protocol == 0 {
            // JediSwap
            let old_apy = self.jediswap_apy.read();
            self.jediswap_apy.write(apy);
            self.emit(APYUpdated {
                protocol: 0,
                old_apy,
                new_apy: apy,
                timestamp,
            });
        } else {
            // Ekubo
            let old_apy = self.ekubo_apy.read();
            self.ekubo_apy.write(apy);
            self.emit(APYUpdated {
                protocol: 1,
                old_apy,
                new_apy: apy,
                timestamp,
            });
        }
    }
    
    /// Record Performance Snapshot
    #[external(v0)]
    fn record_performance_snapshot(
        ref self: ContractState,
        decision_id: felt252,
        total_value: u256,
        jediswap_value: u256,
        ekubo_value: u256,
    ) {
        let timestamp = get_block_timestamp();
        
        // Query actual yields from protocols (on-chain)
        // For MVP: Use placeholder values
        // TODO: Implement actual yield queries
        let jediswap_yield = 0_u256;  // Query from JediSwap
        let ekubo_yield = 0_u256;     // Query from Ekubo
        
        // Get previous snapshot for delta calculation
        let previous = self.previous_performance.read();
        let (performance_delta, is_positive) = if previous.total_value > 0_u256 {
            // Calculate delta: current - previous
            if total_value >= previous.total_value {
                // Positive delta
                (total_value - previous.total_value, true)
            } else {
                // Negative delta
                (previous.total_value - total_value, false)
            }
        } else {
            (0_u256, true)
        };
        
        let snapshot = PerformanceSnapshot {
            decision_id,
            timestamp,
            total_value,
            jediswap_value,
            ekubo_value,
            jediswap_yield,
            ekubo_yield,
            performance_delta,
            is_positive_delta: is_positive,
        };
        
        // Store latest snapshot
        self.latest_performance.write(snapshot);
        // Update previous for next delta calculation (read back after write)
        let stored_snapshot = self.latest_performance.read();
        self.previous_performance.write(stored_snapshot);
        
        // Emit: Performance recorded (audit trail)
        self.emit(PerformanceRecorded {
            decision_id,
            total_value,
            jediswap_value,
            ekubo_value,
            jediswap_yield,
            ekubo_yield,
            total_yield: jediswap_yield + ekubo_yield,
            performance_delta,
            is_positive_delta: is_positive,
            timestamp,
        });
    }
    
    /// Get Latest Decision (for audit trail)
    #[external(v0)]
    fn get_decision(
        ref self: ContractState,
        decision_id: felt252,
    ) -> AllocationDecision {
        // For MVP: Return latest decision if ID matches
        let latest_id = self.latest_decision_id.read();
        assert(decision_id == latest_id, 'Decision not found');
        self.latest_decision.read()
    }
    
    /// Get Latest Performance Snapshot
    #[external(v0)]
    fn get_performance_snapshot(
        ref self: ContractState,
        decision_id: felt252,
    ) -> PerformanceSnapshot {
        // For MVP: Return latest performance if ID matches
        let latest_id = self.latest_decision_id.read();
        assert(decision_id == latest_id, 'Performance snapshot not found');
        self.latest_performance.read()
    }
    
    /// Get decision count
    #[external(v0)]
    fn get_decision_count(ref self: ContractState) -> felt252 {
        self.decision_counter.read()
    }
    
    // Helper: Calculate risk score (internal)
    fn calculate_risk_score_internal(
        utilization: felt252,
        volatility: felt252,
        liquidity: felt252,
        audit_score: felt252,
        age_days: felt252
    ) -> felt252 {
        // Utilization risk: utilization * 25 / 10000
        let util_product = utilization * 25;
        let utilization_risk = felt252_div(util_product, 10000);
        
        // Volatility risk: volatility * 40 / 10000
        let vol_product = volatility * 40;
        let volatility_risk = felt252_div(vol_product, 10000);
        
        // Liquidity risk: categorical mapping (0=High, 1=Medium, 2=Low, 3=VeryLow)
        let liquidity_risk = if liquidity == 0 {
            0
        } else if liquidity == 1 {
            5
        } else if liquidity == 2 {
            15
        } else {
            30
        };
        
        // Audit risk: (100 - audit_score) * 3 / 10
        let audit_diff = 100 - audit_score;
        let audit_product = audit_diff * 3;
        let audit_risk = felt252_div(audit_product, 10);
        
        // Age risk: max(0, (730 - age_days) * 10 / 730)
        let age_days_u256: u256 = age_days.into();
        let age_risk = if age_days_u256 >= 730_u256 {
            0
        } else {
            let age_diff = 730 - age_days;
            let age_product = age_diff * 10;
            felt252_div(age_product, 730)
        };
        
        // Total score
        let total = utilization_risk + volatility_risk + liquidity_risk + audit_risk + age_risk;
        
        // Clip to 5-95 range
        let total_u256: u256 = total.into();
        if total_u256 < 5_u256 {
            5
        } else if total_u256 > 95_u256 {
            95
        } else {
            total
        }
    }
    
    // Helper: Calculate allocation (internal)
    fn calculate_allocation_internal(
        nostra_risk: felt252,
        zklend_risk: felt252,
        ekubo_risk: felt252,
        nostra_apy: felt252,
        zklend_apy: felt252,
        ekubo_apy: felt252
    ) -> (felt252, felt252, felt252) {
        // Risk-adjusted score = (APY * 10000) / (Risk + 1)
        let divisor_nostra = nostra_risk + 1;
        let divisor_zklend = zklend_risk + 1;
        let divisor_ekubo = ekubo_risk + 1;
        
        // Calculate scores with scaling
        let nostra_product = nostra_apy * 10000;
        let nostra_score = felt252_div(nostra_product, divisor_nostra);
        
        let zklend_product = zklend_apy * 10000;
        let zklend_score = felt252_div(zklend_product, divisor_zklend);
        
        let ekubo_product = ekubo_apy * 10000;
        let ekubo_score = felt252_div(ekubo_product, divisor_ekubo);
        
        let total_score = nostra_score + zklend_score + ekubo_score;
        
        // Calculate percentages (basis points, 10000 = 100%)
        let nostra_pct_product = nostra_score * 10000;
        let nostra_pct = felt252_div(nostra_pct_product, total_score);
        
        let zklend_pct_product = zklend_score * 10000;
        let zklend_pct = felt252_div(zklend_pct_product, total_score);
        
        let ekubo_pct = 10000 - nostra_pct - zklend_pct;
        
        (nostra_pct, zklend_pct, ekubo_pct)
    }
    
    // Helper: Query JediSwap APY (internal)
    fn query_jediswap_apy_internal(ref self: ContractState) -> felt252 {
        self.jediswap_apy.read()
    }
    
    // Helper: Query Ekubo APY (internal)
    fn query_ekubo_apy_internal(ref self: ContractState) -> felt252 {
        self.ekubo_apy.read()
    }
    
    // Helper: Verify constraints for 2 protocols (internal)
    fn verify_constraints_2_protocol_internal(
        jedi_pct: felt252,
        ekubo_pct: felt252,
        max_single: felt252,
        min_div: felt252,
    ) -> bool {
        let jedi_u256: u256 = jedi_pct.into();
        let ekubo_u256: u256 = ekubo_pct.into();
        let max_single_u256: u256 = max_single.into();
        
        // Check max single protocol
        if jedi_u256 > max_single_u256 || ekubo_u256 > max_single_u256 {
            return false;
        };
        
        // Check diversification (both must be >= 10% = 1000 basis points)
        let threshold: u256 = 1000_u256;
        let mut count = 0;
        if jedi_u256 >= threshold {
            count += 1;
        };
        if ekubo_u256 >= threshold {
            count += 1;
        };
        
        let count_u256: u256 = count.into();
        let min_div_u256: u256 = min_div.into();
        if count_u256 < min_div_u256 {
            return false;
        };
        
        true
    }
    
    // Helper: Compute rationale hash (internal)
    fn compute_rationale_hash_internal(
        jedi_risk: felt252,
        ekubo_risk: felt252,
        jedi_apy: felt252,
        ekubo_apy: felt252,
        jedi_pct: felt252,
        ekubo_pct: felt252,
    ) -> felt252 {
        // Simple hash of decision inputs
        // In production, use proper hash function (e.g., pedersen_hash)
        jedi_risk + ekubo_risk + jedi_apy + ekubo_apy + jedi_pct + ekubo_pct
    }
}
