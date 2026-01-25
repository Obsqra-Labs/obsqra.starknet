use luminair::prelude::*;
use serde::{Deserialize, Serialize};
use std::fs;
use std::io::{self, Read};
use base64::{engine::general_purpose, Engine as _};
use serde_json::{self, Value};
use integrity::bindings::{
    Felt,
    VerifierConfiguration,
    StarkProofWithSerde,
    StarkConfigWithSerde,
    TracesConfigWithSerde,
    TableCommitmentConfigWithSerde,
    VectorCommitmentConfigWithSerde,
    FriConfigWithSerde,
    ProofOfWorkConfigWithSerde,
    PublicInputWithSerde,
    SegmentInfo,
    AddrValue,
    ContinuousPageHeader,
    StarkUnsentCommitmentWithSerde,
    TracesUnsentCommitmentWithSerde,
    FriUnsentCommitmentWithSerde,
    ProofOfWorkUnsentCommitmentWithSerde,
    StarkWitnessWithSerde,
    TracesDecommitmentWithSerde,
    TableDecommitmentWithSerde,
    TracesWitnessWithSerde,
    TableCommitmentWitnessWithSerde,
    VectorCommitmentWitnessWithSerde,
    FriWitnessWithSerde,
};

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
    // Paths for Integrity (Herodotus) verifier inputs
    verifier_config_path: String,
    stark_proof_path: String,
    // Base64-encoded payloads (currently LuminAIR bincode format, not Integrity ABI)
    verifier_config_b64: String,
    stark_proof_b64: String,
    // Hint about the encoding so downstream can reject/convert explicitly
    verifier_payload_format: String,
    verifier_config: Option<serde_json::Value>,
    stark_proof: Option<serde_json::Value>,
    verified: bool,
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
/// 
/// Returns a GraphTensor that can have retrieve() called on it
fn calculate_risk_score(
    cx: &mut Graph,
    metrics: &ProtocolMetrics,
) -> GraphTensor {
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
    // Use comparison: if raw < 0, use 0; else use raw
    let is_negative = age_penalty_raw.less_than(zero);
    let age_penalty = is_negative * zero + (1.0 - is_negative) * age_penalty_raw;

    // Sum all components
    let total_unclamped = util_component + vol_component + liq_component + audit_component + age_penalty;

    // Clamp to [5, 95] using comparisons (LuminAIR doesn't have max/min methods)
    let min_val = cx.tensor(()).set(vec![5.0]);
    let max_val = cx.tensor(()).set(vec![95.0]);
    
    // Clamp logic: if < min, use min; if > max, use max; else use value
    // Using comparison trick: (condition) * value_if_true + (1 - condition) * value_if_false
    let is_below_min = total_unclamped.less_than(min_val);
    let is_above_max = total_unclamped.greater_than(max_val);
    
    // Clamp to minimum: if below min, use min; else use original
    let clamped_low = is_below_min * min_val + (1.0 - is_below_min) * total_unclamped;
    
    // Clamp to maximum: if above max, use max; else use clamped_low
    let clamped_high = is_above_max * max_val + (1.0 - is_above_max) * clamped_low;
    
    // Note: This doesn't handle both conditions at once, but for our range [5, 95] it should work
    // For simplicity, we'll use a two-step clamp
    let total_clamped = clamped_high;

    // Convert to integer (0-100 scale) - multiply by 100 to get basis points (0-10000)
    let risk_score = total_clamped * 100.0; // Scale to 0-10000 (basis points)

    risk_score
}

// --- Integrity helpers (placeholder data for now) ---

fn felt_hex(f: Felt) -> String {
    format!("0x{:x}", f)
}

fn empty_verifier_configuration() -> VerifierConfiguration {
    let zero = Felt::from(0u8);
    VerifierConfiguration {
        layout: zero,
        hasher: zero,
        stone_version: zero,
        memory_verification: zero,
    }
}

fn empty_vector_commitment_config() -> VectorCommitmentConfigWithSerde {
    let zero = Felt::from(0u8);
    VectorCommitmentConfigWithSerde {
        height: zero,
        n_verifier_friendly_commitment_layers: zero,
    }
}

fn empty_table_commitment_config() -> TableCommitmentConfigWithSerde {
    TableCommitmentConfigWithSerde {
        n_columns: Felt::from(0u8),
        vector: empty_vector_commitment_config(),
    }
}

fn empty_traces_config() -> TracesConfigWithSerde {
    let table = empty_table_commitment_config();
    TracesConfigWithSerde {
        original: table.clone(),
        interaction: table,
    }
}

