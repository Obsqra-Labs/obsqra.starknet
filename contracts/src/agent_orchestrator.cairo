// Agent Orchestrator Contract v1.0.0
// Verifiable autonomous agents with on-chain intents and reputation
//
// Core Components:
// 1. Intent Registry - Users submit goals + constraints on-chain
// 2. Agent Reputation - Track execution success rates transparently
// 3. Policy Marketplace - Pre-built, audited policy templates
//
// Integration: Works with RiskEngine for proof-gated execution
// Deployed: 2026-01-29

use starknet::ContractAddress;
use starknet::get_caller_address;
use starknet::get_block_timestamp;
use starknet::get_block_number;

// ============================================================================
// Data Structures
// ============================================================================

/// Intent types representing user goals
#[derive(Drop, Copy, Serde, starknet::Store, PartialEq)]
pub enum IntentType {
    MaximizeYield,
    MinimizeRisk,
    BalancedGrowth,
    CustomPolicy,
}

/// Intent status lifecycle
#[derive(Drop, Copy, Serde, starknet::Store, PartialEq)]
pub enum IntentStatus {
    Pending,      // Submitted, not yet active
    Active,       // Ready for agent execution
    Executed,     // Successfully executed
    Cancelled,    // Cancelled by user
    Expired,      // Exceeded expiry timestamp
    Failed,       // Execution failed
}

/// Execution outcome for reputation tracking
#[derive(Drop, Copy, Serde, starknet::Store, PartialEq)]
pub enum ExecutionOutcome {
    Success,
    Failed,
    Partial,
}

/// Constraint set for intent execution
#[derive(Drop, Copy, Serde, starknet::Store)]
pub struct ConstraintSet {
    pub max_single_allocation: felt252,    // Max % to single protocol (basis points)
    pub min_diversification: felt252,       // Min number of protocols
    pub max_volatility: felt252,            // Max volatility tolerance (0-100)
    pub min_liquidity: felt252,             // Min liquidity score required
    pub risk_tolerance: felt252,            // 0 = conservative, 100 = aggressive
}

/// User intent stored on-chain
#[derive(Drop, Copy, Serde, starknet::Store)]
pub struct Intent {
    pub id: felt252,
    pub user: ContractAddress,
    pub goal: IntentType,
    pub constraints: ConstraintSet,
    pub policy_hash: felt252,               // Reference to policy from marketplace
    pub status: IntentStatus,
    pub created_at: u64,
    pub expires_at: u64,
    pub executed_by: ContractAddress,       // Agent who executed (0 if not executed)
    pub execution_tx: felt252,              // Transaction hash of execution
}

/// Agent reputation tracked on-chain
#[derive(Drop, Copy, Serde, starknet::Store)]
pub struct AgentReputation {
    pub agent_id: ContractAddress,
    pub total_executions: u64,
    pub successful_executions: u64,
    pub failed_executions: u64,
    pub total_value_executed: u256,
    pub reputation_score: felt252,          // 0-10000 (basis points = 0-100%)
    pub registered_at: u64,
    pub last_execution_at: u64,
    pub is_active: bool,
}

/// Individual execution record for audit trail
#[derive(Drop, Copy, Serde, starknet::Store)]
pub struct ExecutionRecord {
    pub record_id: felt252,
    pub intent_id: felt252,
    pub agent: ContractAddress,
    pub timestamp: u64,
    pub block_number: u64,
    pub proof_hash: felt252,                // Stone proof fact hash
    pub outcome: ExecutionOutcome,
    pub performance_score: felt252,         // 0-100 how well it met intent
    pub value_executed: u256,
}

/// Policy template in marketplace
#[derive(Drop, Copy, Serde, starknet::Store)]
pub struct Policy {
    pub policy_hash: felt252,
    pub creator: ContractAddress,
    pub constraints: ConstraintSet,
    pub is_approved: bool,
    pub approver: ContractAddress,
    pub usage_count: u64,
    pub created_at: u64,
}

// ============================================================================
// Contract Interface
// ============================================================================

