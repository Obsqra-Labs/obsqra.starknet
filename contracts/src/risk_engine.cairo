#[starknet::interface]
pub trait IRiskEngine<TContractState> {
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
        aave_risk: felt252,
        lido_risk: felt252,
        compound_risk: felt252,
        aave_apy: felt252,
        lido_apy: felt252,
        compound_apy: felt252
    ) -> (felt252, felt252, felt252);
    
    fn verify_constraints(
        ref self: TContractState,
        aave_pct: felt252,
        lido_pct: felt252,
        compound_pct: felt252,
        max_single: felt252,
        min_diversification: felt252
    ) -> bool;
}

#[starknet::contract]
mod RiskEngine {
    use starknet::ContractAddress;
    use starknet::storage::StoragePointerWriteAccess;
    use core::traits::Into;
    use core::traits::TryInto;
    use core::option::OptionTrait;
    use core::num::traits::DivRem;
    
    #[storage]
    struct Storage {
        owner: ContractAddress,
    }
    
    #[constructor]
    fn constructor(ref self: ContractState, owner: ContractAddress) {
        self.owner.write(owner);
    }
    
    // Helper: Convert u256 to felt252 (using low part, assuming values fit)
    fn u256_to_felt252(value: u256) -> felt252 {
        // For our use case, values are small enough that low part is sufficient
        // If high != 0, this would overflow, but our values are < 2^128
        value.low.try_into().unwrap()
    }
    
    // Helper: Division using u256
    fn felt252_div(lhs: felt252, rhs: felt252) -> felt252 {
        let lhs_u256: u256 = lhs.into();
        let rhs_u256: u256 = rhs.into();
        // Use DivRem trait - need NonZero for rhs
        // TryInto trait provides the conversion
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
        // Use u256 for comparison
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
        
        // Clip to 5-95 range using u256 comparison
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
        aave_risk: felt252,
        lido_risk: felt252,
        compound_risk: felt252,
        aave_apy: felt252,
        lido_apy: felt252,
        compound_apy: felt252
    ) -> (felt252, felt252, felt252) {
        // Risk-adjusted score = (APY * 10000) / (Risk + 1)
        let divisor_aave = aave_risk + 1;
        let divisor_lido = lido_risk + 1;
        let divisor_compound = compound_risk + 1;
        
        // Calculate scores with scaling
        let aave_product = aave_apy * 10000;
        let aave_score = felt252_div(aave_product, divisor_aave);
        
        let lido_product = lido_apy * 10000;
        let lido_score = felt252_div(lido_product, divisor_lido);
        
        let compound_product = compound_apy * 10000;
        let compound_score = felt252_div(compound_product, divisor_compound);
        
        let total_score = aave_score + lido_score + compound_score;
        
        // Calculate percentages (basis points, 10000 = 100%)
        let aave_pct_product = aave_score * 10000;
        let aave_pct = felt252_div(aave_pct_product, total_score);
        
        let lido_pct_product = lido_score * 10000;
        let lido_pct = felt252_div(lido_pct_product, total_score);
        
        let compound_pct = 10000 - aave_pct - lido_pct;
        
        (aave_pct, lido_pct, compound_pct)
    }
    
    #[external(v0)]
    fn verify_constraints(
        ref self: ContractState,
        aave_pct: felt252,
        lido_pct: felt252,
        compound_pct: felt252,
        max_single: felt252,
        min_diversification: felt252
    ) -> bool {
        // Find maximum allocation using u256 comparisons
        let aave_u256: u256 = aave_pct.into();
        let lido_u256: u256 = lido_pct.into();
        let compound_u256: u256 = compound_pct.into();
        
        let max_alloc = if aave_u256 > lido_u256 {
            if aave_u256 > compound_u256 { aave_pct } else { compound_pct }
        } else {
            if lido_u256 > compound_u256 { lido_pct } else { compound_pct }
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
        if aave_u256 >= threshold_u256 {
            diversification_count += 1;
        };
        if lido_u256 >= threshold_u256 {
            diversification_count += 1;
        };
        if compound_u256 >= threshold_u256 {
            diversification_count += 1;
        };
        
        // Verify minimum diversification (use u256 comparison)
        let min_div_u256: u256 = min_diversification.into();
        let count_u256: u256 = diversification_count.into();
        if count_u256 < min_div_u256 {
            return false;
        };
        
        true
    }
}
