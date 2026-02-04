# Transparency Dashboard

This document explains real-time proof visibility, model version display, verification status tracking, fact registry integration, and complete audit trail.

## Real-Time Proof Visibility

### Proof Display

**Dashboard Components:**
- Latest proof hash (clickable)
- Proof generation timestamp
- Proof size and generation time
- Verification status badge

**Real-Time Updates:**
- Auto-refresh every 10 seconds
- Status changes immediately
- New proofs appear automatically
- Verification status updates

### Proof Information

**Displayed Data:**
- **Proof Hash:** Unique identifier
- **Fact Hash:** SHARP registry identifier
- **Status:** Verified/Pending/Failed
- **Generation Time:** 2-4 seconds
- **Size:** ~400-500 KB

**User Actions:**
- Click proof hash to explore
- View verification details
- Download proof for verification
- Share proof hash

## Model Version Display

### Current Model Information

**Dashboard Section:**
- Active model version (e.g., "1.0.0")
- Model hash (truncated)
- Deployment date
- Description

**Details View:**
- Full model hash
- Version history
- Upgrade timeline
- Model code link

### Version History

**Display:**
- All previous versions
- Chronological timeline
- Upgrade transactions
- Model changes

**User Actions:**
- View version details
- Compare versions
- Check upgrade history
- Verify model hashes

## Verification Status Tracking

### Status Indicators

**Visual Badges:**
- ✅ **Verified:** Green badge, proof is valid
- ⏳ **Pending:** Yellow badge, verification in progress
- ❌ **Failed:** Red badge, verification failed

**Status Details:**
- Verification timestamp
- Fact registry address
- Verification count
- Last checked time

### Real-Time Tracking

**Auto-Update:**
- Polls verification status
- Updates badges automatically
- Shows progress indicators
- Notifies on status change

**Manual Refresh:**
- Refresh button
- Force status check
- Clear cache option
- Reload data

## Fact Registry Integration

### Registry Lookup

**Dashboard Integration:**
- Fact registry address displayed
- Direct link to registry
- Query interface
- Verification results

**User Actions:**
- Click to view registry
- Query fact hash
- Verify on-chain
- Check registration status

### On-Chain Verification

**Display:**
- Fact hash status
- Registry confirmation
- Verification array length
- Registration timestamp

**Verification Tools:**
- Direct contract query
- Starkscan explorer link
- Verification status API
- Independent verification guide

## Complete Audit Trail

### Allocation History

**Display:**
- All allocation decisions
- Chronological list
- Filter by date/status
- Search functionality

**For Each Decision:**
- Decision ID
- Timestamp
- Allocation percentages
- Risk scores
- Proof hash
- Transaction hash
- Verification status
- Model version

### Audit Trail Features

**Filtering:**
- Date range
- Verification status
- Protocol allocation
- Model version
- Performance metrics

**Export:**
- CSV format
- JSON format
- PDF report
- Custom date ranges

### Performance Tracking

**Metrics Display:**
- Allocation performance
- Risk score trends
- APY comparisons
- Yield accrual

**Historical Analysis:**
- Performance over time
- Model version impact
- Allocation effectiveness
- Risk-adjusted returns

## Dashboard Components

### Main Dashboard

**Sections:**
1. **Current Status:**
   - Latest allocation
   - Current verification status
   - Active model version
   - Recent proof hash

2. **Verification Status:**
   - All pending verifications
   - Recent verified proofs
   - Failed verifications
   - Verification timeline

3. **Model Information:**
   - Current model version
   - Model hash
   - Deployment date
   - Version history

4. **Proof Information:**
   - Latest proof hash
   - Fact hash
   - Verification status
   - Registry links

### Transparency View

**Dedicated Page:**
- Complete proof information
- Model provenance details
- Verification status
- Audit trail access

**Features:**
- Detailed proof view
- Model version comparison
- Verification history
- Export capabilities

## User Experience

### At-a-Glance Information

**Quick View:**
- Proof status badge
- Model version
- Latest allocation
- Verification status

**Design Philosophy:**
- Simple, clear display
- Quick action buttons
- Real returns focus
- Provable model showcase

### Detailed Information

**Expandable Sections:**
- Click for details
- Modal views
- Full information
- Export options

**Navigation:**
- Breadcrumb navigation
- Related links
- Quick actions
- Help tooltips

## Integration Points

### Backend API

**Endpoints Used:**
- `/api/v1/verification/verification-status/{proof_job_id}`
- `/api/v1/model-registry/current`
- `/api/v1/model-registry/history`
- `/api/v1/risk-engine/decisions`

### On-Chain Queries

**Contract Calls:**
- ModelRegistry.get_current_model()
- FactRegistry.get_all_verifications_for_fact_hash()
- RiskEngine.get_decision()

### Real-Time Updates

**Polling:**
- Status checks every 10 seconds
- New allocations detected
- Verification status updates
- Model changes notified

## Best Practices

### Display Guidelines

1. **Clear Status Indicators:**
   - Use color coding
   - Provide tooltips
   - Show timestamps
   - Include links

2. **Accessible Information:**
   - Clickable hashes
   - Explorer links
   - Copy-to-clipboard
   - Export options

3. **Performance:**
   - Lazy loading
   - Pagination
   - Caching
   - Optimized queries

## Next Steps

- **[Model Provenance](02-model-provenance.md)** - Version tracking
- **[On-Chain Verification](01-on-chain-zkml-verification.md)** - Verification details
- **[User Guide: Viewing Transparency](../02-user-guides/03-viewing-transparency.md)** - User instructions

---

**Transparency Dashboard Summary:** Real-time display of proof hashes, model versions, verification status, and complete audit trail, providing full transparency and verifiability.
