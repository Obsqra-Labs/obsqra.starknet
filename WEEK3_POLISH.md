# Week 3: Final Polish (1-2 days)

## Current: 75% Complete (7/10)

Remaining:
- Error boundaries
- Loading skeletons
- Mobile responsive
- Documentation

---

## Task 1: Error Boundary (30 min)

Wrap Dashboard in error boundary to catch React errors gracefully.

**File**: `frontend/src/components/ErrorBoundary.tsx`

```tsx
'use client';

import { Component, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: any) {
    console.error('ErrorBoundary caught:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="min-h-screen bg-gradient-to-b from-slate-950 to-slate-900 flex items-center justify-center p-4">
          <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-8 max-w-md">
            <h2 className="text-2xl font-bold text-red-400 mb-4">
              Something went wrong
            </h2>
            <p className="text-gray-300 mb-4">
              {this.state.error?.message || 'An unexpected error occurred'}
            </p>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-red-500 hover:bg-red-600 rounded-lg text-white"
            >
              Reload Page
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
```

**Wrap Dashboard in page.tsx**:
```tsx
<ErrorBoundary>
  <Dashboard />
</ErrorBoundary>
```

---

## Task 2: Loading Skeletons (30 min)

**File**: `frontend/src/components/LoadingSkeleton.tsx`

```tsx
export function CardSkeleton() {
  return (
    <div className="bg-slate-900/70 border border-white/10 rounded-xl p-6 animate-pulse">
      <div className="h-6 bg-white/10 rounded w-1/3 mb-4"></div>
      <div className="h-12 bg-white/10 rounded w-2/3"></div>
    </div>
  );
}

export function TableSkeleton({ rows = 3 }: { rows?: number }) {
  return (
    <div className="space-y-3">
      {[...Array(rows)].map((_, i) => (
        <div key={i} className="h-16 bg-white/5 rounded-lg animate-pulse"></div>
      ))}
    </div>
  );
}
```

**Use in RebalanceHistory**:
```tsx
if (loading && history.length === 0) {
  return <TableSkeleton rows={5} />;
}
```

---

## Task 3: Mobile Responsive (1 hour)

**Update Dashboard.tsx** - Make stats grid responsive:
```tsx
{/* Before */}
<div className="grid grid-cols-3 gap-4">

{/* After */}
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
```

**Update RebalanceHistory.tsx** - Mobile table:
```tsx
{/* Desktop */}
<div className="hidden md:block">
  <table>...</table>
</div>

{/* Mobile */}
<div className="md:hidden space-y-3">
  {history.map(record => (
    <div className="bg-white/5 rounded-lg p-4">
      <div className="flex justify-between mb-2">
        <span className="text-xs text-gray-400">{formatTimeAgo(record.timestamp)}</span>
        <ProofBadge {...} />
      </div>
      <div className="space-y-1">
        <div>Jedi: {record.jediswap_pct}%</div>
        <div>Ekubo: {record.ekubo_pct}%</div>
      </div>
    </div>
  ))}
</div>
```

---

## Task 4: Documentation (30 min)

**File**: `USER_GUIDE.md`

```markdown
# Obsqura Yield Optimizer - User Guide

## Overview

Obsqura is a verifiable AI-powered yield optimizer on Starknet. Every allocation decision is:
- Calculated by AI risk engine
- Cryptographically proven (STARK)
- Verified on-chain
- Fully auditable

## Getting Started

1. **Connect Wallet**
   - Visit https://starknet.obsqra.fi
   - Click "Connect Wallet"
   - Select Argent X or Braavos
   - Approve connection

2. **View Dashboard**
   - See current allocation (JediSwap vs Ekubo)
   - Check TVL (Total Value Locked)
   - Review rebalance history with proofs

3. **AI Orchestration** (Coming Soon)
   - Click "AI Risk Engine: Orchestrate Allocation"
   - AI analyzes protocol metrics
   - Generates STARK proof
   - Executes allocation on-chain
   - View proof in rebalance history

## Understanding Proofs

Each rebalance has a cryptographic proof:

- **⏳ Generated** (Yellow) - Proof created, not yet on-chain
- **✓ Submitted** (Blue) - Sent to SHARP for L1 verification
- **🔄 Verifying** (Orange) - SHARP verifying (10-60 min)
- **✅ Verified** (Green) - Proof verified on Ethereum L1

**Hover over any proof badge** to see:
- Full proof hash
- Transaction hash (click to view on Voyager)
- Fact hash (L1 verification)
- Submission timestamp

## Rebalance History

View all past allocations:
- Time of rebalance
- Allocation percentages (Jediswap/Ekubo)
- Risk scores for each protocol
- Proof verification status
- Transaction link

**Auto-refreshes every 30 seconds**

## Technical Details

- **Network**: Starknet Sepolia (Testnet)
- **Proof System**: STARK (via LuminAIR)
- **Verification**: SHARP → Ethereum L1
- **Contracts**: RiskEngine, StrategyRouterV2
- **Backend**: Python (FastAPI)
- **Frontend**: Next.js + React

## Support

- GitHub: https://github.com/Obsqra-Labs/obsqra.starknet
- Issues: https://github.com/Obsqra-Labs/obsqra.starknet/issues
```

---

## Implementation Order

1. **ErrorBoundary** (30 min) - Catch React errors
2. **LoadingSkeleton** (30 min) - Better loading UX
3. **Mobile Responsive** (1 hour) - Works on all devices
4. **Documentation** (30 min) - User guide

**Total: 2.5 hours → V1.3 COMPLETE (100%)**

---

## Start With: Error Boundary

Let's make the app bulletproof first.

