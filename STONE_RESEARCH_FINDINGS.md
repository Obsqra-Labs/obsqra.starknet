STONE PROVER PIPELINE FEASIBILITY — RESEARCH FINDINGS

---

RESEARCH GAP #1: CAIRO TRACE SERIALIZATION FORMAT

Summary: cairo-run (the Cairo-VM runner used in proof mode) accepts public and private inputs via the --air_public_input and --air_private_input flags and writes the execution trace and memory to files when --proof_mode is set. Inputs must be serialized as felts. Composite types such as u256 (256-bit integers) are split into two 128-bit limbs (low/high), and a ContractAddress is a single felt. If the serialization is wrong, the program or proof generation tools will fail with explicit errors.

Findings:

Input method: The dev-log shows the command used to generate a proof-ready trace: cargo run verification/risk_example.cairo --layout=small|all_cairo --proof_mode --air_public_input ... --air_private_input ... --trace_file ... --memory_file ... --print_output. cairo-run reads values from the --air_public_input and --air_private_input flags rather than STDIN and produces trace/memory files when --proof_mode is enabled.

u256 serialization: Cairo defines u256 as a struct with low and high fields. When passing a 256-bit amount to cairo-run, the integer must be decomposed into two felts: {"low": <low_felt>, "high": <high_felt>}. Python libraries (e.g., starknet_py) offer helpers like to_uint256 for this purpose. An on-chain storage map in the unified strategy router uses Map<ContractAddress, u256>, implying the same two-felt representation.

ContractAddress serialization: ContractAddress is an alias for a felt252 value; it is passed as a single felt. For contract addresses and token addresses in Starknet, ensure the value fits within the field modulus.

Stdlib I/O modules: Cairo 2.11 introduces modules such as cairo::io::read()/write(), but the repository does not use them for proof mode. Proof generation relies on the command-line interface rather than STDIN.

Error handling: Wrong serialization manifests in different ways. The proof serializer rejected a Stone proof without annotations with "Unexpected number of interaction elements: 0". Passing an incorrectly generated proof to the verifier caused an invalid final_pc revert. These errors show that mismatches in format or AIR/layout cause explicit failures.

Sources:

- Dev-log showing the cairo-run invocation and proof generation flags.
- Proof loader converting verifier settings to felts.
- Dev-log describing serializer and verifier failures.

Gaps/Uncertainties:

- The repository does not include explicit examples of passing u256 or ContractAddress values to cairo-run. Without external documentation, the exact JSON syntax cannot be confirmed.
- The cairo::io module's behaviour in proof mode is not demonstrated.

Next Steps:

- Write a small Cairo program that accepts a u256 and run it with cairo-run to confirm the input syntax.
- Consult Cairo documentation or examples for the expected JSON format of --air_public_input/--air_private_input when using composite types.
- Add validation in the pipeline to catch serialization errors early and provide clear messages to users.

---

RESEARCH GAP #2: PROOF SIZE VS TRACE SIZE RELATIONSHIP

Summary: Proof size and latency increase with trace size. For the risk program, generating a proof with layout small (8,192 steps) produced a Stone proof of ~400 KB. Proofs for larger traces (e.g., all_cairo with 131,072 steps) are expected to be significantly larger (multiple megabytes) and take longer to generate. The growth is roughly sub-linear because STARKs compress data via FRI, but more steps still require more commitments and witness elements. The four-felt VerifierConfiguration adds negligible overhead to the calldata; most calldata comes from the StarkProofWithSerde witness.

Findings:

Small proof baseline: Tuning FRI parameters for the small layout (fri_step_list=[3,3,3,2], last_layer_degree_bound=64) allowed the prover to succeed and produced risk_small_proof.json (~400 KB).

Relationship to trace size: The FRI degree equation log2(last_layer_degree_bound) + Σ(fri_step_list) = log2(n_steps) + 4 links FRI parameters to the trace size. Doubling or quadrupling n_steps typically requires additional FRI layers, increasing proof size and queries. While STARK proofs have logarithmic overhead, bigger traces still produce more witness rows, so proof size and generation time scale roughly linearly with n_steps.

Verifier configuration overhead: The verifier configuration consists of four felts (layout, hasher, stone_version, memory_verification). When serializing the proof, these four felts form a prefix and do not materially increase calldata size.

Calldata size: Serializing the 400 KB small proof into a flat list of felts yields tens of kilobytes of calldata. The on-chain call must pass thousands of felts to the verifier. For full-trace proofs, calldata will be correspondingly larger.