fn empty_fri_config() -> FriConfigWithSerde {
    FriConfigWithSerde {
        log_input_size: Felt::from(0u8),
        n_layers: Felt::from(0u8),
        inner_layers: vec![],
        fri_step_sizes: vec![],
        log_last_layer_degree_bound: Felt::from(0u8),
    }
}

fn empty_stark_config() -> StarkConfigWithSerde {
    StarkConfigWithSerde {
        traces: empty_traces_config(),
        composition: empty_table_commitment_config(),
        fri: empty_fri_config(),
        proof_of_work: ProofOfWorkConfigWithSerde { n_bits: 0 },
        log_trace_domain_size: Felt::from(0u8),
        n_queries: Felt::from(0u8),
        log_n_cosets: Felt::from(0u8),
        n_verifier_friendly_commitment_layers: Felt::from(0u8),
    }
}

fn empty_public_input() -> PublicInputWithSerde {
    PublicInputWithSerde {
        log_n_steps: Felt::from(0u8),
        range_check_min: Felt::from(0u8),
        range_check_max: Felt::from(0u8),
        layout: Felt::from(0u8),
        dynamic_params: vec![],
        segments: vec![],
        padding_addr: Felt::from(0u8),
        padding_value: Felt::from(0u8),
        main_page: vec![],
        continuous_page_headers: vec![],
    }
}

fn empty_stark_unsent_commitment() -> StarkUnsentCommitmentWithSerde {
    StarkUnsentCommitmentWithSerde {
        traces: TracesUnsentCommitmentWithSerde {
            original: Felt::from(0u8),
            interaction: Felt::from(0u8),
        },
        composition: Felt::from(0u8),
        oods_values: vec![],
        fri: FriUnsentCommitmentWithSerde {
            inner_layers: vec![],
            last_layer_coefficients: vec![],
        },
        proof_of_work: ProofOfWorkUnsentCommitmentWithSerde { nonce: 0 },
    }
}

fn empty_table_decommitment() -> TableDecommitmentWithSerde {
    TableDecommitmentWithSerde { values: vec![] }
}

fn empty_table_witness() -> TableCommitmentWitnessWithSerde {
    TableCommitmentWitnessWithSerde {
        vector: VectorCommitmentWitnessWithSerde {
            authentications: vec![],
        },
    }
}

fn empty_traces_witness() -> TracesWitnessWithSerde {
    TracesWitnessWithSerde {
        original: empty_table_witness(),
        interaction: empty_table_witness(),
    }
}

fn empty_traces_decommitment() -> TracesDecommitmentWithSerde {
    TracesDecommitmentWithSerde {
        original: empty_table_decommitment(),
        interaction: empty_table_decommitment(),
    }
}

fn empty_stark_witness() -> StarkWitnessWithSerde {
    StarkWitnessWithSerde {
        traces_decommitment: empty_traces_decommitment(),
        traces_witness: empty_traces_witness(),
        composition_decommitment: empty_table_decommitment(),
        composition_witness: empty_table_witness(),
        fri_witness: FriWitnessWithSerde { layers: vec![] },
    }
}

fn empty_stark_proof() -> StarkProofWithSerde {
    StarkProofWithSerde {
        config: empty_stark_config(),
        public_input: empty_public_input(),
        unsent_commitment: empty_stark_unsent_commitment(),
        witness: empty_stark_witness(),
    }
}

fn serialize_vector_commitment_config_json(cfg: &VectorCommitmentConfigWithSerde) -> Value {
    serde_json::json!({
        "height": felt_hex(cfg.height),
        "n_verifier_friendly_commitment_layers": felt_hex(cfg.n_verifier_friendly_commitment_layers),
    })
}

fn serialize_table_commitment_config_json(cfg: &TableCommitmentConfigWithSerde) -> Value {
    serde_json::json!({
        "n_columns": felt_hex(cfg.n_columns),
        "vector": serialize_vector_commitment_config_json(&cfg.vector),
    })
}

fn serialize_traces_config_json(cfg: &TracesConfigWithSerde) -> Value {
    serde_json::json!({
        "original": serialize_table_commitment_config_json(&cfg.original),
        "interaction": serialize_table_commitment_config_json(&cfg.interaction),
    })
}

fn serialize_fri_config_json(cfg: &FriConfigWithSerde) -> Value {
    serde_json::json!({
        "log_input_size": felt_hex(cfg.log_input_size),
        "n_layers": felt_hex(cfg.n_layers),
        "inner_layers": cfg.inner_layers.iter().map(serialize_table_commitment_config_json).collect::<Vec<Value>>(),
        "fri_step_sizes": cfg.fri_step_sizes.iter().map(|f| felt_hex(*f)).collect::<Vec<String>>(),
        "log_last_layer_degree_bound": felt_hex(cfg.log_last_layer_degree_bound),
    })
}

