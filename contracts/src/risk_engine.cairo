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
        // Find maximum allocation using u256 comparisons
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
        
        // Verify minimum diversification (use u256 comparison)
        let min_div_u256: u256 = min_diversification.into();
        let count_u256: u256 = diversification_count.into();
        if count_u256 < min_div_u256 {
            return false;
        };
        
        true
    }
}