Latency: The repository does not provide timing measurements. Typical STARK pipelines include: (1) compile (~0.5 s when cached), (2) cairo-run to produce trace (seconds for small programs), (3) cpu_air_prover to generate the proof (seconds to minutes depending on trace size), (4) serialization (sub-second), and (5) on-chain verification (several seconds). The full trace may take tens of seconds or more, so Atlantic's 10–20 s managed service may remain competitive.

Sources:

- Dev-log describing the small Stone proof size and FRI parameters.
- Proof loader showing the four-felt verifier configuration prefix.

Gaps/Uncertainties:

- There are no measurements of proof sizes or generation times for larger traces. Without this data, the scaling relationship cannot be quantified.
- The actual calldata size is not provided; estimates are based on typical STARK encoding.

Next Steps:

- Once the full-trace proof can be generated, measure its size and the time taken by each stage (compile, trace generation, prover, serializer, on-chain verification).
- Use these measurements to determine whether local Stone proofs can beat Atlantic's latency and to project storage needs for storing proofs and traces.
- Explore recursive proof techniques or compression to reduce on-chain calldata.

---

RESEARCH GAP #3: INTEGRITY VERIFIER COMPATIBILITY

Summary: The Integrity verifier expects a VerifierConfiguration struct containing four felts—layout, hasher, stone_version and memory_verification—and a StarkProofWithSerde struct that includes the STARK configuration, public input, unsent commitment and witness. Stone proofs produced locally must be annotated and generated with FRI parameters and layout settings matching the verifier. Without annotations, the proof_serializer fails ("Unexpected number of interaction elements: 0"). Even annotated proofs will be rejected by the verifier if the AIR or layout differs, resulting in invalid final_pc. Atlantic wraps Stone proofs into the expected format, but local proofs require the same process.

Findings:

VerifierConfiguration: The Rust operator defines an empty_verifier_configuration function that sets layout, hasher, stone_version and memory_verification to zero felts. When constructing a real configuration, these felts correspond to ASCII strings (e.g., "recursive", "keccak_160_lsb", "stone5", "strict"). The Python zkML service converts these strings to felts before prefixing them to the proof calldata.

StarkProofWithSerde: empty_stark_proof builds a placeholder with nested config, public_input, unsent_commitment and witness fields. Serialization helpers convert each nested structure into JSON by encoding every felt as a hex string. This implies that a real proof must populate all these fields with meaningful data.

Transformation requirements: The dev-log notes that a Stone proof without annotations was rejected by proof_serializer, and adding annotations (via cpu_air_prover --generate_annotations) allowed serialization. The annotated proof still failed at the verifier due to invalid final_pc, indicating that the AIR or layout used when generating the proof must match the verifier's expected program. Atlantic's managed service produces a Stone proof JSON that, when parsed into VerifierConfiguration + StarkProofWithSerde, matches the verifier.

Sources:

- Definition of VerifierConfiguration and StarkProofWithSerde fields in the Rust operator.
- Serialization functions for the proof and configuration.
- zkML proof service prefixing verifier settings.
- Dev-log describing serializer and verifier failures.

Gaps/Uncertainties:

- The exact field list of StarkProofWithSerde is extensive; only high-level structure is shown. Without access to the Integrity repository, nested field definitions (e.g., FRI layers) remain opaque.
- The dev-log does not specify whether Atlantic performs additional transformations (e.g., adding interaction metadata); such details must be verified from Herodotus documentation.

Next Steps:

- Examine the Integrity proof_serializer source to understand exactly what data it expects in each field.
- Compare Atlantic-generated proof JSON with a local Stone proof to identify structural differences.
- Ensure that local proof generation uses the same layout and hasher (recursive, keccak_160_lsb), stone version (stone5) and memory verification (strict) as the verifier.

---

RESEARCH GAP #4: STONE VERSION COMPATIBILITY

Summary: The Integrity verifier deployed on Sepolia expects stone_version = "stone5". The repository configures the verifier with layout="recursive", hasher="keccak_160_lsb", stone_version="stone5", and memory_verification="strict". Atlantic's documentation and the dev-log recommend the same parameters. Proofs generated with different stone versions are unlikely to verify successfully; thus, the local prover must generate stone5 proofs. Other versions (stone4, stone6, stone7) are not mentioned in the repository.

Findings:

Configuration: backend/app/config.py sets INTEGRITY_STONE_VERSION = "stone5" along with INTEGRITY_LAYOUT = "recursive", INTEGRITY_HASHER = "keccak_160_lsb", and INTEGRITY_MEMORY_VERIFICATION = "strict". These values encode the verifier's expectations.