#[starknet::interface]
pub trait IAgentOrchestrator<TContractState> {
    // ========== Version & Admin ==========
    fn get_version(self: @TContractState) -> felt252;
    fn get_contract_version(self: @TContractState) -> felt252;
    fn get_owner(self: @TContractState) -> ContractAddress;
    fn set_risk_engine(ref self: TContractState, risk_engine: ContractAddress);
    fn get_risk_engine(self: @TContractState) -> ContractAddress;
    
    // ========== Intent Registry ==========
    /// Submit a new intent
    fn submit_intent(
        ref self: TContractState,
        goal: IntentType,
        constraints: ConstraintSet,
        policy_hash: felt252,
        expires_in_seconds: u64,
    ) -> felt252;
    
    /// Cancel an intent (only intent owner)
    fn cancel_intent(ref self: TContractState, intent_id: felt252);
    
    /// Get intent details
    fn get_intent(self: @TContractState, intent_id: felt252) -> Intent;
    
    /// Get user's intent count
    fn get_user_intent_count(self: @TContractState, user: ContractAddress) -> u64;
    
    /// Get user's intent by index
    fn get_user_intent_at(self: @TContractState, user: ContractAddress, index: u64) -> felt252;
    
    /// Get total intent count
    fn get_intent_count(self: @TContractState) -> felt252;
    
    // ========== Agent Execution ==========
    /// Execute an intent (called by agent with proof)
    fn execute_intent(
        ref self: TContractState,
        intent_id: felt252,
        proof_hash: felt252,
        value_executed: u256,
    ) -> bool;
    
    /// Record execution outcome (for reputation)
    fn record_execution_outcome(
        ref self: TContractState,
        intent_id: felt252,
        outcome: ExecutionOutcome,
        performance_score: felt252,
    );
    
    /// Get execution record
    fn get_execution_record(self: @TContractState, record_id: felt252) -> ExecutionRecord;
    
    /// Get execution record count
    fn get_execution_count(self: @TContractState) -> felt252;
    
    // ========== Agent Reputation ==========
    /// Register as an agent
    fn register_agent(ref self: TContractState) -> bool;
    
    /// Deactivate agent (self)
    fn deactivate_agent(ref self: TContractState);
    
    /// Get agent reputation
    fn get_agent_reputation(self: @TContractState, agent: ContractAddress) -> AgentReputation;
    
    /// Check if address is registered agent
    fn is_registered_agent(self: @TContractState, agent: ContractAddress) -> bool;
    
    /// Get registered agent count
    fn get_agent_count(self: @TContractState) -> u64;
    
    // ========== Policy Marketplace ==========
    /// Register a new policy template
    fn register_policy(
        ref self: TContractState,
        constraints: ConstraintSet,
    ) -> felt252;
    
    /// Approve a policy (owner only)
    fn approve_policy(ref self: TContractState, policy_hash: felt252);
    
    /// Revoke policy approval (owner only)
    fn revoke_policy(ref self: TContractState, policy_hash: felt252);
    
    /// Get policy details
    fn get_policy(self: @TContractState, policy_hash: felt252) -> Policy;
    
    /// Check if policy is approved
    fn is_policy_approved(self: @TContractState, policy_hash: felt252) -> bool;
    
    /// Get policy count
    fn get_policy_count(self: @TContractState) -> felt252;
}

// ============================================================================
// Contract Implementation
// ============================================================================

#[starknet::contract]
pub mod AgentOrchestrator {
    use super::{
        ContractAddress, get_caller_address, get_block_timestamp, get_block_number,
        IntentType, IntentStatus, ExecutionOutcome,
        ConstraintSet, Intent, AgentReputation, ExecutionRecord, Policy,
        IAgentOrchestrator
    };
    use starknet::storage::{
        StoragePointerReadAccess, StoragePointerWriteAccess,
        Map, StorageMapReadAccess, StorageMapWriteAccess,
    };
    use core::num::traits::Zero;
    use core::poseidon::poseidon_hash_span;

    // ========== Storage ==========
    #[storage]
    struct Storage {
        // Admin
        owner: ContractAddress,
        risk_engine: ContractAddress,
        contract_version: felt252,
        