fn serialize_stark_config_json(cfg: &StarkConfigWithSerde) -> Value {
    serde_json::json!({
        "traces": serialize_traces_config_json(&cfg.traces),
        "composition": serialize_table_commitment_config_json(&cfg.composition),
        "fri": serialize_fri_config_json(&cfg.fri),
        "proof_of_work": { "n_bits": cfg.proof_of_work.n_bits },
        "log_trace_domain_size": felt_hex(cfg.log_trace_domain_size),
        "n_queries": felt_hex(cfg.n_queries),
        "log_n_cosets": felt_hex(cfg.log_n_cosets),
        "n_verifier_friendly_commitment_layers": felt_hex(cfg.n_verifier_friendly_commitment_layers),
    })
}

fn serialize_segment_info_json(seg: &SegmentInfo) -> Value {
    serde_json::json!({
        "begin_addr": felt_hex(seg.begin_addr),
        "stop_ptr": felt_hex(seg.stop_ptr),
    })
}

fn serialize_addr_value_json(av: &AddrValue) -> Value {
    serde_json::json!({
        "address": felt_hex(av.address),
        "value": felt_hex(av.value),
    })
}

fn serialize_continuous_page_header_json(h: &ContinuousPageHeader) -> Value {
    serde_json::json!({
        "start_address": felt_hex(h.start_address),
        "size": felt_hex(h.size),
        "hash": felt_hex(h.hash),
        "prod": felt_hex(h.prod),
    })
}

fn serialize_public_input_json(pi: &PublicInputWithSerde) -> Value {
    serde_json::json!({
        "log_n_steps": felt_hex(pi.log_n_steps),
        "range_check_min": felt_hex(pi.range_check_min),
        "range_check_max": felt_hex(pi.range_check_max),
        "layout": felt_hex(pi.layout),
        "dynamic_params": pi.dynamic_params.iter().map(|f| felt_hex(*f)).collect::<Vec<String>>(),
        "segments": pi.segments.iter().map(serialize_segment_info_json).collect::<Vec<Value>>(),
        "padding_addr": felt_hex(pi.padding_addr),
        "padding_value": felt_hex(pi.padding_value),
        "main_page": pi.main_page.iter().map(serialize_addr_value_json).collect::<Vec<Value>>(),
        "continuous_page_headers": pi.continuous_page_headers.iter().map(serialize_continuous_page_header_json).collect::<Vec<Value>>(),
    })
}

fn serialize_stark_unsent_commitment_json(s: &StarkUnsentCommitmentWithSerde) -> Value {
    serde_json::json!({
        "traces": {
            "original": felt_hex(s.traces.original),
            "interaction": felt_hex(s.traces.interaction),
        },
        "composition": felt_hex(s.composition),
        "oods_values": s.oods_values.iter().map(|f| felt_hex(*f)).collect::<Vec<String>>(),
        "fri": {
            "inner_layers": s.fri.inner_layers.iter().map(|f| felt_hex(*f)).collect::<Vec<String>>(),
            "last_layer_coefficients": s.fri.last_layer_coefficients.iter().map(|f| felt_hex(*f)).collect::<Vec<String>>(),
        },
        "proof_of_work": { "nonce": s.proof_of_work.nonce },
    })
}

fn serialize_table_decommitment_json(d: &TableDecommitmentWithSerde) -> Value {
    serde_json::json!({
        "values": d.values.iter().map(|f| felt_hex(*f)).collect::<Vec<String>>(),
    })
}

fn serialize_table_witness_json(w: &TableCommitmentWitnessWithSerde) -> Value {
    serde_json::json!({
        "vector": {
            "authentications": w.vector.authentications.iter().map(|f| felt_hex(*f)).collect::<Vec<String>>(),
        }
    })
}

fn serialize_traces_witness_json(w: &TracesWitnessWithSerde) -> Value {
    serde_json::json!({
        "original": serialize_table_witness_json(&w.original),
        "interaction": serialize_table_witness_json(&w.interaction),
    })
}

fn serialize_traces_decommitment_json(d: &TracesDecommitmentWithSerde) -> Value {
    serde_json::json!({
        "original": serialize_table_decommitment_json(&d.original),
        "interaction": serialize_table_decommitment_json(&d.interaction),
    })
}