Atlantic alignment: The dev-log notes that Atlantic's managed proving service uses the same tuple (recursive, keccak_160_lsb, stone5, strict). This indicates that stone5 is the standard version currently supported by Integrity.

Embedding in calldata: When preparing a proof for verification, the zkML proof service prefixes these strings converted to felts before the proof data.

Version detection: The repository does not explain how to determine which stone version a given cpu_air_prover binary produces. Typically, each release of Stone corresponds to a protocol version; generating a different version may require building the prover from another commit.

Sources:

- Integrity configuration specifying stone version.
- Dev-log describing Atlantic settings and the need for stone5.
- Proof prefixing code including stone version.

Gaps/Uncertainties:

- The repository does not list all stone versions or their differences. Without access to the Stone prover repository, we cannot enumerate stone4, stone6, etc.
- It is unclear whether cpu_air_prover can be configured to output different versions.

Next Steps:

- Consult the Stone prover repository's release notes to see available versions and confirm that the current binary outputs stone5 proofs.
- Monitor Herodotus and Starkware announcements in case Integrity upgrades to a newer stone version (which would require local updates).
- If version mismatch becomes an issue, add a check to parse the proof and confirm its stone_version before serialization.

---

RESEARCH GAP #5: LATENCY BREAKDOWN & BOTTLENECK IDENTIFICATION

Summary: The Stone pipeline comprises compilation, trace generation, proof generation, serialization and on-chain verification. Although the repository lacks direct benchmarks, the small proof example (8,192 steps, ~400 KB) suggests that trace generation and proof generation are the dominant stages. Parameter mismatches can cause the prover to abort (Signal 6), representing a significant bottleneck. Overall latency for a small proof may be on the order of several seconds, whereas the full trace could take tens of seconds or more, making it unclear whether local Stone proofs can beat Atlantic's 10–20 second SLA.

Findings:

Compilation (scarb build): Building a Cairo program to Sierra is a one-time cost. When cached, this step takes less than a second; without cache, it may take a few seconds.

Trace generation (cairo-run): The dev-log notes invoking cairo-run with --proof_mode --trace_file --memory_file. Execution time scales with n_steps; a small program (8k steps) likely finishes in under two seconds, whereas the full trace (131k steps) could take significantly longer.

Proof generation (cpu_air_prover): For the small trace, the prover succeeded after FRI parameter tuning; the proof size was ~400 KB. No timing is given, but typical STARK proof generation for 8k steps takes a few seconds. Attempts to generate a proof for the full trace repeatedly aborted with Signal 6, suggesting the prover is sensitive to FRI parameters and that recovery might be time-consuming.

Serialization (proof_serializer): Serializing the annotated small proof to calldata succeeded after adding annotations. The serializer runs as a command-line tool and is expected to be fast (<1 s).

On-chain verification: The dev-log records a call to verify_proof_full_and_register_fact for the small proof, which reverted with invalid final_pc. When the call eventually succeeds, on-chain verification will also contribute to latency (transaction submission and STARK verification on the L2). This could take several seconds.

Bottlenecks: Tuning FRI parameters and generating proofs for large traces appear to be the slowest steps. Parameter mismatch causing Signal 6 wastes time and requires retries. Once the proof is generated, serialization and verification are relatively minor.

Sources:

- Dev-log showing proof generation steps and FRI parameter tuning.
- Proof prefix size (four felts) showing serialization overhead is minimal.

Gaps/Uncertainties:

- No actual timing measurements are given. Estimates rely on general STARK performance characteristics.
- On-chain verification time is unknown; it depends on network conditions and the verifier's implementation.

Next Steps:

- Instrument each stage of the local pipeline (compile, run, prover, serialize, verify) and record timings for the small and full trace.
- Identify whether multi-threading or GPU acceleration for cpu_air_prover can reduce proof generation time.
- Compare measured latency with Atlantic's 10–20 s SLA to determine trade-offs between independence (Stone) and convenience (Atlantic).

---

RESEARCH GAP #6: FAILURE MODE ANALYSIS & ERROR HANDLING

Summary: Failures in the Stone pipeline arise from incorrect input serialization, mismatched FRI parameters, missing annotations, and verifier mismatches. The dev-log records aborts with Signal 6 during proof generation, serializer errors ("Unexpected number of interaction elements: 0"), on-chain reverts (invalid final_pc) and operational failures (INSUFFICIENT_CREDITS). The Python utilities raise exceptions when files are missing or parsing fails, and the zkML service raises FileNotFoundError if no proof is configured. Proper error handling involves validating inputs, ensuring FRI parameters satisfy the degree equation, generating annotated proofs, catching exceptions and on-chain revert messages, and falling back to Atlantic when necessary.