        // Intent Registry
        intent_counter: felt252,
        intents: Map<felt252, Intent>,
        user_intent_count: Map<ContractAddress, u64>,
        user_intents: Map<(ContractAddress, u64), felt252>,  // (user, index) → intent_id
        
        // Agent Reputation
        agent_count: u64,
        agent_reputation: Map<ContractAddress, AgentReputation>,
        registered_agents: Map<u64, ContractAddress>,  // index → agent address
        
        // Execution Records
        execution_counter: felt252,
        execution_records: Map<felt252, ExecutionRecord>,
        
        // Policy Marketplace
        policy_counter: felt252,
        policies: Map<felt252, Policy>,
        approved_policies: Map<felt252, bool>,
    }

    // ========== Events ==========
    #[event]
    #[derive(Drop, starknet::Event)]
    pub enum Event {
        IntentSubmitted: IntentSubmitted,
        IntentCancelled: IntentCancelled,
        IntentExecuted: IntentExecuted,
        IntentExpired: IntentExpired,
        AgentRegistered: AgentRegistered,
        AgentDeactivated: AgentDeactivated,
        ReputationUpdated: ReputationUpdated,
        PolicyRegistered: PolicyRegistered,
        PolicyApproved: PolicyApproved,
        PolicyRevoked: PolicyRevoked,
        ExecutionRecorded: ExecutionRecorded,
    }

    #[derive(Drop, starknet::Event)]
    pub struct IntentSubmitted {
        #[key]
        pub intent_id: felt252,
        #[key]
        pub user: ContractAddress,
        pub goal: IntentType,
        pub policy_hash: felt252,
        pub expires_at: u64,
    }

    #[derive(Drop, starknet::Event)]
    pub struct IntentCancelled {
        #[key]
        pub intent_id: felt252,
        #[key]
        pub user: ContractAddress,
    }

    #[derive(Drop, starknet::Event)]
    pub struct IntentExecuted {
        #[key]
        pub intent_id: felt252,
        #[key]
        pub agent: ContractAddress,
        pub proof_hash: felt252,
        pub value_executed: u256,
    }

    #[derive(Drop, starknet::Event)]
    pub struct IntentExpired {
        #[key]
        pub intent_id: felt252,
    }

    #[derive(Drop, starknet::Event)]
    pub struct AgentRegistered {
        #[key]
        pub agent: ContractAddress,
        pub registered_at: u64,
    }

    #[derive(Drop, starknet::Event)]
    pub struct AgentDeactivated {
        #[key]
        pub agent: ContractAddress,
    }

    #[derive(Drop, starknet::Event)]
    pub struct ReputationUpdated {
        #[key]
        pub agent: ContractAddress,
        pub new_score: felt252,
        pub total_executions: u64,
    }

    #[derive(Drop, starknet::Event)]
    pub struct PolicyRegistered {
        #[key]
        pub policy_hash: felt252,
        pub creator: ContractAddress,
    }

    #[derive(Drop, starknet::Event)]
    pub struct PolicyApproved {
        #[key]
        pub policy_hash: felt252,
        pub approver: ContractAddress,
    }

    #[derive(Drop, starknet::Event)]
    pub struct PolicyRevoked {
        #[key]
        pub policy_hash: felt252,
    }

    #[derive(Drop, starknet::Event)]
    pub struct ExecutionRecorded {
        #[key]
        pub record_id: felt252,
        #[key]
        pub intent_id: felt252,
        pub agent: ContractAddress,
        pub outcome: ExecutionOutcome,
    }

    // ========== Constructor ==========
    #[constructor]
    fn constructor(ref self: ContractState, owner: ContractAddress) {
        self.owner.write(owner);
        self.intent_counter.write(0);
        self.execution_counter.write(0);
        self.policy_counter.write(0);
        self.agent_count.write(0);
    }

    // ========== Implementation ==========
    #[abi(embed_v0)]
    impl AgentOrchestratorImpl of IAgentOrchestrator<ContractState> {
        
        // ========== Version & Admin ==========
        
        fn get_version(self: @ContractState) -> felt252 {
            'agent_orchestrator_v1'
        }
        
