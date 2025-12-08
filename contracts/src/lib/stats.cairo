/// Fixed-Point Arithmetic Library for Cairo
/// 
/// Implements Q16.16 fixed-point math (16 bits integer, 16 bits fractional)
/// This provides sufficient precision for ML risk scoring while being efficient
/// 
/// Scale factor: 2^16 = 65536
/// Range: -32768.0 to 32767.99998 (signed) or 0 to 65535.99998 (unsigned)

use core::integer::{u64_safe_divmod, u64_as_non_zero};

/// Fixed-point scale: 2^16 = 65536
const SCALE: u64 = 65536;
const SCALE_FELT: felt252 = 65536;

/// Half scale for rounding: 2^15 = 32768
const HALF_SCALE: u64 = 32768;

/// Maximum safe integer value to prevent overflow
const MAX_SAFE_INT: u64 = 0x7FFFFFFF; // 2^31 - 1

/// Convert integer to fixed-point
/// 
/// # Arguments
/// * `value` - Integer value to convert
/// 
/// # Returns
/// Fixed-point representation (value * SCALE)
fn from_int(value: felt252) -> felt252 {
    value * SCALE_FELT
}

/// Convert fixed-point to integer (truncating fractional part)
/// 
/// # Arguments
/// * `fixed` - Fixed-point value
/// 
/// # Returns
/// Integer part of the fixed-point number
fn to_int(fixed: felt252) -> felt252 {
    fixed / SCALE_FELT
}

/// Multiply two fixed-point numbers
/// 
/// # Arguments
/// * `a` - First fixed-point number
/// * `b` - Second fixed-point number
/// 
/// # Returns
/// Product in fixed-point format
/// 
/// # Formula
/// (a * b) / SCALE
fn mul_fp(a: felt252, b: felt252) -> felt252 {
    (a * b) / SCALE_FELT
}

/// Divide two fixed-point numbers
/// 
/// # Arguments
/// * `a` - Numerator (fixed-point)
/// * `b` - Denominator (fixed-point)
/// 
/// # Returns
/// Quotient in fixed-point format
/// 
/// # Formula
/// (a * SCALE) / b
fn div_fp(a: felt252, b: felt252) -> felt252 {
    assert(b != 0, 'Division by zero');
    (a * SCALE_FELT) / b
}

/// Add two fixed-point numbers
/// 
/// # Arguments
/// * `a` - First fixed-point number
/// * `b` - Second fixed-point number
/// 
/// # Returns
/// Sum in fixed-point format
#[inline(always)]
fn add_fp(a: felt252, b: felt252) -> felt252 {
    a + b
}

/// Subtract two fixed-point numbers
/// 
/// # Arguments
/// * `a` - First fixed-point number
/// * `b` - Second fixed-point number
/// 
/// # Returns
/// Difference in fixed-point format
#[inline(always)]
fn sub_fp(a: felt252, b: felt252) -> felt252 {
    a - b
}

/// Multiply integer by fixed-point number
/// 
/// # Arguments
/// * `integer` - Regular integer
/// * `fixed` - Fixed-point number
/// 
/// # Returns
/// Product in fixed-point format
fn mul_int_fp(integer: felt252, fixed: felt252) -> felt252 {
    integer * fixed
}

/// Divide fixed-point by integer
/// 
/// # Arguments
/// * `fixed` - Fixed-point number
/// * `integer` - Regular integer divisor
/// 
/// # Returns
/// Quotient in fixed-point format
fn div_fp_int(fixed: felt252, integer: felt252) -> felt252 {
    assert(integer != 0, 'Division by zero');
    fixed / integer
}

/// Convert from basis points (10000 = 100%) to fixed-point (1.0)
/// 
/// # Arguments
/// * `basis_points` - Value in basis points (e.g., 6500 for 65%)
/// 
/// # Returns
/// Fixed-point representation
/// 
/// # Example
/// 6500 basis points = 0.65 = (6500 * SCALE) / 10000
fn from_basis_points(basis_points: felt252) -> felt252 {
    (basis_points * SCALE_FELT) / 10000
}

/// Convert fixed-point to basis points
/// 
/// # Arguments
/// * `fixed` - Fixed-point number
/// 
/// # Returns
/// Value in basis points
fn to_basis_points(fixed: felt252) -> felt252 {
    (fixed * 10000) / SCALE_FELT
}

/// Get minimum of two fixed-point numbers
/// 
/// # Arguments
/// * `a` - First number
/// * `b` - Second number
/// 
/// # Returns
/// Minimum value
fn min_fp(a: felt252, b: felt252) -> felt252 {
    if a < b {
        a
    } else {
        b
    }
}

