# Revenue Model and Pricing Strategy - Obsqra Labs
## Financial Analysis and Pricing Framework

**Date**: January 27, 2026  
**Author**: Obsqra Labs Research Team  
**Status**: Strategic Planning Document  
**Category**: Business Strategy - Financial

---

## Executive Summary

This document outlines Obsqra Labs' revenue model and pricing strategy for the "Open Core + Enterprise Service" approach. The model includes revenue streams from open source consulting, enterprise service, and potential grants, with detailed pricing analysis, cost structure, unit economics, and revenue projections.

**Revenue Strategy**: Open source builds ecosystem (60% focus), enterprise service generates revenue (40% focus), creating sustainable business model.

**Key Insight**: Infrastructure cost is fixed, value scales with usage, enabling 99.8%+ cost savings vs Atlantic while maintaining profitability.

---

## Table of Contents

1. [Revenue Streams](#revenue-streams)
2. [Pricing Strategy](#pricing-strategy)
3. [Cost Structure Analysis](#cost-structure-analysis)
4. [Unit Economics](#unit-economics)
5. [Revenue Projections](#revenue-projections)
6. [Sensitivity Analysis](#sensitivity-analysis)
7. [Comparison with Atlantic](#comparison-with-atlantic)
8. [Value-Based Pricing Rationale](#value-based-pricing-rationale)
9. [Pricing Tiers and Packages](#pricing-tiers-and-packages)
10. [Discount and Negotiation Strategy](#discount-and-negotiation-strategy)

---

## Revenue Streams

### Stream 1: Open Source Consulting

**Description**: Consulting services for teams using open source orchestration layer

**Services**:
- Integration support
- Custom development
- Training and workshops
- Architecture consulting

**Pricing**: $150-300/hour
- Integration support: $150/hour
- Custom development: $200/hour
- Training: $300/hour
- Architecture: $250/hour

**Projected Revenue**:
- Year 1: $50,000-100,000
- Year 2: $100,000-200,000
- Assumes 5-10 consulting engagements/year

### Stream 2: Enterprise Service

**Description**: Managed proof generation service for enterprise and funded teams

**Pricing Model**: Infrastructure cost + margin
- Base infrastructure: $100-200/month
- Margin: 20-30%
- Total: $120-260/month per customer

**Projected Revenue**:
- Year 1: $36,000-180,000 (10-30 customers)
- Year 2: $180,000-360,000 (30-60 customers)

### Stream 3: Foundation Grants

**Description**: Starknet Foundation grants for open source infrastructure

**Grant Types**:
- Seed Grant: Up to $25K
- Growth Grant: $25K-$1M

**Projected Revenue**:
- Year 1: $25,000-100,000 (if awarded)
- Year 2: $0-50,000 (one-time grants)

### Total Revenue Projections

**Year 1** (Conservative):
- Consulting: $50,000
- Enterprise Service: $36,000
- Grants: $25,000
- **Total: $111,000**

**Year 1** (Base):
- Consulting: $75,000
- Enterprise Service: $96,000
- Grants: $50,000
- **Total: $221,000**

**Year 1** (Optimistic):
- Consulting: $100,000
- Enterprise Service: $180,000
- Grants: $100,000
- **Total: $380,000**

**Year 2** (Base):
- Consulting: $150,000
- Enterprise Service: $240,000
- Grants: $25,000
- **Total: $415,000**

---

## Pricing Strategy

### Infrastructure Cost + Margin Model

**Rationale**:
- Infrastructure cost is fixed (shared across customers)
- Value scales with usage (customers get more value at scale)
- Margin reflects value, not cost
- Enables competitive pricing vs Atlantic

**Pricing Formula**:
```
Price = Infrastructure_Cost_Per_Customer + Margin
```

**Infrastructure Cost Per Customer**:
- Base infrastructure: $100-200/month (shared)
- Per customer: $10-50/month (scales sub-linearly)
- Support: $50-200/month (depends on tier)

**Margin**:
- Starter: 20% margin
- Professional: 25% margin
- Enterprise: 30% margin

### Value-Based Pricing

**Value Proposition**:
- Atlantic: $0.75/proof × 1,000 proofs/day = $22,500/month
- Obsqra: $200/month (infrastructure cost)
- **Value: $22,300/month savings (99.1%)**

**Pricing Reflects Value**:
- Customer saves $22,300/month
- We charge $200/month
- Customer gets 99.1% savings
- We get sustainable revenue

### Competitive Pricing

**vs Atlantic**:
- Atlantic: $0.75/proof (pay-per-proof)
- Obsqra: $0.0003-0.003/proof (at scale)
- **99.8%+ cost savings**

**vs Self-Hosted**:
- Self-hosted: Infrastructure + maintenance
- Obsqra: Managed service
- **Value: No infrastructure management**

---

## Cost Structure Analysis

### Infrastructure Costs

**Base Infrastructure** (shared):
- Server (8-core, 16GB): $50-100/month
- Storage (100GB SSD): $10-20/month
- Network: $10-20/month
- Monitoring: $10-20/month
- **Total: $80-160/month**

**Per Customer Infrastructure**:
- Additional compute: $5-20/month (scales sub-linearly)
- Storage: $2-10/month
- Network: $2-5/month
- **Total: $9-35/month per customer**

**Scaling**:
- 10 customers: $80 + (10 × $20) = $280/month
- 20 customers: $80 + (20 × $15) = $380/month (economies of scale)
- 50 customers: $80 + (50 × $10) = $580/month (more economies)

### Operational Costs

**Support Costs**:
- Starter: $50/month (email support)
- Professional: $100/month (Slack support)
- Enterprise: $200/month (dedicated support)

**Development Costs**:
- Ongoing development: $2,000-5,000/month
- Feature development: Variable
- Maintenance: $1,000-2,000/month

**Marketing Costs**:
- Content marketing: $500-1,000/month
- Conference/events: $1,000-3,000/month
- Advertising: $500-1,000/month

### Total Cost Structure

**Monthly Fixed Costs**:
- Infrastructure: $80-160
- Development: $2,000-5,000
- Marketing: $1,000-3,000
- **Total: $3,080-8,160/month**

**Per Customer Variable Costs**:
- Infrastructure: $9-35
- Support: $50-200
- **Total: $59-235/customer/month**

---

## Unit Economics

### Per Customer Economics

**Starter Tier** ($200/month):
- Revenue: $200
- Infrastructure: $20
- Support: $50
- **Margin: $130 (65%)**

**Professional Tier** ($500/month):
- Revenue: $500
- Infrastructure: $30
- Support: $100
- **Margin: $370 (74%)**

**Enterprise Tier** ($2,000/month):
- Revenue: $2,000
- Infrastructure: $50
- Support: $200
- **Margin: $1,750 (87.5%)**

### Customer Lifetime Value (LTV)

**Assumptions**:
- Average revenue: $400/month
- Customer lifetime: 24 months
- Churn rate: 10%/year

**LTV Calculation**:
```
LTV = (Monthly Revenue × Gross Margin) × Customer Lifetime
LTV = ($400 × 75%) × 24 months
LTV = $300 × 24 = $7,200
```

### Customer Acquisition Cost (CAC)

**Assumptions**:
- Marketing spend: $2,000/month
- Sales time: 20 hours/month × $100/hour = $2,000/month
- Total: $4,000/month
- Customers acquired: 2/month

**CAC Calculation**:
```
CAC = Total Acquisition Cost / Customers Acquired
CAC = $4,000 / 2 = $2,000
```

### LTV:CAC Ratio

**Calculation**:
```
LTV:CAC = $7,200 / $2,000 = 3.6:1
```

**Target**: > 3:1 ✅ (Meets target)

**Payback Period**:
```
Payback = CAC / (Monthly Revenue × Gross Margin)
Payback = $2,000 / ($400 × 75%) = $2,000 / $300 = 6.7 months
```

**Target**: < 12 months ✅ (Meets target)

---

## Revenue Projections

### Year 1 Projections

**Conservative Scenario**:
- Customers: 10 (avg $300/month)
- MRR: $3,000
- Annual: $36,000
- Costs: $12,000
- **Net: $24,000**

**Base Scenario**:
- Customers: 20 (avg $400/month)
- MRR: $8,000
- Annual: $96,000
- Costs: $24,000
- **Net: $72,000**

**Optimistic Scenario**:
- Customers: 30 (avg $500/month)
- MRR: $15,000
- Annual: $180,000
- Costs: $36,000
- **Net: $144,000**

### Year 2 Projections

**Base Scenario**:
- Customers: 50 (avg $400/month)
- MRR: $20,000
- Annual: $240,000
- Costs: $60,000
- **Net: $180,000**

**Optimistic Scenario**:
- Customers: 75 (avg $500/month)
- MRR: $37,500
- Annual: $450,000
- Costs: $90,000
- **Net: $360,000**

### Year 3 Projections

**Base Scenario**:
- Customers: 100 (avg $400/month)
- MRR: $40,000
- Annual: $480,000
- Costs: $120,000
- **Net: $360,000**

---

## Sensitivity Analysis

### Scenario 1: Lower Customer Acquisition

**Assumptions**:
- 50% of base scenario customers
- Same pricing

**Year 1**:
- Customers: 10
- Revenue: $48,000
- Costs: $12,000
- **Net: $36,000**

**Impact**: Still profitable, slower growth

### Scenario 2: Higher Churn

**Assumptions**:
- 20% churn (vs 10% base)
- Same acquisition

**Year 1**:
- Customers: 16 (vs 20)
- Revenue: $76,800
- Costs: $19,200
- **Net: $57,600**

**Impact**: Reduced revenue, still profitable

### Scenario 3: Lower Pricing

**Assumptions**:
- 20% price reduction
- Same customer count

**Year 1**:
- Customers: 20
- Revenue: $76,800 (vs $96,000)
- Costs: $24,000
- **Net: $52,800**

**Impact**: Reduced margin, still profitable

### Scenario 4: Higher Infrastructure Costs

**Assumptions**:
- 50% higher infrastructure costs
- Same revenue

**Year 1**:
- Revenue: $96,000
- Costs: $30,000 (vs $24,000)
- **Net: $66,000**

**Impact**: Reduced margin, still profitable

---

## Comparison with Atlantic

### Cost Comparison

**At 1,000 proofs/day**:
- Atlantic: $0.75/proof × 1,000 = $750/day = $22,500/month
- Obsqra: $200/month (infrastructure)
- **Savings: $22,300/month (99.1%)**

**At 10,000 proofs/day**:
- Atlantic: $0.75/proof × 10,000 = $7,500/day = $225,000/month
- Obsqra: $500/month (infrastructure)
- **Savings: $224,500/month (99.8%)**

### Break-Even Analysis

**For Customer**:
- Atlantic cost: $22,500/month (1K proofs/day)
- Obsqra cost: $200/month
- **Break-even: Immediate (saves from day 1)**

**For Obsqra**:
- Infrastructure: $200/month
- Support: $100/month
- **Break-even: 1 customer at $300/month**

### Value Proposition

**Customer Perspective**:
- Saves $22,300/month
- Pays $200/month
- **ROI: 11,150%**

**Obsqra Perspective**:
- Costs $200/month
- Charges $200/month
- **Margin: 0% (at cost)**
- **But**: Infrastructure shared, margin improves with scale

---

## Value-Based Pricing Rationale

### Value Calculation

**Customer Value**:
- Cost savings vs Atlantic: $22,300/month
- Time savings (no infrastructure): $500/month (estimated)
- Support value: $200/month (estimated)
- **Total Value: $23,000/month**

**Obsqra Pricing**:
- Starter: $200/month
- Professional: $500/month
- Enterprise: $2,000/month

**Value Capture**:
- Starter: 0.9% of value
- Professional: 2.2% of value
- Enterprise: 8.7% of value

**Rationale**: Capture small % of massive value, still profitable

### Pricing Psychology

**Anchor Point**: Atlantic at $0.75/proof
- Customer sees $22,500/month cost
- Obsqra at $200/month seems cheap
- **99.1% savings is compelling**

**Value Perception**:
- Customer saves $22,300/month
- Pays $200/month
- **Feels like getting value, not paying cost**

---

## Pricing Tiers and Packages

### Starter Package

**Target**: Small teams, early-stage

**Included**:
- Up to 1,000 proofs/day
- Standard API access
- Email support (48h)
- 99.5% uptime SLA
- Basic monitoring

**Price**: $200/month

**Economics**:
- Revenue: $200
- Costs: $70
- **Margin: $130 (65%)**

### Professional Package

**Target**: Growing teams, funded startups

**Included**:
- Up to 10,000 proofs/day
- Priority API access
- Slack support (24h)
- 99.9% uptime SLA
- Advanced monitoring
- Custom integrations

**Price**: $500/month

**Economics**:
- Revenue: $500
- Costs: $130
- **Margin: $370 (74%)**

### Enterprise Package

**Target**: Large teams, enterprise

**Included**:
- Unlimited proofs
- Dedicated infrastructure
- Dedicated support (4h)
- 99.99% uptime SLA
- Custom monitoring
- White-label options
- Custom features

**Price**: $2,000+/month (custom)

**Economics**:
- Revenue: $2,000
- Costs: $250
- **Margin: $1,750 (87.5%)**

---

## Discount and Negotiation Strategy

### Discount Framework

**Volume Discounts**:
- 2-year contract: 10% discount
- 3-year contract: 15% discount
- Annual prepay: 5% discount

**Early Adopter Discount**:
- First 10 customers: 20% discount (first 6 months)
- Beta customers: 30% discount (first 3 months)

**Non-Profit/Research**:
- Academic institutions: 25% discount
- Non-profits: 20% discount
- Research labs: 25% discount

### Negotiation Guidelines

**When to Discount**:
- Strategic partnerships
- High-volume customers
- Long-term contracts
- Early adopters

**Discount Limits**:
- Maximum discount: 30%
- Maintain minimum margin: 50%
- Protect unit economics

**Value Add Instead**:
- Additional support hours
- Custom features
- Extended SLA
- Training/workshops

---

## Conclusion

The revenue model enables sustainable business while providing massive value to customers:

**Customer Value**:
- ✅ 99.8%+ cost savings vs Atlantic
- ✅ Managed service (no infrastructure)
- ✅ Enterprise support
- ✅ Vertical expertise

**Obsqra Value**:
- ✅ Sustainable revenue
- ✅ High margins (65-87%)
- ✅ Scalable model
- ✅ Business sustainability

**Next Steps**:
1. Finalize pricing tiers
2. Develop pricing page
3. Create sales materials
4. Launch enterprise service

**Timeline**: Pricing finalized in Month 3, launch in Month 6

---

**This revenue model enables business sustainability while providing exceptional value to customers.**
