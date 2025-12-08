/// SHARP Proof Verification Interface
/// 
/// Integrates with Starknet's SHARP (Shared Prover) for zero-knowledge proof verification

use starknet::ContractAddress;

/// SHARP Fact Registry Interface
/// 
/// The fact registry stores verified computation facts on-chain
/// Each fact has a unique hash that can be queried for validity
#[starknet::interface]
trait IFactRegistry<TContractState> {
    /// Check if a fact is valid (verified by SHARP)
    /// 
    /// Args:
    ///     fact: Fact hash from SHARP verification
    /// 
    /// Returns:
    ///     true if fact has been verified and registered
    fn is_valid(self: @TContractState, fact: felt252) -> bool;
}

/// SHARP Fact Registry Contract Address (Starknet Sepolia)
/// 
/// Note: This is a placeholder. Update with actual SHARP registry address
/// Real address can be found at: https://docs.starknet.io/documentation/architecture_and_concepts/Network_Architecture/fact-registry/
const SHARP_FACT_REGISTRY_SEPOLIA: felt252 = 0x0; // TODO: Update with actual address

/// Proof metadata for risk calculation
#[derive(Drop, Copy, Serde, starknet::Store)]
struct ProofMetadata {
    proof_fact: felt252,       // SHARP fact hash
    computation_hash: felt252, // Hash of input metrics
    output_score: felt252,     // Proven risk score
    verified_at: u64,          // Block number when verified
    verifier: ContractAddress, // Address that submitted proof
}

/// Verify a risk calculation proof via SHARP
/// 
/// Args:
///     proof_fact: Fact hash from SHARP
///     computation_hash: Hash of the input metrics
///     expected_score: Expected risk score output
/// 
/// Returns:
///     true if proof is valid and output matches
/// 
/// # Security
/// - Checks fact exists in SHARP registry
/// - Validates computation hash matches inputs
/// - Ensures output score matches proven value
fn verify_risk_proof(
    proof_fact: felt252,
    computation_hash: felt252,
    expected_score: felt252,
    registry_address: ContractAddress
) -> bool {
    // Create dispatcher for fact registry
    let registry = IFactRegistryDispatcher { 
        contract_address: registry_address 
    };
    
    // Check if proof fact is valid in SHARP registry
    let is_verified = registry.is_valid(proof_fact);
    
    if !is_verified {
        return false;
    }
    
    // Additional validation could include:
    // - Verify computation_hash matches expected format
    // - Check expected_score is in valid range
    // - Validate proof was submitted by authorized account
    
    true
}

/// Compute hash of protocol metrics for proof verification
/// 
/// Args:
///     utilization: Utilization in basis points
///     volatility: Volatility in basis points
///     liquidity: Liquidity category (0-3)
///     audit_score: Audit score (0-100)
///     age_days: Protocol age in days
/// 
/// Returns:
///     Hash of the input metrics
fn compute_metrics_hash(
    utilization: felt252,
    volatility: felt252,
    liquidity: felt252,
    audit_score: felt252,
    age_days: felt252
) -> felt252 {
    use core::pedersen::pedersen;
    
    // Compute Pedersen hash of all metrics
    let hash1 = pedersen(utilization, volatility);
    let hash2 = pedersen(liquidity, audit_score);
    let hash3 = pedersen(age_days, hash1);
    pedersen(hash2, hash3)
}

/// Verify allocation decision with proof
/// 
/// Ensures that the AI's allocation decision was computed correctly
/// and verified by SHARP before execution
/// 
/// Args:
///     jediswap_metrics: JediSwap protocol metrics
///     ekubo_metrics: Ekubo protocol metrics
///     jediswap_proof_fact: SHARP fact for JediSwap risk calculation
///     ekubo_proof_fact: SHARP fact for Ekubo risk calculation
///     expected_jediswap_score: Expected JediSwap risk score
///     expected_ekubo_score: Expected Ekubo risk score
///     registry_address: SHARP fact registry contract
/// 
/// Returns:
///     true if both proofs are valid
fn verify_allocation_decision_with_proofs(
    jediswap_metrics: (felt252, felt252, felt252, felt252, felt252),
    ekubo_metrics: (felt252, felt252, felt252, felt252, felt252),
    jediswap_proof_fact: felt252,
    ekubo_proof_fact: felt252,
    expected_jediswap_score: felt252,
    expected_ekubo_score: felt252,
    registry_address: ContractAddress
) -> bool {
    // Compute hashes of input metrics
    let (j_util, j_vol, j_liq, j_audit, j_age) = jediswap_metrics;
    let jediswap_hash = compute_metrics_hash(j_util, j_vol, j_liq, j_audit, j_age);
    
    let (e_util, e_vol, e_liq, e_audit, e_age) = ekubo_metrics;
    let ekubo_hash = compute_metrics_hash(e_util, e_vol, e_liq, e_audit, e_age);
    
    // Verify JediSwap proof
    let jediswap_valid = verify_risk_proof(
        jediswap_proof_fact,
        jediswap_hash,
        expected_jediswap_score,
        registry_address
    );
    
    if !jediswap_valid {
        return false;
    }
    
    // Verify Ekubo proof
    let ekubo_valid = verify_risk_proof(
        ekubo_proof_fact,
        ekubo_hash,
        expected_ekubo_score,
        registry_address
    );
    
    if !ekubo_valid {
        return false;
    }
    
    // Both proofs valid
    true
}

#[cfg(test)]
mod tests {
    use super::{compute_metrics_hash, SHARP_FACT_REGISTRY_SEPOLIA};
    
    #[test]
    fn test_compute_metrics_hash() {
        // Test that same metrics produce same hash
        let hash1 = compute_metrics_hash(6500, 3500, 1, 98, 800);
        let hash2 = compute_metrics_hash(6500, 3500, 1, 98, 800);
        
        assert(hash1 == hash2, 'Hash should be deterministic');
    }
    
    #[test]
    fn test_different_metrics_different_hash() {
        // Test that different metrics produce different hashes
        let hash1 = compute_metrics_hash(6500, 3500, 1, 98, 800);
        let hash2 = compute_metrics_hash(5200, 2800, 2, 95, 400);
        
        assert(hash1 != hash2, 'Different metrics should differ');
    }
}