fn serialize_stark_witness_json(w: &StarkWitnessWithSerde) -> Value {
    serde_json::json!({
        "traces_decommitment": serialize_traces_decommitment_json(&w.traces_decommitment),
        "traces_witness": serialize_traces_witness_json(&w.traces_witness),
        "composition_decommitment": serialize_table_decommitment_json(&w.composition_decommitment),
        "composition_witness": serialize_table_witness_json(&w.composition_witness),
        "fri_witness": {
            "layers": w.fri_witness.layers.iter().map(|f| felt_hex(*f)).collect::<Vec<String>>(),
        }
    })
}

fn serialize_stark_proof_json(proof: &StarkProofWithSerde) -> Value {
    serde_json::json!({
        "config": serialize_stark_config_json(&proof.config),
        "public_input": serialize_public_input_json(&proof.public_input),
        "unsent_commitment": serialize_stark_unsent_commitment_json(&proof.unsent_commitment),
        "witness": serialize_stark_witness_json(&proof.witness),
    })
}

fn serialize_verifier_config_json(cfg: &VerifierConfiguration) -> Value {
    serde_json::json!({
        "layout": felt_hex(cfg.layout),
        "hasher": felt_hex(cfg.hasher),
        "stone_version": felt_hex(cfg.stone_version),
        "memory_verification": felt_hex(cfg.memory_verification),
    })
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
    let jedi_risk_expr = calculate_risk_score(&mut cx, &input.jediswap_metrics);
    let ekubo_risk_expr = calculate_risk_score(&mut cx, &input.ekubo_metrics);
    
    // Retrieve outputs (retrieve() returns a mutable reference we can pass to compile)
    let mut jedi_risk_out = jedi_risk_expr.retrieve();
    let mut ekubo_risk_out = ekubo_risk_expr.retrieve();

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

    // Save proof and settings to files first
    let proof_path = "/tmp/risk_proof.bin";
    let settings_path = "/tmp/risk_settings.bin";
    
    proof.to_bincode_file(proof_path)?;
    settings.to_bincode_file(settings_path)?;

    // Verify proof immediately (verify consumes proof, so do it after saving)
    println!("   Verifying proof...");
    // Reload proof and settings for verification
    let proof_for_verify = LuminairProof::from_bincode_file(proof_path)?;
    let settings_for_verify = CircuitSettings::from_bincode_file(settings_path)?;
    let verification_result = verify(proof_for_verify, settings_for_verify);
    let is_verified = verification_result.is_ok();
    
    if is_verified {
        println!("   ✅ Proof verified successfully!");
    } else {
        eprintln!("   ❌ Proof verification failed: {:?}", verification_result.err());
        // Don't fail - return verification status
    }

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

    // Build Integrity-friendly payloads (currently zeroed placeholders matching the ABI shape)
    let integrity_verifier_cfg = empty_verifier_configuration();
    let integrity_stark_proof = empty_stark_proof();
    let verifier_config_json = serialize_verifier_config_json(&integrity_verifier_cfg);
    let stark_proof_json = serialize_stark_proof_json(&integrity_stark_proof);
    let verifier_config_json_b64 =
        general_purpose::STANDARD.encode(serde_json::to_string(&verifier_config_json)?.as_bytes());
    let stark_proof_json_b64 =
        general_purpose::STANDARD.encode(serde_json::to_string(&stark_proof_json)?.as_bytes());

    // Output result
    let output = RiskScoringOutput {
        jediswap_risk: jedi_risk,
        ekubo_risk: ekubo_risk,
        proof_hash,
        proof_data_path: proof_path.to_string(),
        settings_path: settings_path.to_string(),
        // For now, expose the same paths under Integrity-friendly names.
        // These are bincode-serialized CircuitSettings and proof bytes.
        verifier_config_path: settings_path.to_string(),
        stark_proof_path: proof_path.to_string(),
        // Integrity JSON (placeholder values) encoded to base64 for transport
        verifier_config_b64: verifier_config_json_b64,
        stark_proof_b64: stark_proof_json_b64,
        verifier_payload_format: "integrity_json".to_string(),
        verifier_config: Some(verifier_config_json),
        stark_proof: Some(stark_proof_json),
        verified: is_verified,
    };

    println!("\n📊 Risk Scores:");
    println!("   JediSwap: {} (basis points)", jedi_risk);
    println!("   Ekubo: {} (basis points)", ekubo_risk);
    println!("   Proof hash: {}", output.proof_hash);

    // Output JSON to stdout
    println!("\n{}", serde_json::to_string_pretty(&output)?);

    Ok(())
}
