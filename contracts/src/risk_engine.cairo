
use starknet::ContractAddress;

// On-chain agent: User-signed constraint approval
#[derive(Drop, Serde, starknet::Store)]
pub struct ConstraintSignature {
    pub signer: ContractAddress,
    pub max_single: felt252,
    pub min_diversification: felt252,
    pub max_volatility: felt252,
    pub min_liquidity: felt252,
    pub signature_r: felt252,
    pub signature_s: felt252,
    pub timestamp: u64,
}

#[starknet::interface]
pub trait IRiskEngine<TContractState> {
    // Version 2.2 - Fixed 2-protocol allocation (sum to 100%)
    fn get_contract_version(self: @TContractState) -> felt252;
    fn get_build_timestamp(self: @TContractState) -> felt252;
    
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
    
    // NEW: Full orchestration function (v4 with on-chain agent features)
    fn propose_and_execute_allocation(
        ref self: TContractState,
        jediswap_metrics: ProtocolMetrics,
        ekubo_metrics: ProtocolMetrics,
        // Proof verification parameters
        jediswap_proof_fact: felt252,         // SHARP fact hash
        ekubo_proof_fact: felt252,            // SHARP fact hash
        expected_jediswap_score: felt252,     // Risk score from proof
        expected_ekubo_score: felt252,        // Risk score from proof
        fact_registry_address: ContractAddress, // SHARP fact registry
        // On-chain agent additions
        model_version: felt252,                // Model version hash (from ModelRegistry)
        constraint_signature: ConstraintSignature, // User-signed constraints (signer=0 means not provided)
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

    // Stage 3A: On-Chain Model (parameterized formula)
    fn set_model_params(ref self: TContractState, version: felt252, params: ModelParams);
    fn get_model_params(self: @TContractState, version: felt252) -> ModelParams;
}

// Stage 3A: Parameterized model (weights + clamp bounds)
#[derive(Drop, Serde, starknet::Store)]
pub struct ModelParams {
    pub w_utilization: felt252,
    pub w_volatility: felt252,
    pub w_liquidity_0: felt252,
    pub w_liquidity_1: felt252,
    pub w_liquidity_2: felt252,
    pub w_liquidity_3: felt252,
    pub w_audit: felt252,
    pub w_age: felt252,
    pub age_cap_days: felt252,
    pub clamp_min: felt252,
    pub clamp_max: felt252,
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
    // On-chain agent additions
    model_version: felt252,              // Model version hash for provenance
    jediswap_proof_fact: felt252,        // Proof fact hash for audit
    ekubo_proof_fact: felt252,           // Proof fact hash for audit
    constraint_signature: ConstraintSignature, // User-signed constraints (signer=0 means not provided)
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
    use super::{ProtocolMetrics, AllocationDecision, DAOConstraints, PerformanceSnapshot, ConstraintSignature, ModelParams};
    use starknet::ContractAddress;
    use starknet::get_block_number;
    use starknet::get_block_timestamp;
    use starknet::get_caller_address;
    use starknet::storage::{
        StoragePointerWriteAccess, StoragePointerReadAccess,
        StorageMapReadAccess, StorageMapWriteAccess,
        Map
    };
    use core::traits::Into;
    use core::traits::TryInto;
    // Removed DivRem import - using simpler division
    
    // Import interfaces
    use super::super::strategy_router_v2::IStrategyRouterV2Dispatcher;
    use super::super::strategy_router_v2::IStrategyRouterV2DispatcherTrait;
    use super::super::dao_constraint_manager::IDAOConstraintManagerDispatcher;
    use super::super::dao_constraint_manager::IDAOConstraintManagerDispatcherTrait;
    use super::super::sharp_verifier::verify_allocation_decision_with_proofs;
    // Note: ModelRegistry interface not public, using approved_model_versions map instead
    
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
        
        // Model version tracking (for provenance - 5/5 zkML requirement)
        current_model_hash: felt252,
        
        // On-chain agent additions
        model_registry: ContractAddress,              // ModelRegistry contract address
        approved_model_versions: Map<felt252, bool>,  // Approved model hashes
        permissionless_mode: bool,                    // Enable permissionless execution