Findings:

Prover errors: When using cpu_air_prover on the full trace, the process repeatedly aborted with Signal 6 despite different FRI parameter attempts. This indicates that mismatched FRI parameters or resource limitations cause native crashes. Fixing the parameters (for the small trace) resolved the issue.

Serializer errors: Passing a non-annotated Stone proof to the proof_serializer failed with "Unexpected number of interaction elements: 0". Using --generate_annotations when generating the proof resolved this.

Verifier reverts: Invoking verify_proof_full_and_register_fact with the small proof (even after successful serialization) resulted in a revert with invalid final_pc. This means the proof's AIR/layout must exactly match the program expected by the verifier; otherwise the final program counter (PC) doesn't align.

Operational errors: Submitting an Atlantic job without credits returned INSUFFICIENT_CREDITS. This requires monitoring credit balances and handling such responses gracefully.

Python error handling: The proof loader checks for missing files and raises FileNotFoundError or CalledProcessError. It also raises ValueError if the serializer output cannot be parsed. The zkML service verifies that either a calldata file or proof JSON is provided; otherwise it raises FileNotFoundError.

Distinguishing errors: Input serialization errors (e.g., wrong u256 format) would be caught during cairo-run or cpu_air_prover; FRI parameter mismatches produce native aborts; missing annotations produce serializer errors; AIR/layout mismatches cause on-chain reverts.

Sources:

- Dev-log showing prover aborts and serializer/verifier failures.
- Proof loader error handling.
- zkML proof service error handling.

Gaps/Uncertainties:

- The repository does not include examples of cairo-run error messages for bad serialization; these must be inferred.
- Only one verifier error (invalid final_pc) is reported; other potential revert reasons are unknown.

Next Steps:

- Enhance the pipeline with detailed logging: capture all subprocess stderr and exit codes, and classify errors (param mismatch, missing annotation, on-chain revert, etc.).
- Implement validation of FRI parameters before running cpu_air_prover (check log2(last_layer_degree_bound) + Σ(fri_step_list) = log2(n_steps) + 4).
- When a local proof fails, fall back to Atlantic and record the failure reason to aid debugging.
- Add unit tests with intentionally malformed inputs to ensure early detection of serialization errors.

---

RESEARCH GAP #7: ATLANTIC PRICING & OPERATIONAL MODEL

Summary: The repository mentions that Atlantic (Herodotus's managed Stone/SHARP prover) offers free proof generation on Sepolia and requires credits on mainnet. No specific pricing, quotas or rate limits are documented. Submitting a job without sufficient credits returns INSUFFICIENT_CREDITS. Without external documentation, details such as cost per proof, volume discounts, rate limits and SLA remain unknown.

Findings:

Free vs paid tiers: The dev-log notes that Atlantic "can produce the Stone-style proof … required by Integrity and can also handle L1 verification (Sepolia is free; mainnet needs credits)". This indicates that testnet use is free while mainnet is paid.

Submission flow: The log describes a typical Atlantic flow: upload the program JSON (POST …/atlantic-query), poll for the result, download the Stone proof, then parse it into VerifierConfiguration + StarkProofWithSerde.

Operational constraints: An attempted submission with declaredJobSize=XS/S, sharpProver=stone returned INSUFFICIENT_CREDITS. There is no mention of rate limits or free call limits.

Configuration: The backend config includes ATLANTIC_API_KEY and ATLANTIC_BASE_URL, implying that an API key controls access and credit balance.

Sources:

- Dev-log describing Atlantic usage and credit requirement.
- Dev-log recording INSUFFICIENT_CREDITS response.
- Backend configuration specifying Atlantic API key and base URL.

Gaps/Uncertainties:

- The repository does not include any official pricing tables, cost per proof, volume discounts, rate limits or SLA information.
- Without internet access, these details cannot be confirmed.

Next Steps:

- Consult Herodotus/Atlantic documentation or support for current pricing and credit packages. Determine the cost per proof and any free allowances on mainnet.
- Request test credits and measure Atlantic's end-to-end latency and throughput to inform cost/benefit analysis.
- Compare the total cost and latency of Atlantic against the cost of running local Stone proofs (compute time, storage, engineering effort) to determine when local proving becomes advantageous.

