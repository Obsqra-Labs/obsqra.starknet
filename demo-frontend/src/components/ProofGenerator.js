/**
 * ProofGenerator Component
 * Shows Stone prover proof generation in real-time
 */

// Use production API if on production domain, otherwise localhost
const API_BASE = window.location.hostname === 'starknet.obsqra.fi' 
    ? 'https://starknet.obsqra.fi/api/v1'
    : 'http://localhost:8001/api/v1';

export class ProofGenerator {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.proofData = null;
    }

    render() {
        this.container.innerHTML = `
            <h3>STARK Proof Generation</h3>
            <button id="generateProofBtn" class="btn-primary">Generate STARK Proof</button>
            <div id="proofStatus"></div>
            <div id="proofDetails" class="proof-details" style="display: none;"></div>
        `;

        document.getElementById('generateProofBtn').addEventListener('click', () => this.generateProof());
    }

    async generateProof() {
        const statusDiv = document.getElementById('proofStatus');
        const detailsDiv = document.getElementById('proofDetails');
        
        statusDiv.innerHTML = `
            <div class="proof-status generating">
                <div class="spinner"></div>
                <p>Generating STARK proof...</p>
            </div>
        `;
        detailsDiv.style.display = 'none';

        try {
            const startTime = Date.now();
            const response = await fetch(`${API_BASE}/demo/generate-proof`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    jediswap_metrics: {
                        utilization: 75,
                        volatility: 30,
                        liquidity: 5000000,
                        audit_score: 85,
                        age_days: 180
                    },
                    ekubo_metrics: {
                        utilization: 60,
                        volatility: 25,
                        liquidity: 3000000,
                        audit_score: 90,
                        age_days: 120
                    }
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);

            this.proofData = data;

            // Update status
            const proofSource = data.proof_source || 'unknown';
            const sourceLabel = proofSource === 'stone' ? 'Stone Prover (Local)' : 
                              proofSource === 'luminair' ? 'LuminAIR' : proofSource;

            statusDiv.innerHTML = `
                <div class="proof-status success">
                    <p><strong>✅ Proof Generated!</strong></p>
                    <p>Source: ${sourceLabel}</p>
                    <p>Generation Time: ${data.generation_time_seconds.toFixed(2)}s</p>
                </div>
            `;

            // Show details
            detailsDiv.innerHTML = `
                <h4>Proof Details</h4>
                <p><strong>Proof Hash:</strong></p>
                <code>${data.proof_hash}</code>
                <p><strong>Proof Size:</strong> ${data.proof_size_kb.toFixed(2)} KB</p>
                <p><strong>Allocation:</strong> ${(data.jediswap_pct / 100).toFixed(1)}% Jediswap, ${(data.ekubo_pct / 100).toFixed(1)}% Ekubo</p>
                <p><strong>Risk Scores:</strong> Jediswap=${data.jediswap_risk}, Ekubo=${data.ekubo_risk}</p>
                <p><strong>Constraints Verified:</strong> ${data.constraints_verified ? '✅ Yes' : '❌ No'}</p>
                <p><strong>Message:</strong> ${data.message}</p>
            `;
            detailsDiv.style.display = 'block';

        } catch (error) {
            statusDiv.innerHTML = `
                <div class="proof-status error">
                    <p><strong>❌ Proof Generation Failed</strong></p>
                    <p>${error.message}</p>
                    <p>Make sure the backend is running on port 8001</p>
                </div>
            `;
            console.error('Proof generation error:', error);
        }
    }

    getProofData() {
        return this.proofData;
    }
}