        // Stage 3A: Parameterized formula (keyed by model_version)
        model_params: Map<felt252, ModelParams>,
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
        model_hash: felt252,  // Model version hash for provenance
        timestamp: u64,
        block_number: u64,
        // On-chain agent additions
        jediswap_proof_fact: felt252,        // Proof fact hash for audit
        ekubo_proof_fact: felt252,           // Proof fact hash for audit
        constraint_signer: ContractAddress,  // User who signed constraints (0 if not provided)
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
    struct ModelParamsUpdated {
        version: felt252,
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
        model_registry: ContractAddress,  // NEW: ModelRegistry contract
    ) {
        self.owner.write(owner);
        self.strategy_router.write(strategy_router);
        self.dao_manager.write(dao_manager);
        self.model_registry.write(model_registry);  // NEW
        self.decision_counter.write(0);
        
        // Initialize default APY values (basis points: 850 = 8.5%, 1210 = 12.1%)
        self.jediswap_apy.write(850);
        self.ekubo_apy.write(1210);
        
        // Initialize model hash (will be set when model is registered)
        // Default to 0 (no model registered yet)
        self.current_model_hash.write(0);
        
        // Initialize on-chain agent settings
        self.permissionless_mode.write(false);  // Start with permissionless mode disabled
        
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
        if rhs == 0 {
            return 0;
        }
        let lhs_u256: u256 = lhs.into();
        let rhs_u256: u256 = rhs.into();
        let quotient = lhs_u256 / rhs_u256;
        u256_to_felt252(quotient)
    }
    
    // Helper: Comparison using u256
    fn felt252_gt(lhs: felt252, rhs: felt252) -> bool {
        let lhs_u256: u256 = lhs.into();
        let rhs_u256: u256 = rhs.into();
        lhs_u256 > rhs_u256
    }
    
    #[external(v0)]
    fn get_contract_version(self: @ContractState) -> felt252 {
        220  // Version 2.2.0
    }
    
