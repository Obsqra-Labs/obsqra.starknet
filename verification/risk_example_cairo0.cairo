%builtins output pedersen range_check bitwise

from starkware.cairo.common.math import unsigned_div_rem
from starkware.cairo.common.math_cmp import is_le

func div_floor{range_check_ptr}(numerator: felt, denominator: felt) -> (res: felt) {
    let (q, _) = unsigned_div_rem(numerator, denominator);
    return (res=q);
}

func calculate_risk_score{range_check_ptr}(
    utilization: felt,
    volatility: felt,
    liquidity: felt,
    audit_score: felt,
    age_days: felt,
) -> (risk: felt) {
    alloc_locals;

    // utilization_risk = utilization * 25 / 10000
    let util_prod = utilization * 25;
    let (util_risk) = div_floor(util_prod, 10000);

    // volatility_risk = volatility * 40 / 10000
    let vol_prod = volatility * 40;
    let (vol_risk) = div_floor(vol_prod, 10000);

    // liquidity_risk mapping
    local liquidity_risk;
    if (liquidity == 0) {
        assert liquidity_risk = 0;
    } else {
        if (liquidity == 1) {
            assert liquidity_risk = 5;
        } else {
            if (liquidity == 2) {
                assert liquidity_risk = 15;
            } else {
                assert liquidity_risk = 30;
            }
        }
    }

    // audit_risk = (100 - audit_score) * 3 / 10
    let audit_diff = 100 - audit_score;
    let audit_prod = audit_diff * 3;
    let (audit_risk) = div_floor(audit_prod, 10);

    // age_risk = max(0, (730 - age_days) * 10 / 730)
    let age_is_le = is_le(age_days, 729);
    local range_check_ptr = range_check_ptr;
    let age_capped = age_is_le * age_days + (1 - age_is_le) * 730;
    let diff = 730 - age_capped;
    let prod = diff * 10;
    let (age_risk) = div_floor(prod, 730);

    let total = util_risk + vol_risk + liquidity_risk + audit_risk + age_risk;

    local total_is_lt_5 = is_le(total, 4);
    local range_check_ptr = range_check_ptr;
    if (total_is_lt_5 == 1) {
        return (risk=5);
    }
    local total_ge_96 = is_le(96, total);
    local range_check_ptr = range_check_ptr;
    if (total_ge_96 == 1) {
        return (risk=95);
    }
    return (risk=total);
}

func main{
    output_ptr: felt*,
    pedersen_ptr: felt*,
    range_check_ptr: felt,
    bitwise_ptr: felt*,
}() {
    alloc_locals;

    local jedi_utilization;
    local jedi_volatility;
    local jedi_liquidity;
    local jedi_audit_score;
    local jedi_age_days;
    local ekubo_utilization;
    local ekubo_volatility;
    local ekubo_liquidity;
    local ekubo_audit_score;
    local ekubo_age_days;

    %{
        ids.jedi_utilization = program_input['jedi_utilization']
        ids.jedi_volatility = program_input['jedi_volatility']
        ids.jedi_liquidity = program_input['jedi_liquidity']
        ids.jedi_audit_score = program_input['jedi_audit_score']
        ids.jedi_age_days = program_input['jedi_age_days']
        ids.ekubo_utilization = program_input['ekubo_utilization']
        ids.ekubo_volatility = program_input['ekubo_volatility']
        ids.ekubo_liquidity = program_input['ekubo_liquidity']
        ids.ekubo_audit_score = program_input['ekubo_audit_score']
        ids.ekubo_age_days = program_input['ekubo_age_days']
    %}

    let (jedi_risk) = calculate_risk_score(
        utilization=jedi_utilization,
        volatility=jedi_volatility,
        liquidity=jedi_liquidity,
        audit_score=jedi_audit_score,
        age_days=jedi_age_days,
    );
    let (ekubo_risk) = calculate_risk_score(
        utilization=ekubo_utilization,
        volatility=ekubo_volatility,
        liquidity=ekubo_liquidity,
        audit_score=ekubo_audit_score,
        age_days=ekubo_age_days,
    );

    assert output_ptr[0] = jedi_risk;
    assert output_ptr[1] = ekubo_risk;
    let output_ptr = output_ptr + 2;

    return ();
}