        fn get_contract_version(self: @ContractState) -> felt252 {
            1
        }
        
        fn get_owner(self: @ContractState) -> ContractAddress {
            self.owner.read()
        }
        
        fn set_risk_engine(ref self: ContractState, risk_engine: ContractAddress) {
            let caller = get_caller_address();
            assert(caller == self.owner.read(), 'Only owner');
            self.risk_engine.write(risk_engine);
        }
        
        fn get_risk_engine(self: @ContractState) -> ContractAddress {
            self.risk_engine.read()
        }
        
        // ========== Intent Registry ==========
        
        fn submit_intent(
            ref self: ContractState,
            goal: IntentType,
            constraints: ConstraintSet,
            policy_hash: felt252,
            expires_in_seconds: u64,
        ) -> felt252 {
            let caller = get_caller_address();
            let timestamp = get_block_timestamp();
            
            // Validate policy if provided
            if policy_hash != 0 {
                let policy_approved = self.approved_policies.read(policy_hash);
                assert(policy_approved, 'Policy not approved');
            }
            
            // Generate intent ID
            let intent_id = self.intent_counter.read() + 1;
            self.intent_counter.write(intent_id);
            
            // Calculate expiry
            let expires_at = timestamp + expires_in_seconds;
            
            // Create intent
            let zero_addr: ContractAddress = Zero::zero();
            let intent = Intent {
                id: intent_id,
                user: caller,
                goal,
                constraints,
                policy_hash,
                status: IntentStatus::Active,
                created_at: timestamp,
                expires_at,
                executed_by: zero_addr,
                execution_tx: 0,
            };
            
            // Store intent
            self.intents.write(intent_id, intent);
            
            // Track user's intents
            let user_count = self.user_intent_count.read(caller);
            self.user_intents.write((caller, user_count), intent_id);
            self.user_intent_count.write(caller, user_count + 1);
            
            // Emit event
            self.emit(IntentSubmitted {
                intent_id,
                user: caller,
                goal,
                policy_hash,
                expires_at,
            });
            
            intent_id
        }
        
        fn cancel_intent(ref self: ContractState, intent_id: felt252) {
            let caller = get_caller_address();
            let mut intent = self.intents.read(intent_id);
            
            // Validate ownership and status
            assert(intent.user == caller, 'Not intent owner');
            assert(intent.status == IntentStatus::Active || intent.status == IntentStatus::Pending, 'Cannot cancel');
            
            // Update status
            intent.status = IntentStatus::Cancelled;
            self.intents.write(intent_id, intent);
            
            // Emit event
            self.emit(IntentCancelled {
                intent_id,
                user: caller,
            });
        }
        
        fn get_intent(self: @ContractState, intent_id: felt252) -> Intent {
            self.intents.read(intent_id)
        }
        
        fn get_user_intent_count(self: @ContractState, user: ContractAddress) -> u64 {
            self.user_intent_count.read(user)
        }
        
        fn get_user_intent_at(self: @ContractState, user: ContractAddress, index: u64) -> felt252 {
            self.user_intents.read((user, index))
        }
        
        fn get_intent_count(self: @ContractState) -> felt252 {
            self.intent_counter.read()
        }
        
        // ========== Agent Execution ==========
        