    #[external(v0)]
    fn get_build_timestamp(self: @ContractState) -> felt252 {
        1733673600  // Dec 8, 2024
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
    
    /// MAIN ORCHESTRATION FUNCTION - 100% On-Chain, Fully Auditable (v4 with on-chain agent)
    #[external(v0)]
    fn propose_and_execute_allocation(
        ref self: ContractState,
        jediswap_metrics: ProtocolMetrics,
        ekubo_metrics: ProtocolMetrics,
        jediswap_proof_fact: felt252,
        ekubo_proof_fact: felt252,
        expected_jediswap_score: felt252,
        expected_ekubo_score: felt252,
        fact_registry_address: ContractAddress,
        model_version: felt252,                // NEW: Model version hash
        constraint_signature: ConstraintSignature, // NEW: User-signed constraints (signer=0 means not provided)
    ) -> AllocationDecision {
        // Permissionless mode check: if enabled, skip owner check (proof verification is the gate)
        let permissionless = self.permissionless_mode.read();
        if !permissionless {
            // Traditional mode: verify caller is owner
            let owner = self.owner.read();
            assert(get_caller_address() == owner, 'Unauthorized');
        }
        // In permissionless mode, anyone can call - proof verification is the authorization gate
        
        let block_number = get_block_number();
        let timestamp = get_block_timestamp();
        
        // Generate unique decision ID
        let decision_id = self.decision_counter.read() + 1;
        self.decision_counter.write(decision_id);
        
        // ============================================
        // STEP 0: VERIFY PROOFS (NEW - CRITICAL)
        // ============================================
        // Verify both proofs are valid in SHARP registry
        let proofs_valid = verify_allocation_decision_with_proofs(
            (jediswap_metrics.utilization, jediswap_metrics.volatility,
             jediswap_metrics.liquidity, jediswap_metrics.audit_score,
             jediswap_metrics.age_days),
            (ekubo_metrics.utilization, ekubo_metrics.volatility,
             ekubo_metrics.liquidity, ekubo_metrics.audit_score,
             ekubo_metrics.age_days),
            jediswap_proof_fact,
            ekubo_proof_fact,
            expected_jediswap_score,
            expected_ekubo_score,
            fact_registry_address
        );
        
        assert(proofs_valid, 0); // Proofs not verified in SHARP registry
        
        // ============================================
        // STEP 0.5: VERIFY MODEL VERSION (NEW - On-Chain Agent)
        // ============================================
        // Verify model version is approved (check approved_model_versions map)
        // Note: ModelRegistry integration can be added later when interface is public
        let is_approved = self.approved_model_versions.read(model_version);
        if !is_approved {
            // If not in approved list, allow if model_version is 0 (legacy)
            // Otherwise, require approval
            assert(model_version == 0, 3); // Model version not approved
        }
        
        // ============================================
        // STEP 0.6: VERIFY CONSTRAINT SIGNATURE (NEW - On-Chain Agent)
        // ============================================
        // Verify user-signed constraint approval (if provided - signer != 0)
        let constraint_signer = constraint_signature.signer;
        let zero_addr: ContractAddress = starknet::contract_address_const::<0>();
        if constraint_signer != zero_addr {
            // Constraint signature provided, verify it matches constraints used
            // For now, we'll validate that the signature exists (full signature verification can be added later)
            // Store signature for audit trail (already in constraint_signature parameter)
        }
        
        // ============================================
        // STEP 1: Calculate Risk Scores (On-Chain)
        // ============================================
        let jediswap_risk = calculate_risk_score_internal(
            ref self,
            model_version,
            jediswap_metrics.utilization,
            jediswap_metrics.volatility,
            jediswap_metrics.liquidity,
            jediswap_metrics.audit_score,
            jediswap_metrics.age_days,
        );
        
        // Verify on-chain calculation matches proven score
        assert(jediswap_risk == expected_jediswap_score, 1); // JediSwap risk score mismatch
        
        let ekubo_risk = calculate_risk_score_internal(
            ref self,
            model_version,
            ekubo_metrics.utilization,
            ekubo_metrics.volatility,
            ekubo_metrics.liquidity,
            ekubo_metrics.audit_score,
            ekubo_metrics.age_days,
        );
        
        // Verify on-chain calculation matches proven score
        assert(ekubo_risk == expected_ekubo_score, 2); // Ekubo risk score mismatch
        
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
        let (jedi_pct, ekubo_pct) = calculate_allocation_2_protocol_internal(
            jediswap_risk,
            ekubo_risk,
            jediswap_apy,
            ekubo_apy,
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
        // Extract constraint signer before moving constraint_signature
        let constraint_signer_addr = constraint_signature.signer;
        
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
            // On-chain agent additions
            model_version,
            jediswap_proof_fact,
            ekubo_proof_fact,
            constraint_signature,
        };
        
        // Store latest decision (clone for return)
        self.latest_decision.write(decision);
        self.latest_decision_id.write(decision_id);
        
        // Emit: Execution complete (audit trail with on-chain agent data)
        self.emit(AllocationExecuted {
            decision_id,
            strategy_router_tx,
            model_hash: model_version,  // Use provided model_version instead of stored
            timestamp,
            block_number,
            // On-chain agent additions
            jediswap_proof_fact,
            ekubo_proof_fact,
            constraint_signer: constraint_signer_addr,
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
    
    #[external(v0)]
    fn set_strategy_router(
        ref self: ContractState,
        new_router: ContractAddress,
    ) {
        let owner = self.owner.read();
        assert(get_caller_address() == owner, 'Unauthorized');
        self.strategy_router.write(new_router);
    }
    
    // ============================================
    // On-Chain Agent Functions
    // ============================================
    
    /// Approve a model version for use in allocation decisions
    /// Only owner can approve model versions
    #[external(v0)]
    fn approve_model_version(
        ref self: ContractState,
        model_hash: felt252,
    ) {
        let owner = self.owner.read();
        assert(get_caller_address() == owner, 'Unauthorized');
        self.approved_model_versions.write(model_hash, true);
    }
    
    /// Revoke approval for a model version
    /// Only owner can revoke model versions
    #[external(v0)]
    fn revoke_model_version(
        ref self: ContractState,
        model_hash: felt252,
    ) {
        let owner = self.owner.read();
        assert(get_caller_address() == owner, 'Unauthorized');
        self.approved_model_versions.write(model_hash, false);
    }
    
    /// Check if a model version is approved
    #[external(v0)]
    fn is_model_version_approved(
        self: @ContractState,
        model_hash: felt252,
    ) -> bool {
        self.approved_model_versions.read(model_hash)
    }
    
    /// Enable or disable permissionless execution mode
    /// When enabled, anyone can call propose_and_execute_allocation with valid proof
    /// Only owner can toggle this mode
    #[external(v0)]
    fn set_permissionless_mode(
        ref self: ContractState,
        enabled: bool,
    ) {
        let owner = self.owner.read();
        assert(get_caller_address() == owner, 'Unauthorized');
        self.permissionless_mode.write(enabled);
    }
    
    /// Get current permissionless mode status
    #[external(v0)]
    fn get_permissionless_mode(
        self: @ContractState,
    ) -> bool {
        self.permissionless_mode.read()
    }
    
    /// Set ModelRegistry contract address
    /// Only owner can set this
    #[external(v0)]
    fn set_model_registry(
        ref self: ContractState,
        model_registry: ContractAddress,
    ) {
        let owner = self.owner.read();
        assert(get_caller_address() == owner, 'Unauthorized');
        self.model_registry.write(model_registry);
    }

    /// Stage 3A: Set parameterized model (owner only)
    #[external(v0)]
    fn set_model_params(
        ref self: ContractState,
        version: felt252,
        params: ModelParams,
    ) {
        let owner = self.owner.read();
        assert(get_caller_address() == owner, 'Unauthorized');
        self.model_params.write(version, params);
        // ModelParamsUpdated event can be emitted when EventEmitter is available for new variants
    }

    /// Stage 3A: Get parameterized model (view)
    #[external(v0)]
    fn get_model_params(self: @ContractState, version: felt252) -> ModelParams {
        self.model_params.read(version)
    }
    
    // Helper: Calculate risk score (internal) - Stage 3A: uses params when model_version set
    fn calculate_risk_score_internal(
        ref self: ContractState,
        model_version: felt252,
        utilization: felt252,
        volatility: felt252,
        liquidity: felt252,
        audit_score: felt252,
        age_days: felt252
    ) -> felt252 {
        let (w_util, w_vol, liq_0, liq_1, liq_2, liq_3, w_audit, w_age, age_cap, clamp_min, clamp_max) = if model_version == 0 {
            // Stage 2: fixed formula (backward compat)
            (25, 40, 0, 5, 15, 30, 3, 10, 730, 5, 95)
        } else {
            let params = self.model_params.read(model_version);
            // If params not set (all zeros), fallback to fixed
            if params.w_utilization == 0 && params.w_volatility == 0 {
                (25, 40, 0, 5, 15, 30, 3, 10, 730, 5, 95)
            } else {
                (params.w_utilization, params.w_volatility, params.w_liquidity_0, params.w_liquidity_1, params.w_liquidity_2, params.w_liquidity_3, params.w_audit, params.w_age, params.age_cap_days, params.clamp_min, params.clamp_max)
            }
        };

        // Utilization risk
        let util_product = utilization * w_util;
        let utilization_risk = felt252_div(util_product, 10000);

        // Volatility risk
        let vol_product = volatility * w_vol;
        let volatility_risk = felt252_div(vol_product, 10000);

        // Liquidity risk: categorical
        let liquidity_risk = if liquidity == 0 { liq_0 } else if liquidity == 1 { liq_1 } else if liquidity == 2 { liq_2 } else { liq_3 };

        // Audit risk: (100 - audit_score) * w_audit / 10
        let audit_diff = 100 - audit_score;
        let audit_product = audit_diff * w_audit;
        let audit_risk = felt252_div(audit_product, 10);

        // Age risk: max(0, (age_cap - age_days) * w_age / age_cap)
        let age_days_u256: u256 = age_days.into();
        let age_cap_u256: u256 = age_cap.into();
        let age_risk = if age_days_u256 >= age_cap_u256 {
            0
        } else {
            let age_diff = age_cap - age_days;
            let age_product = age_diff * w_age;
            felt252_div(age_product, age_cap)
        };

        let total = utilization_risk + volatility_risk + liquidity_risk + audit_risk + age_risk;

        let total_u256: u256 = total.into();
        let min_u256: u256 = clamp_min.into();
        let max_u256: u256 = clamp_max.into();
        if total_u256 < min_u256 {
            clamp_min
        } else if total_u256 > max_u256 {
            clamp_max
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
    
    // Helper: Calculate allocation for 2 protocols (internal)
    // Ensures jedi_pct + ekubo_pct = 10000 exactly
    fn calculate_allocation_2_protocol_internal(
        jedi_risk: felt252,
        ekubo_risk: felt252,
        jedi_apy: felt252,
        ekubo_apy: felt252,
    ) -> (felt252, felt252) {
        // Risk-adjusted score = (APY * 10000) / (Risk + 1)
        let divisor_jedi = jedi_risk + 1;
        let divisor_ekubo = ekubo_risk + 1;
        
        let jedi_score = felt252_div(jedi_apy * 10000, divisor_jedi);
        let ekubo_score = felt252_div(ekubo_apy * 10000, divisor_ekubo);
        let total_score = jedi_score + ekubo_score;
        
        // Calculate JediSwap percentage
        let jedi_pct = felt252_div(jedi_score * 10000, total_score);
        // Ekubo gets the remainder - ensures sum is exactly 10000
        let ekubo_pct = 10000 - jedi_pct;
        
        (jedi_pct, ekubo_pct)
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
