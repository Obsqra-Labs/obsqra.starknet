#[starknet::interface]
trait IRiskEngine<TContractState> {
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
    
    #[storage]
    struct Storage {
        owner: ContractAddress,
    }
    
    #[constructor]
    fn constructor(ref self: ContractState, owner: ContractAddress) {
        self.owner.write(owner);
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
        let utilization_risk = utilization * 25 / 10000;
        
        // Volatility risk: volatility * 40 / 10000
        let volatility_risk = volatility * 40 / 10000;
        
        // Liquidity risk: categorical mapping
        let liquidity_risk = if liquidity == 0 {
            0
        } else if liquidity == 1 {
            5
        } else if liquidity == 2 {
            15
        } else {
            30
        };
        
        // Audit risk: (100 - audit_score) * 0.3
        let audit_risk = (100 - audit_score) * 3 / 10;
        
        // Age risk: max(0, (730 - age_days) * 10 / 730)
        let age_risk = if age_days >= 730 {
            0
        } else {
            (730 - age_days) * 10 / 730
        };
        
        // Total score
        let total = utilization_risk + volatility_risk + liquidity_risk + audit_risk + age_risk;
        
        // Clip to 5-95 range
        if total < 5 {
            return 5;
        };
        if total > 95 {
            return 95;
        };
        return total;
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
        // Risk-adjusted score = APY / (Risk + 1)
        let aave_score = aave_apy / (aave_risk + 1);
        let lido_score = lido_apy / (lido_risk + 1);
        let compound_score = compound_apy / (compound_risk + 1);
        
        let total_score = aave_score + lido_score + compound_score;
        
        // Calculate percentages (basis points, 10000 = 100%)
        let aave_pct = (aave_score * 10000) / total_score;
        let lido_pct = (lido_score * 10000) / total_score;
        let compound_pct = 10000 - aave_pct - lido_pct;
        
        return (aave_pct, lido_pct, compound_pct);
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
        // Check max single protocol
        let max_alloc = if aave_pct > lido_pct {
            if aave_pct > compound_pct {
                aave_pct
            } else {
                compound_pct
            }
        } else {
            if lido_pct > compound_pct {
                lido_pct
            } else {
                compound_pct
            }
        };
        
        if max_alloc > max_single {
            return false;
        };
        
        // Check diversification (count protocols with >10%)
        let diversification_count = 0;
        if aave_pct >= 1000 {
            diversification_count += 1;
        };
        if lido_pct >= 1000 {
            diversification_count += 1;
        };
        if compound_pct >= 1000 {
            diversification_count += 1;
        };
        
        if diversification_count < min_diversification {
            return false;
        };
        
        return true;
    }
}