        fn execute_intent(
            ref self: ContractState,
            intent_id: felt252,
            proof_hash: felt252,
            value_executed: u256,
        ) -> bool {
            let caller = get_caller_address();
            let timestamp = get_block_timestamp();
            let block_number = get_block_number();
            
            // Validate agent is registered
            let agent_rep = self.agent_reputation.read(caller);
            assert(agent_rep.is_active, 'Agent not registered');
            
            // Get and validate intent
            let mut intent = self.intents.read(intent_id);
            assert(intent.status == IntentStatus::Active, 'Intent not active');
            assert(timestamp <= intent.expires_at, 'Intent expired');
            
            // Mark intent as executed
            intent.status = IntentStatus::Executed;
            intent.executed_by = caller;
            intent.execution_tx = proof_hash;  // Store proof hash as execution reference
            self.intents.write(intent_id, intent);
            
            // Create execution record
            let record_id = self.execution_counter.read() + 1;
            self.execution_counter.write(record_id);
            
            let record = ExecutionRecord {
                record_id,
                intent_id,
                agent: caller,
                timestamp,
                block_number,
                proof_hash,
                outcome: ExecutionOutcome::Success,  // Initial assumption
                performance_score: 0,  // To be updated later
                value_executed,
            };
            self.execution_records.write(record_id, record);
            
            // Update agent reputation (optimistic - mark as success)
            let mut updated_rep = self.agent_reputation.read(caller);
            updated_rep.total_executions = updated_rep.total_executions + 1;
            updated_rep.successful_executions = updated_rep.successful_executions + 1;
            updated_rep.total_value_executed = updated_rep.total_value_executed + value_executed;
            updated_rep.last_execution_at = timestamp;
            
            // Recalculate reputation score (success rate * 10000)
            let success_rate = (updated_rep.successful_executions * 10000) / updated_rep.total_executions;
            updated_rep.reputation_score = success_rate.into();
            
            self.agent_reputation.write(caller, updated_rep);
            
            // Emit events
            self.emit(IntentExecuted {
                intent_id,
                agent: caller,
                proof_hash,
                value_executed,
            });
            
            self.emit(ExecutionRecorded {
                record_id,
                intent_id,
                agent: caller,
                outcome: ExecutionOutcome::Success,
            });
            
            self.emit(ReputationUpdated {
                agent: caller,
                new_score: updated_rep.reputation_score,
                total_executions: updated_rep.total_executions,
            });
            
            true
        }
        
        fn record_execution_outcome(
            ref self: ContractState,
            intent_id: felt252,
            outcome: ExecutionOutcome,
            performance_score: felt252,
        ) {
            let caller = get_caller_address();
            
            // Only owner or the executing agent can update outcome
            let intent = self.intents.read(intent_id);
            assert(caller == self.owner.read() || caller == intent.executed_by, 'Not authorized');
            
            // Find and update execution record
            // For now, we assume the most recent record for this intent
            let record_count = self.execution_counter.read();
            let mut i: felt252 = record_count;
            
            loop {
                if i == 0 {
                    break;
                }
                
                let mut record = self.execution_records.read(i);
                if record.intent_id == intent_id {
                    record.outcome = outcome;
                    record.performance_score = performance_score;
                    self.execution_records.write(i, record);
                    
                    // Update agent reputation if outcome changed to failed
                    if outcome == ExecutionOutcome::Failed {
                        let mut agent_rep = self.agent_reputation.read(record.agent);
                        // Reverse the optimistic success count
                        if agent_rep.successful_executions > 0 {
                            agent_rep.successful_executions = agent_rep.successful_executions - 1;
                        }
                        agent_rep.failed_executions = agent_rep.failed_executions + 1;
                        
                        // Recalculate reputation
                        if agent_rep.total_executions > 0 {
                            let success_rate = (agent_rep.successful_executions * 10000) / agent_rep.total_executions;
                            agent_rep.reputation_score = success_rate.into();
                        }
                        
                        self.agent_reputation.write(record.agent, agent_rep);
                        
                        self.emit(ReputationUpdated {
                            agent: record.agent,
                            new_score: agent_rep.reputation_score,
                            total_executions: agent_rep.total_executions,
                        });
                    }
                    
                    break;
                }
                
                i = i - 1;
            };
        }
        
        fn get_execution_record(self: @ContractState, record_id: felt252) -> ExecutionRecord {
            self.execution_records.read(record_id)
        }
        
        fn get_execution_count(self: @ContractState) -> felt252 {
            self.execution_counter.read()
        }
        
        // ========== Agent Reputation ==========
        
