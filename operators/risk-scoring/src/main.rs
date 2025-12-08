use luminair::prelude::*;
use serde::{Deserialize, Serialize};
use std::fs;
use std::io::{self, Read};

/// Protocol metrics input (matching our Python/Cairo model)
#[derive(Debug, Deserialize, Serialize)]
struct ProtocolMetrics {
    utilization: u32,    // Basis points (0-10000)
    volatility: u32,      // Basis points (0-10000)
    liquidity: u32,      // 1-3 scale
    audit_score: u32,    // 0-100
    age_days: u32,       // Days since launch
}

/// Input for risk scoring operator
#[derive(Debug, Deserialize)]
struct RiskScoringInput {
    jediswap_metrics: ProtocolMetrics,
    ekubo_metrics: ProtocolMetrics,
}

/// Output from risk scoring operator
#[derive(Debug, Serialize)]
struct RiskScoringOutput {
    jediswap_risk: u32,
    ekubo_risk: u32,
    proof_hash: String,
    proof_data_path: String,
    settings_path: String,
}

/// Calculate risk score using LuminAIR ZK circuit
/// 
/// Risk formula (matching Cairo/Python):
/// - util_component = (utilization / 10000) * 35
/// - vol_component = (volatility / 10000) * 30
/// - liq_component = (3 - liquidity) * 5
/// - audit_component = (100 - audit_score) / 5
/// - age_penalty = max(0, 10 - age_days / 100)
/// - total = clamp(sum, 5, 95)
fn calculate_risk_score(
    cx: &mut Graph,
    metrics: &ProtocolMetrics,
) -> (Tensor, Tensor) {
    // Convert inputs to f32 for computation
    let util = metrics.utilization as f32 / 10000.0;
    let vol = metrics.volatility as f32 / 10000.0;
    let liq = metrics.liquidity as f32;
    let audit = metrics.audit_score as f32;
    let age = metrics.age_days as f32;

    // Create tensors for components
    let util_t = cx.tensor(()).set(vec![util]);
    let vol_t = cx.tensor(()).set(vec![vol]);
    let liq_t = cx.tensor(()).set(vec![liq]);
    let audit_t = cx.tensor(()).set(vec![audit]);
    let age_t = cx.tensor(()).set(vec![age]);

    // Calculate components
    // util_component = (utilization / 10000) * 35
    let util_component = util_t * 35.0;

    // vol_component = (volatility / 10000) * 30
    let vol_component = vol_t * 30.0;

    // liq_component = (3 - liquidity) * 5
    let liq_component = (3.0 - liq_t) * 5.0;

    // audit_component = (100 - audit_score) / 5
    let audit_component = (100.0 - audit_t) / 5.0;

    // age_penalty = max(0, 10 - age_days / 100)
    let age_penalty_raw = 10.0 - (age_t / 100.0);
    let zero = cx.tensor(()).set(vec![0.0]);
    let age_penalty = age_penalty_raw.maximum(zero);

    // Sum all components
    let total_unclamped = util_component + vol_component + liq_component + audit_component + age_penalty;

    // Clamp to [5, 95]
    let min_val = cx.tensor(()).set(vec![5.0]);
    let max_val = cx.tensor(()).set(vec![95.0]);
    let total_clamped = total_unclamped.maximum(min_val).minimum(max_val);

    // Convert to integer (0-100 scale)
    let risk_score = total_clamped * 100.0; // Scale to 0-10000 (basis points)

    (risk_score, total_clamped)
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Parse command line arguments
    let args: Vec<String> = std::env::args().collect();
    
    let input_json = if args.len() > 1 {
        // Read from file
        fs::read_to_string(&args[1])?
    } else {
        // Read from stdin
        let mut buffer = String::new();
        io::stdin().read_to_string(&mut buffer)?;
        buffer
    };

    // Parse input
    let input: RiskScoringInput = serde_json::from_str(&input_json)?;

    println!("🔐 Generating STARK proof for risk scoring...");
    println!("   JediSwap: util={}, vol={}, liq={}, audit={}, age={}",
        input.jediswap_metrics.utilization,
        input.jediswap_metrics.volatility,
        input.jediswap_metrics.liquidity,
        input.jediswap_metrics.audit_score,
        input.jediswap_metrics.age_days
    );
    println!("   Ekubo: util={}, vol={}, liq={}, audit={}, age={}",
        input.ekubo_metrics.utilization,
        input.ekubo_metrics.volatility,
        input.ekubo_metrics.liquidity,
        input.ekubo_metrics.audit_score,
        input.ekubo_metrics.age_days
    );

    // Build computation graph
    let mut cx = Graph::new();

    // Calculate risk scores for both protocols
    let (jedi_risk_tensor, _) = calculate_risk_score(&mut cx, &input.jediswap_metrics);
    let (ekubo_risk_tensor, _) = calculate_risk_score(&mut cx, &input.ekubo_metrics);

    // Retrieve outputs
    let mut jedi_risk_out = jedi_risk_tensor.retrieve();
    let mut ekubo_risk_out = ekubo_risk_tensor.retrieve();

    // Compile the graph
    println!("   Compiling computation graph...");
    cx.compile(
        <(GenericCompiler, StwoCompiler)>::default(),
        &mut (&mut jedi_risk_out, &mut ekubo_risk_out),
    );

    // Generate circuit settings and trace
    println!("   Generating execution trace...");
    let mut settings = cx.gen_circuit_settings();
    let trace = cx.gen_trace(&mut settings)?;

    // Generate proof
    println!("   Proving computation...");
    let proof = prove(trace, settings.clone())?;
    println!("   ✅ Proof generated successfully!");

    // Save proof and settings to files
    let proof_path = "/tmp/risk_proof.bin";
    let settings_path = "/tmp/risk_settings.bin";
    
    proof.to_bincode_file(proof_path)?;
    settings.to_bincode_file(settings_path)?;

    // Calculate proof hash (SHA256 of proof data)
    use std::collections::hash_map::DefaultHasher;
    use std::hash::{Hash, Hasher};
    let proof_data = fs::read(proof_path)?;
    let mut hasher = DefaultHasher::new();
    proof_data.hash(&mut hasher);
    let proof_hash = format!("0x{:x}", hasher.finish());

    // Get risk scores (convert from f32 to u32)
    let jedi_risk = jedi_risk_out.data()[0] as u32;
    let ekubo_risk = ekubo_risk_out.data()[0] as u32;

    // Output result
    let output = RiskScoringOutput {
        jediswap_risk: jedi_risk,
        ekubo_risk: ekubo_risk,
        proof_hash,
        proof_data_path: proof_path.to_string(),
        settings_path: settings_path.to_string(),
    };

    println!("\n📊 Risk Scores:");
    println!("   JediSwap: {} (basis points)", jedi_risk);
    println!("   Ekubo: {} (basis points)", ekubo_risk);
    println!("   Proof hash: {}", output.proof_hash);

    // Output JSON to stdout
    println!("\n{}", serde_json::to_string_pretty(&output)?);

    Ok(())
}