/// Get maximum of two fixed-point numbers
/// 
/// # Arguments
/// * `a` - First number
/// * `b` - Second number
/// 
/// # Returns
/// Maximum value
fn max_fp(a: felt252, b: felt252) -> felt252 {
    if a > b {
        a
    } else {
        b
    }
}

/// Clamp fixed-point value between min and max
/// 
/// # Arguments
/// * `value` - Value to clamp
/// * `min_val` - Minimum allowed value
/// * `max_val` - Maximum allowed value
/// 
/// # Returns
/// Clamped value
fn clamp_fp(value: felt252, min_val: felt252, max_val: felt252) -> felt252 {
    max_fp(min_val, min_fp(value, max_val))
}

/// Convert percentage (0-100) to fixed-point (0.0-1.0)
/// 
/// # Arguments
/// * `percentage` - Percentage value (0-100)
/// 
/// # Returns
/// Fixed-point representation
fn from_percentage(percentage: felt252) -> felt252 {
    (percentage * SCALE_FELT) / 100
}

/// Convert fixed-point to percentage
/// 
/// # Arguments
/// * `fixed` - Fixed-point number
/// 
/// # Returns
/// Percentage value (0-100)
fn to_percentage(fixed: felt252) -> felt252 {
    (fixed * 100) / SCALE_FELT
}

/// Calculate weighted sum of two values
/// 
/// # Arguments
/// * `a` - First value (fixed-point)
/// * `weight_a` - Weight for first value (fixed-point, 0.0-1.0)
/// * `b` - Second value (fixed-point)
/// * `weight_b` - Weight for second value (fixed-point, 0.0-1.0)
/// 
/// # Returns
/// Weighted sum (a * weight_a + b * weight_b)
fn weighted_sum(a: felt252, weight_a: felt252, b: felt252, weight_b: felt252) -> felt252 {
    add_fp(mul_fp(a, weight_a), mul_fp(b, weight_b))
}

/// Linear interpolation between two values
/// 
/// # Arguments
/// * `a` - Start value
/// * `b` - End value
/// * `t` - Interpolation factor (0.0-1.0 in fixed-point)
/// 
/// # Returns
/// Interpolated value: a + (b - a) * t
fn lerp(a: felt252, b: felt252, t: felt252) -> felt252 {
    add_fp(a, mul_fp(sub_fp(b, a), t))
}

#[cfg(test)]
mod tests {
    use super::{from_int, to_int, mul_fp, div_fp, add_fp, sub_fp, SCALE_FELT};
    use super::{from_basis_points, to_basis_points, min_fp, max_fp, clamp_fp};

    #[test]
    fn test_from_int() {
        // 5 * 65536 = 327680
        assert(from_int(5) == 327680, 'from_int failed');
    }

    #[test]
    fn test_to_int() {
        // 327680 / 65536 = 5
        assert(to_int(327680) == 5, 'to_int failed');
    }

    #[test]
    fn test_mul_fp() {
        let a = from_int(3); // 3.0
        let b = from_int(4); // 4.0
        let result = mul_fp(a, b);
        assert(to_int(result) == 12, 'mul_fp failed');
    }

    #[test]
    fn test_div_fp() {
        let a = from_int(12); // 12.0
        let b = from_int(4);  // 4.0
        let result = div_fp(a, b);
        assert(to_int(result) == 3, 'div_fp failed');
    }

    #[test]
    fn test_add_fp() {
        let a = from_int(3); // 3.0
        let b = from_int(7); // 7.0
        let result = add_fp(a, b);
        assert(to_int(result) == 10, 'add_fp failed');
    }

    #[test]
    fn test_sub_fp() {
        let a = from_int(10); // 10.0
        let b = from_int(3);  // 3.0
        let result = sub_fp(a, b);
        assert(to_int(result) == 7, 'sub_fp failed');
    }

    #[test]
    fn test_basis_points() {
        // 6500 basis points = 65%
        let fp = from_basis_points(6500);
        let bp = to_basis_points(fp);
        assert(bp == 6500, 'basis points conversion failed');
    }

    #[test]
    fn test_min_max() {
        let a = from_int(5);
        let b = from_int(10);
        assert(to_int(min_fp(a, b)) == 5, 'min_fp failed');
        assert(to_int(max_fp(a, b)) == 10, 'max_fp failed');
    }

    #[test]
    fn test_clamp() {
        let value = from_int(15);
        let min_val = from_int(5);
        let max_val = from_int(10);
        let result = clamp_fp(value, min_val, max_val);
        assert(to_int(result) == 10, 'clamp_fp failed');
    }
}