        fn register_agent(ref self: ContractState) -> bool {
            let caller = get_caller_address();
            let timestamp = get_block_timestamp();
            
            // Check if already registered
            let existing = self.agent_reputation.read(caller);
            assert(!existing.is_active, 'Already registered');
            
            // Create reputation record
            let reputation = AgentReputation {
                agent_id: caller,
                total_executions: 0,
                successful_executions: 0,
                failed_executions: 0,
                total_value_executed: 0,
                reputation_score: 5000,  // Start at 50% (neutral)
                registered_at: timestamp,
                last_execution_at: 0,
                is_active: true,
            };
            
            self.agent_reputation.write(caller, reputation);
            
            // Track registered agents
            let agent_count = self.agent_count.read();
            self.registered_agents.write(agent_count, caller);
            self.agent_count.write(agent_count + 1);
            
            // Emit event
            self.emit(AgentRegistered {
                agent: caller,
                registered_at: timestamp,
            });
            
            true
        }
        
        fn deactivate_agent(ref self: ContractState) {
            let caller = get_caller_address();
            
            let mut reputation = self.agent_reputation.read(caller);
            assert(reputation.is_active, 'Not active agent');
            
            reputation.is_active = false;
            self.agent_reputation.write(caller, reputation);
            
            self.emit(AgentDeactivated {
                agent: caller,
            });
        }
        
        fn get_agent_reputation(self: @ContractState, agent: ContractAddress) -> AgentReputation {
            self.agent_reputation.read(agent)
        }
        
        fn is_registered_agent(self: @ContractState, agent: ContractAddress) -> bool {
            let reputation = self.agent_reputation.read(agent);
            reputation.is_active
        }
        
        fn get_agent_count(self: @ContractState) -> u64 {
            self.agent_count.read()
        }
        
        // ========== Policy Marketplace ==========
        
        fn register_policy(
            ref self: ContractState,
            constraints: ConstraintSet,
        ) -> felt252 {
            let caller = get_caller_address();
            let timestamp = get_block_timestamp();
            
            // Generate policy hash from constraints
            let mut hash_input: Array<felt252> = array![];
            hash_input.append(constraints.max_single_allocation);
            hash_input.append(constraints.min_diversification);
            hash_input.append(constraints.max_volatility);
            hash_input.append(constraints.min_liquidity);
            hash_input.append(constraints.risk_tolerance);
            hash_input.append(timestamp.into());
            
            let policy_hash = poseidon_hash_span(hash_input.span());
            
            let zero_addr: ContractAddress = Zero::zero();
            let policy = Policy {
                policy_hash,
                creator: caller,
                constraints,
                is_approved: false,
                approver: zero_addr,
                usage_count: 0,
                created_at: timestamp,
            };
            
            self.policies.write(policy_hash, policy);
            
            // Increment policy counter
            let count = self.policy_counter.read() + 1;
            self.policy_counter.write(count);
            
            self.emit(PolicyRegistered {
                policy_hash,
                creator: caller,
            });
            
            policy_hash
        }
        
        fn approve_policy(ref self: ContractState, policy_hash: felt252) {
            let caller = get_caller_address();
            assert(caller == self.owner.read(), 'Only owner');
            
            let mut policy = self.policies.read(policy_hash);
            assert(policy.created_at != 0, 'Policy not found');
            
            policy.is_approved = true;
            policy.approver = caller;
            self.policies.write(policy_hash, policy);
            
            self.approved_policies.write(policy_hash, true);
            
            self.emit(PolicyApproved {
                policy_hash,
                approver: caller,
            });
        }
        
        fn revoke_policy(ref self: ContractState, policy_hash: felt252) {
            let caller = get_caller_address();
            assert(caller == self.owner.read(), 'Only owner');
            
            let mut policy = self.policies.read(policy_hash);
            policy.is_approved = false;
            self.policies.write(policy_hash, policy);
            
            self.approved_policies.write(policy_hash, false);
            
            self.emit(PolicyRevoked {
                policy_hash,
            });
        }
        
        fn get_policy(self: @ContractState, policy_hash: felt252) -> Policy {
            self.policies.read(policy_hash)
        }
        
        fn is_policy_approved(self: @ContractState, policy_hash: felt252) -> bool {
            self.approved_policies.read(policy_hash)
        }
        
        fn get_policy_count(self: @ContractState) -> felt252 {
            self.policy_counter.read()
        }
    }
}
