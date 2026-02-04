/**
 * Obsqra ZKML Demo - Functional Implementation
 */

// API configuration
const API_BASE = window.location.hostname === 'starknet.obsqra.fi' 
    ? 'https://starknet.obsqra.fi/api/v1'
    : 'http://localhost:8001/api/v1';

// State
let currentProof = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    const generateBtn = document.getElementById('generateBtn');
    if (generateBtn) {
        generateBtn.addEventListener('click', handleGenerateProof);
    }
});

async function handleGenerateProof() {
    const btn = document.getElementById('generateBtn');
    const btnText = document.getElementById('btnText');
    const btnSpinner = document.getElementById('btnSpinner');
    const proofSection = document.getElementById('proofSection');
    const constraintSection = document.getElementById('constraintSection');
    
    // Show loading state
    btn.disabled = true;
    btnText.textContent = 'Generating...';
    btnSpinner.style.display = 'inline-block';
    
    try {
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
        currentProof = data;
        
        // Display proof
        displayProof(data);
        displayConstraints(data);
        
        // Show sections
        proofSection.style.display = 'block';
        constraintSection.style.display = 'block';
        
        // Scroll to proof
        proofSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
    } catch (error) {
        console.error('Proof generation error:', error);
        alert('Failed to generate proof. Make sure the backend is running.\n\nError: ' + error.message);
    } finally {
        // Reset button
        btn.disabled = false;
        btnText.textContent = 'Generate STARK Proof';
        btnSpinner.style.display = 'none';
    }
}

function displayProof(data) {
    const proofHash = document.getElementById('proofHash');
    const proofTime = document.getElementById('proofTime');
    const proofSize = document.getElementById('proofSize');
    const proofAllocation = document.getElementById('proofAllocation');
    const proofSource = document.getElementById('proofSource');
    
    if (proofHash) {
        proofHash.textContent = data.proof_hash.slice(0, 32) + '...';
    }
    
    if (proofTime) {
        proofTime.textContent = data.generation_time_seconds.toFixed(2) + 's';
    }
    
    if (proofSize) {
        proofSize.textContent = data.proof_size_kb.toFixed(2) + ' KB';
    }
    
    if (proofAllocation) {
        const jedi = (data.jediswap_pct / 100).toFixed(1);
        const ekubo = (data.ekubo_pct / 100).toFixed(1);
        proofAllocation.textContent = `${jedi}% Jediswap, ${ekubo}% Ekubo`;
    }
    
    if (proofSource) {
        const source = data.proof_source || 'unknown';
        let sourceLabel = source;
        let sourceClass = '';
        
        if (source === 'stone') {
            sourceLabel = 'Stone Prover (Local)';
            sourceClass = 'stone-badge';
        } else if (source === 'luminair') {
            sourceLabel = 'LuminAIR';
            sourceClass = 'luminair-badge';
        } else if (source === 'luminair_fallback') {
            sourceLabel = 'LuminAIR (Fallback)';
            sourceClass = 'luminair-badge';
        } else if (source === 'mock') {
            sourceLabel = 'Mock (Demo)';
            sourceClass = 'mock-badge';
        }
        
        proofSource.textContent = sourceLabel.toUpperCase();
        proofSource.className = `source-badge ${sourceClass}`;
    }
}

function displayConstraints(data) {
    const constraintList = document.getElementById('constraintList');
    if (!constraintList) return;
    
    const maxSingle = Math.max(data.jediswap_pct, data.ekubo_pct) / 100;
    const total = (data.jediswap_pct + data.ekubo_pct) / 100;
    const jediRisk = data.jediswap_risk;
    const ekuboRisk = data.ekubo_risk;
    
    const maxSingleOk = maxSingle <= 40;
    const totalOk = Math.abs(total - 100) < 1;
    const riskOk = (jediRisk >= 0 && jediRisk <= 100) && (ekuboRisk >= 0 && ekuboRisk <= 100);
    
    constraintList.innerHTML = `
        <div class="constraint-item ${maxSingleOk ? '' : 'violated'}">
            <span class="constraint-name">Max 40% single protocol</span>
            <span class="constraint-status">${maxSingleOk ? '✅ Verified' : '❌ Violated'} (${maxSingle.toFixed(1)}%)</span>
        </div>
        <div class="constraint-item ${totalOk ? '' : 'violated'}">
            <span class="constraint-name">Total allocation = 100%</span>
            <span class="constraint-status">${totalOk ? '✅ Verified' : '❌ Violated'} (${total.toFixed(1)}%)</span>
        </div>
        <div class="constraint-item ${riskOk ? '' : 'violated'}">
            <span class="constraint-name">Risk scores within bounds (0-100)</span>
            <span class="constraint-status">${riskOk ? '✅ Verified' : '❌ Violated'}</span>
        </div>
    `;
}
