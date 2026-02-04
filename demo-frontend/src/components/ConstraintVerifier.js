/**
 * ConstraintVerifier Component
 * Shows constraint verification in proofs
 */

export class ConstraintVerifier {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
    }

    render(proofData = null) {
        const constraints = [
            { name: 'Max 40% single protocol', key: 'max_single_protocol', value: 40 },
            { name: 'Total allocation = 100%', key: 'total_allocation', value: 100 },
            { name: 'Risk scores within bounds', key: 'risk_bounds', value: '0-100' }
        ];

        let html = `
            <h3>Constraint Verification</h3>
            <p>DAO constraints enforced cryptographically in proofs:</p>
            <ul class="constraint-list">
        `;

        if (proofData) {
            const maxSingle = Math.max(proofData.jediswap_pct, proofData.ekubo_pct) / 100;
            const total = (proofData.jediswap_pct + proofData.ekubo_pct) / 100;
            const jediRisk = proofData.jediswap_risk;
            const ekuboRisk = proofData.ekubo_risk;

            // Check constraints
            const maxSingleOk = maxSingle <= 40;
            const totalOk = Math.abs(total - 100) < 1; // Allow small rounding
            const riskOk = (jediRisk >= 0 && jediRisk <= 100) && (ekuboRisk >= 0 && ekuboRisk <= 100);

            html += `
                <li class="constraint-item ${maxSingleOk ? 'verified' : 'violated'}">
                    <span>Max 40% single protocol</span>
                    <span>${maxSingleOk ? '✅ Verified' : '❌ Violated'} (${maxSingle.toFixed(1)}%)</span>
                </li>
                <li class="constraint-item ${totalOk ? 'verified' : 'violated'}">
                    <span>Total allocation = 100%</span>
                    <span>${totalOk ? '✅ Verified' : '❌ Violated'} (${total.toFixed(1)}%)</span>
                </li>
                <li class="constraint-item ${riskOk ? 'verified' : 'violated'}">
                    <span>Risk scores within bounds (0-100)</span>
                    <span>${riskOk ? '✅ Verified' : '❌ Violated'}</span>
                </li>
            `;
        } else {
            constraints.forEach(constraint => {
                html += `
                    <li class="constraint-item">
                        <span>${constraint.name}</span>
                        <span>Pending proof generation</span>
                    </li>
                `;
            });
        }

        html += `
            </ul>
            <p class="constraint-note">
                <strong>Note:</strong> Constraints are enforced cryptographically in the proof.
                Violations cannot produce valid proofs.
            </p>
        `;

        this.container.innerHTML = html;
    }
}
