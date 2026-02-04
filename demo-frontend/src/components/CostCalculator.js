/**
 * CostCalculator Component
 * Shows cost savings with Stone prover vs cloud proving
 */

export class CostCalculator {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
    }

    render(proofData = null) {
        const allocationsPerYear = proofData?.cost_savings?.allocations_per_year || 100000;
        const stoneCost = proofData?.cost_savings?.stone_cost ?? 0;
        const cloudCost = proofData?.cost_savings?.cloud_cost ?? (allocationsPerYear * 0.75);
        const savings = proofData?.cost_savings?.annual_savings ?? (cloudCost - stoneCost);
        const savingsPct = proofData?.cost_savings?.savings_percentage ?? ((savings / cloudCost * 100) || 0);

        this.container.innerHTML = `
            <h3>Cost Comparison</h3>
            <p>Annual cost for ${allocationsPerYear.toLocaleString()} allocations:</p>
            
            <div class="cost-comparison">
                <div class="cost-box stone">
                    <h4>Stone Prover (Local)</h4>
                    <div class="cost-amount">$${stoneCost.toLocaleString()}</div>
                    <p>$0 per proof</p>
                    <p>Self-hosted</p>
                </div>
                
                <div class="cost-box cloud">
                    <h4>Cloud Proving</h4>
                    <div class="cost-amount">$${cloudCost.toLocaleString()}</div>
                    <p>$0.75 per proof</p>
                    <p>Managed service</p>
                </div>
            </div>
            
            <div class="savings">
                <h4>Annual Savings</h4>
                <div class="savings-amount">$${savings.toLocaleString()}</div>
                <p>${savingsPct.toFixed(1)}% cost reduction</p>
                <p><strong>Only possible with local Stone prover</strong></p>
            </div>
            
            <div style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 6px;">
                <p><strong>Note:</strong> Both Stone prover and cloud proving are valid options.</p>
                <p>We optimized for cost by using local proving, enabling 95% cost reduction for high-frequency allocations.</p>
            </div>
        `;
    }

    updateAllocations(allocationsPerYear) {
        const stoneCost = 0;
        const cloudCost = allocationsPerYear * 0.75;
        const savings = cloudCost - stoneCost;
        const savingsPct = (savings / cloudCost * 100) || 0;

        this.render({
            cost_savings: {
                allocations_per_year: allocationsPerYear,
                stone_cost: stoneCost,
                cloud_cost: cloudCost,
                annual_savings: savings,
                savings_percentage: savingsPct
            }
        });
    }
}
