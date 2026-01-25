'use client';

import { useAccount } from '@starknet-react/core';
import { useStrategyRouter } from '@/hooks/useStrategyRouter';
import { useRiskEngineBackend } from '@/hooks/useRiskEngineBackend';
import { useSettlement } from '@/hooks/useSettlement';
import { useRiskEngineOrchestration, ProtocolMetrics } from '@/hooks/useRiskEngineOrchestration';
import { useRiskEngineBackendOrchestration, type ProtocolMetrics as BackendProtocolMetrics } from '@/hooks/useRiskEngineBackendOrchestration';
import { useTransactionMonitor, TransactionStatusBadge } from '@/hooks/useTransactionMonitor';
import { useProofGeneration } from '@/hooks/useProofGeneration';
import { useStrategyDeposit } from '@/hooks/useStrategyDeposit';
import { useTransactionHistory } from '@/hooks/useTransactionHistory';
// import { usePoolSelection } from '@/hooks/usePoolSelection';
import { ProofDisplay } from './ProofDisplay';
import { TransactionHistory } from './TransactionHistory';
import { AnalyticsDashboard } from './AnalyticsDashboard';
import { RebalanceHistory } from './RebalanceHistory';
import { DepositAllocationPreview } from './DepositAllocationPreview';
import { IntegrationTests } from './IntegrationTests';
import { categorizeError } from '@/services/errorHandler';
import { useState, useMemo, useEffect } from 'react';
import { getConfig } from '@/lib/config';
import { useProofHistory } from '@/hooks/useProofHistory';
import { ProofBadge } from './ProofBadge';
import { useMarketSnapshot } from '@/hooks/useMarketSnapshot';
import { useMarketMetrics } from '@/hooks/useMarketMetrics';

type TabType = 'overview' | 'analytics' | 'history' | 'integration-tests';

export function Dashboard() {
  // ⚠️ CRITICAL: All useState MUST be called FIRST, in same order every render
  // This prevents "Cannot update a component during render" errors
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [allocationForm, setAllocationForm] = useState({ jediswap: 50, ekubo: 50 });
  const [isUpdating, setIsUpdating] = useState(false);
  const [settlementError, setSettlementError] = useState<string | null>(null);
  const [isCalculatingRisk, setIsCalculatingRisk] = useState(false);
  const [riskError, setRiskError] = useState<string | null>(null);
  const [lastTxHash, setLastTxHash] = useState<string | null>(null);
  const [generatingProofType, setGeneratingProofType] = useState<'risk' | 'allocation' | null>(null);
  const [depositAmount, setDepositAmount] = useState('');
  const [withdrawAmount, setWithdrawAmount] = useState('');
  const [isDepositing, setIsDepositing] = useState(false);
  const [isWithdrawing, setIsWithdrawing] = useState(false);
  const [latestDecision, setLatestDecision] = useState<{
    decisionId?: number;
    proofHash?: string;
    jediswap_pct?: number;
    ekubo_pct?: number;
  } | null>(null);
  
  // Now safe to call other hooks
  const { account, address } = useAccount();
  const router = useStrategyRouter();
  const strategyDeposit = useStrategyDeposit(getConfig().strategyRouterAddress);
  const txHistory = useTransactionHistory();
  const riskEngine = useRiskEngineBackend();
  const settlement = useSettlement();
  const proofGen = useProofGeneration();
  const riskEngineOrchestration = useRiskEngineOrchestration();
  const backendOrchestration = useRiskEngineBackendOrchestration();
  const { status: txStatus } = useTransactionMonitor(lastTxHash || undefined);
  const proofHistory = useProofHistory(5);
  const latestProof = proofHistory.data[0];
  const marketSnapshot = useMarketSnapshot();
  const marketMetrics = useMarketMetrics();
  
  // Fetch user's STRK balance on mount and when address changes
  useEffect(() => {
    if (address && strategyDeposit.isReady) {
      strategyDeposit.fetchBalance();
    }
  }, [address, strategyDeposit.isReady]); // Removed fetchBalance from deps to prevent infinite loop

  // Calculate allocation from live contract data
  const allocation = useMemo(() => {
    return {
      jediswap: router.jediswapAllocation,
      ekubo: router.ekuboAllocation,
    };
  }, [router.jediswapAllocation, router.ekuboAllocation]);

  // Format TVL from live contract data
  const tvlDisplay = useMemo(() => {
    if (router.isLoading) return '...';
    const tvl = BigInt(router.totalValueLocked || '0');
    const tvlEth = Number(tvl) / 1e18;
    return tvlEth.toFixed(2);
  }, [router.isLoading, router.totalValueLocked]);

  // Format yield from live contract data
  const yieldDisplay = useMemo(() => {
    if (router.isLoading) return '...';
    const yieldAmount = BigInt(router.totalYieldAccrued || '0');
    const yieldEth = Number(yieldAmount) / 1e18;
    return yieldEth.toFixed(4);
  }, [router.isLoading, router.totalYieldAccrued]);

  // Format individual protocol TVLs
  const jediTvlDisplay = useMemo(() => {
    if (router.isLoading) return '...';
    const tvl = BigInt(router.jediswapTvl || '0');
    const tvlEth = Number(tvl) / 1e18;
    return tvlEth.toFixed(4);
  }, [router.isLoading, router.jediswapTvl]);

  const ekuboTvlDisplay = useMemo(() => {
    if (router.isLoading) return '...';
    const tvl = BigInt(router.ekuboTvl || '0');
    const tvlEth = Number(tvl) / 1e18;
    return tvlEth.toFixed(4);
  }, [router.isLoading, router.ekuboTvl]);

  // Handle deposit - STRK deposit
  const handleDeposit = async () => {
    if (!depositAmount || parseFloat(depositAmount) <= 0) {
      alert('Please enter a valid deposit amount');
      return;
    }

    setIsDepositing(true);

    // Use real STRK deposit via Strategy Router contract
    if (!address || !strategyDeposit.isReady) {
      alert('❌ Wallet not connected or Strategy Router not ready');
      setIsDepositing(false);
      return;
    }

    try {
      console.log('💰 Depositing STRK to Strategy Router...');
      
      // Execute the deposit transaction
      const txHash = await strategyDeposit.deposit(parseFloat(depositAmount));
      
      console.log('Deposit returned txHash:', txHash);
      
      if (!txHash) {
        throw new Error('Deposit failed - no transaction hash returned');
      }
      
      // Track transaction in history
      console.log('Adding to transaction history...');
      const txId = txHistory.addTransaction(txHash, 'DEPOSIT', {
        amount: depositAmount,
        protocol: 'Strategy Router',
      });
      
      console.log('Transaction added with ID:', txId);
      console.log('Full txHistory state:', txHistory.transactions);

      // Show immediate feedback with allocation breakdown
      const depositAmt = parseFloat(depositAmount);
      const jediswapAmt = (depositAmt * allocation.jediswap) / 100;
      const ekuboAmt = (depositAmt * allocation.ekubo) / 100;
      
      // Check if allocation matches latest recommendation
      const matchesRecommendation = latestDecision && (
        Math.abs(allocation.jediswap - (latestDecision.jediswap_pct || 0)) < 0.1 &&
        Math.abs(allocation.ekubo - (latestDecision.ekubo_pct || 0)) < 0.1
      );
      
      setDepositAmount('');
      alert(
        '✅ Deposit Submitted!\n\n' +
        '💰 Amount: ' + depositAmount + ' STRK\n\n' +
        '📊 Allocation:\n' +
        '  JediSwap: ' + allocation.jediswap.toFixed(2) + '% (' + jediswapAmt.toFixed(4) + ' STRK)\n' +
        '  Ekubo: ' + allocation.ekubo.toFixed(2) + '% (' + ekuboAmt.toFixed(4) + ' STRK)\n\n' +
        (matchesRecommendation && latestDecision?.decisionId ? 
          `✅ Verified: Matches AI Decision #${latestDecision.decisionId}\n` +
          (latestDecision.proofHash ? `🔐 Proof: ${latestDecision.proofHash.slice(0, 12)}...\n` : '') :
          latestDecision?.decisionId ?
          `⚠️ Note: Allocation differs from latest AI Decision #${latestDecision.decisionId}\n` :
          '') +
        '🔗 Tx Hash: ' + txHash.slice(0, 10) + '...\n\n' +
        '⏳ Waiting for confirmation on Starknet...\n\n' +
        'Check History tab to see transaction (should appear as "pending")'
      );

      // Confirm transaction after a reasonable wait (matching Starknet block time ~6 seconds)
      // This will show as "confirmed" in the history tab
      setTimeout(() => {
        console.log('Calling confirmTransaction with ID:', txId);
        console.log('Transactions before reload:', txHistory.transactions);
        
        // Reload from localStorage to get the latest state
        const stored = localStorage.getItem(`obsqra_transaction_history_${address}`);
        if (stored) {
          console.log('📂 Reloaded from localStorage:', stored);
        }
        
        txHistory.confirmTransaction(txId);
        console.log('✅ Deposit confirmed in history:', txHash);
        console.log('Updated txHistory:', txHistory.transactions);
      }, 6000);

    } catch (error: any) {
      console.error('❌ Deposit error:', error);
      console.error('Full error:', JSON.stringify(error, null, 2));
      
      // Extract just the error message if it's nested
      const errorMsg = error.message?.split('\n')[0] || String(error);
      
      alert(
        '❌ Deposit failed\n\n' +
        'Error: ' + errorMsg + '\n\n' +
        'Check console for details'
      );
    } finally {
      setIsDepositing(false);
    }
  };

  // Handle withdraw via Strategy Router
  const handleWithdraw = async () => {
    if (!withdrawAmount || parseFloat(withdrawAmount) <= 0) {
      alert('Please enter a valid withdrawal amount');
      return;
    }

    setIsWithdrawing(true);

    // Use real Strategy Router withdrawal
    if (!address || !strategyDeposit.isReady) {
      alert('❌ Wallet not connected or Strategy Router not ready');
      setIsWithdrawing(false);
      return;
    }

    try {
      console.log('🏧 Withdrawing STRK from Strategy Router...');
      
      const txHash = await strategyDeposit.withdraw(parseFloat(withdrawAmount));
      
      console.log('Withdrawal returned txHash:', txHash);
      
      if (!txHash) {
        throw new Error('Withdrawal failed - no transaction hash returned');
      }
      
      // Track transaction in history
      console.log('Adding withdrawal to transaction history...');
      const txId = txHistory.addTransaction(txHash, 'WITHDRAW', {
        amount: withdrawAmount,
        protocol: 'Strategy Router',
      });
      
      console.log('Withdrawal transaction added with ID:', txId);

      setWithdrawAmount('');
      alert(
        '✅ Withdrawal Submitted!\n\n' +
        '💰 Amount: ' + withdrawAmount + ' STRK\n' +
        '🔗 Tx Hash: ' + txHash.slice(0, 10) + '...\n\n' +
        '⏳ Waiting for confirmation on Starknet...\n\n' +
        'Check History tab to see transaction (should appear as "pending")'
      );

      // Confirm transaction after a reasonable wait
      setTimeout(() => {
        console.log('Calling confirmTransaction for withdrawal with ID:', txId);
        txHistory.confirmTransaction(txId);
        console.log('✅ Withdrawal confirmed in history:', txHash);
      }, 6000);

    } catch (error: any) {
      console.error('❌ Withdrawal error:', error);
      console.error('Full error:', JSON.stringify(error, null, 2));
      
      // Extract just the error message if it's nested
      const errorMsg = error.message?.split('\n')[0] || String(error);
      
      alert(
        '❌ Withdrawal failed\n\n' +
        'Error: ' + errorMsg + '\n\n' +
        'Check console for details'
      );
    } finally {
      setIsWithdrawing(false);
    }
  };

  // Handle allocation update
  const handleUpdateAllocation = async () => {
    const total = allocationForm.jediswap + allocationForm.ekubo;
    if (Math.abs(total - 100) > 0.1) {
      alert('Allocation must total 100%');
      return;
    }

    setIsUpdating(true);
    setSettlementError(null);

    // Use real settlement for allocation updates
    if (!settlement.isConnected) {
      setSettlementError('Wallet not connected. Please connect your wallet first.');
      setIsUpdating(false);
      return;
    }

    try {
      // Update allocation with JediSwap and Ekubo percentages
      const result = await settlement.updateAllocation({
        jediswap: allocationForm.jediswap,
        ekubo: allocationForm.ekubo,
      });

      if (result && result.status === 'success') {
        const txId = txHistory.addTransaction(result.txHash, 'UPDATE_ALLOCATION', {
          jediswap: allocationForm.jediswap,
          ekubo: allocationForm.ekubo,
        });
        txHistory.confirmTransaction(txId);

        alert('✅ Allocation updated on-chain!\nTx: ' + result.txHash.slice(0, 10) + '...\n\nJediSwap: ' + allocationForm.jediswap + '%\nEkubo: ' + allocationForm.ekubo + '%\n\nRefreshing display...');
        setSettlementError(null);
        
        // Wait for transaction to be included, then refresh
        setTimeout(() => {
          console.log('🔄 Refreshing allocation display...');
          router.refetch();
        }, 5000);
      } else {
        // Transaction failed or returned null
        const errorMsg = settlement.error || 'Settlement failed - transaction may have been rejected';
        setSettlementError(errorMsg);
        console.error('❌ Allocation update failed:', errorMsg);
        
        // Show clear error message
        if (errorMsg.includes('Unauthorized') || errorMsg.includes('permission') || errorMsg.includes('ENTRYPOINT_FAILED')) {
          alert('❌ Authorization Error\n\nOnly the contract owner or RiskEngine can update allocations.\n\nTo update allocations, use the "AI Risk Engine: Orchestrate Allocation" button, which will update via RiskEngine.');
        } else {
          alert('❌ Update Failed\n\n' + errorMsg + '\n\nPlease try again or use the AI Risk Engine to update allocations.');
        }
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Settlement failed';
      setSettlementError(errorMsg);
      console.error('Settlement error:', error);
      
      // Show user-friendly error for authorization issues
      if (errorMsg.includes('Unauthorized') || errorMsg.includes('permission') || errorMsg.includes('ENTRYPOINT_FAILED')) {
        alert('❌ Authorization Error\n\nThe contract rejected the allocation update. This function may require admin/owner privileges.\n\nPlease contact the contract administrator or check if your account has the necessary permissions.');
      }
    } finally {
      setIsUpdating(false);
    }
  };

  const handleSliderChange = (protocol: 'jediswap' | 'ekubo', value: number) => {
    const clamped = Math.max(0, Math.min(100, value));
    setAllocationForm({
      jediswap: protocol === 'jediswap' ? clamped : 100 - clamped,
      ekubo: protocol === 'ekubo' ? clamped : 100 - clamped,
    });
  };

  const applyDecision = async (decision: any, label: string) => {
    console.log(`✅ ${label} complete:`, decision);

    setAllocationForm({
      jediswap: decision.jediswap_pct / 100,
      ekubo: decision.ekubo_pct / 100,
    });

    const actualTxHash = decision.tx_hash || `pending-${decision.decision_id}`;
    const txId = txHistory.addTransaction(
      actualTxHash,
      'AI_ORCHESTRATION',
      {
        decisionId: decision.decision_id,
        jediswap: decision.jediswap_pct,
        ekubo: decision.ekubo_pct,
        jediswapRisk: decision.jediswap_risk,
        ekuboRisk: decision.ekubo_risk,
        jediswapApy: decision.jediswap_apy,
        ekuboApy: decision.ekubo_apy,
        rationaleHash: decision.rationale_hash,
        timestamp: new Date(decision.timestamp * 1000).toISOString(),
        blockNumber: decision.block_number,
        aiManaged: true,
      }
    );

    txHistory.confirmTransaction(txId);

    if (!decision.tx_hash && decision.proof_job_id) {
      setTimeout(async () => {
        try {
          const historyResponse = await fetch('/api/v1/analytics/rebalance-history?limit=20');
          if (historyResponse.ok) {
            const history = await historyResponse.json();
            const matchingRecord = history.find((r: any) => r.id === decision.proof_job_id);
            if (matchingRecord?.tx_hash && matchingRecord.tx_hash.startsWith('0x')) {
              txHistory.updateTransaction(txId, { hash: matchingRecord.tx_hash });
            }
          }
        } catch (err) {
          console.warn('Failed to fetch real tx_hash from history:', err);
        }
      }, 3000);
    }

    setLatestDecision({
      decisionId: decision.decision_id,
      proofHash: decision.proof_hash,
      jediswap_pct: decision.jediswap_pct / 100,
      ekubo_pct: decision.ekubo_pct / 100,
    });

    console.log('🔄 Scheduling allocation refresh after orchestration...');
    setTimeout(() => router.refetch(), 8000);
    setTimeout(() => router.refetch(), 20000);

    const proofStatus = decision.proof_status || 'generated';
    const isVerified = proofStatus === 'verified';
    const proofIcon = isVerified ? '✅' : '🔐';
    const proofInfo = decision.proof_hash
      ? `\n\n${proofIcon} STARK Proof:\n${decision.proof_hash.slice(0, 20)}...\nStatus: ${proofStatus}\n${isVerified ? '✅ Locally verified (&lt;1s)\n' : ''}`
      : '';

    alert(
      `✅ ${label} Complete!\n\n` +
      `Decision ID: ${decision.decision_id}\n` +
      `Block: ${decision.block_number}\n\n` +
      `Allocation:\n` +
      `JediSwap: ${decision.jediswap_pct.toFixed(1)}% (Risk: ${decision.jediswap_risk}, APY: ${decision.jediswap_apy.toFixed(2)}%)\n` +
      `Ekubo: ${decision.ekubo_pct.toFixed(1)}% (Risk: ${decision.ekubo_risk}, APY: ${decision.ekubo_apy.toFixed(2)}%)\n` +
      proofInfo +
      `\nFull audit trail available on-chain.`
    );
  };

  // Handle AI Risk Engine orchestration (100% on-chain flow)
  const handleAIOchestration = async () => {
    setIsCalculatingRisk(true);
    setRiskError(null);

    try {
      const jediswapMetrics: BackendProtocolMetrics = {
        utilization: 5000,
        volatility: 4000,
        liquidity: 1,
        audit_score: 95,
        age_days: 700,
      };
      const ekuboMetrics: BackendProtocolMetrics = {
        utilization: 5500,
        volatility: 5700,
        liquidity: 2,
        audit_score: 95,
        age_days: 700,
      };

      console.log('🤖 AI Risk Engine: Starting full on-chain orchestration...');
      const decision = await backendOrchestration.proposeAndExecuteAllocation(
        jediswapMetrics,
        ekuboMetrics
      );

      if (!decision) {
        throw new Error('Failed to execute AI orchestration');
      }

      await applyDecision(decision, 'AI Risk Engine Orchestration');
    } catch (error) {
      const obsqraError = categorizeError(error);
      setRiskError(obsqraError.userMessage);
      console.error('❌ AI orchestration error:', error);
      if (riskEngineOrchestration.error) {
        alert(`❌ AI Orchestration Failed: ${riskEngineOrchestration.error}`);
      }
    } finally {
      setIsCalculatingRisk(false);
      setGeneratingProofType(null);
    }
  };

  const handleMarketOrchestration = async () => {
    setIsCalculatingRisk(true);
    setRiskError(null);

    try {
      console.log('🌍 Market Orchestration: Using read-only mainnet metrics...');
      const decision = await backendOrchestration.proposeFromMarket();
      if (!decision) {
        throw new Error('Failed to execute market orchestration');
      }
      await applyDecision(decision, 'Market Orchestration');
    } catch (error) {
      const obsqraError = categorizeError(error);
      setRiskError(obsqraError.userMessage);
      console.error('❌ Market orchestration error:', error);
      if (backendOrchestration.error) {
        alert(`❌ Market Orchestration Failed: ${backendOrchestration.error}`);
      }
    } finally {
      setIsCalculatingRisk(false);
      setGeneratingProofType(null);
    }
  };


  if (!account) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center p-8 bg-black/40 rounded-2xl border border-purple-500/30 max-w-md">
          <div className="text-6xl mb-4">🔐</div>
          <h2 className="text-2xl font-bold text-white mb-2">Connect Wallet</h2>
          <p className="text-gray-400">Connect your Starknet wallet to access the dashboard.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4 max-w-6xl text-white">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-white">Yield Optimizer</h1>
          <p className="text-gray-400 text-sm">Strategy Router v3.5 on Starknet Sepolia</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="px-4 py-2 rounded-full text-sm font-bold bg-green-500/20 text-green-400 border border-green-500/30">
            Production
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 bg-white/5 p-1 rounded-xl border border-white/10">
        {(['overview', 'analytics', 'history', 'integration-tests'] as TabType[]).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`flex-1 px-4 py-2.5 rounded-lg font-medium transition-all ${activeTab === tab ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg' : 'text-gray-400 hover:text-white hover:bg-white/5'}`}
          >
            {tab === 'overview' && '📊 Overview'}
            {tab === 'analytics' && '📈 Analytics'}
            {tab === 'history' && ('📜 History' + (txHistory.transactions.length > 0 ? ' (' + txHistory.transactions.length + ')' : ''))}
            {tab === 'integration-tests' && '🧪 Integration Tests'}
          </button>
        ))}
      </div>

      {/* Analytics Tab */}
      {activeTab === 'analytics' && <AnalyticsDashboard allocation={allocation} />}

      {/* Integration Tests Tab */}
      {activeTab === 'integration-tests' && (
        <div className="bg-slate-900/70 border border-white/10 rounded-xl p-6 shadow-lg">
          <IntegrationTests />
        </div>
      )}

      {/* History Tab */}
      {activeTab === 'history' && (
        <div className="bg-slate-900/70 border border-white/10 rounded-xl p-6 shadow-lg">
          <TransactionHistory />
        </div>
      )}

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Stats */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="bg-gradient-to-br from-purple-900/60 via-slate-900/70 to-slate-900/80 border border-purple-400/30 rounded-xl p-5 shadow-lg">
              <p className="text-sm text-purple-200 mb-1">Vault TVL (Total Deposits)</p>
              <p className="text-3xl font-bold text-white">{tvlDisplay} <span className="text-lg text-purple-200">STRK</span></p>
              <div className="mt-2 pt-2 border-t border-purple-400/20">
                <p className="text-xs text-purple-300 mb-1">Total Yield Accrued</p>
                <p className="text-xl font-bold text-green-400">{yieldDisplay} <span className="text-sm text-purple-200">STRK</span></p>
              </div>
              <div className="mt-2 pt-2 border-t border-purple-400/20">
                <p className="text-xs text-purple-300 mb-1">Protocol TVL (Deployed)</p>
                <div className="grid grid-cols-2 gap-2 text-xs mt-1">
                  <div>
                    <p className="text-purple-300 mb-0.5">JediSwap</p>
                    <p className="text-white font-semibold">{jediTvlDisplay} STRK</p>
                  </div>
                  <div>
                    <p className="text-purple-300 mb-0.5">Ekubo</p>
                    <p className="text-white font-semibold">{ekuboTvlDisplay} STRK</p>
                  </div>
                </div>
              </div>
            </div>
            <div className="bg-gradient-to-br from-blue-900/60 via-slate-900/70 to-slate-900/80 border border-blue-400/30 rounded-xl p-5 shadow-lg">
              <p className="text-sm text-blue-200 mb-1">🔄 JediSwap</p>
              <p className="text-3xl font-bold text-white">{allocation.jediswap.toFixed(1)}%</p>
              <p className="text-xs text-blue-300 mt-1">TVL: {jediTvlDisplay} STRK</p>
            </div>
            <div className="bg-gradient-to-br from-amber-900/60 via-slate-900/70 to-slate-900/80 border border-amber-400/30 rounded-xl p-5 shadow-lg">
              <p className="text-sm text-orange-200 mb-1">🌀 Ekubo</p>
              <p className="text-3xl font-bold text-white">{allocation.ekubo.toFixed(1)}%</p>
              <p className="text-xs text-orange-300 mt-1">TVL: {ekuboTvlDisplay} STRK</p>
            </div>
          </div>

          {/* Market Snapshot */}
          <div className="bg-slate-900/70 border border-white/10 rounded-xl p-6 shadow-lg">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-xl font-bold text-white">Read‑Only Market Snapshot</h2>
                <p className="text-xs text-gray-400">Mainnet data feed (no writes)</p>
              </div>
              <button
                onClick={() => marketSnapshot.refetch()}
                className="px-3 py-1.5 text-sm bg-gray-700 hover:bg-gray-600 text-white rounded transition-colors flex items-center gap-2"
              >
                🔄 Refresh
              </button>
            </div>

            {marketSnapshot.error && (
              <div className="mb-3 text-sm text-red-400 bg-red-500/10 border border-red-500/30 rounded p-2">
                ⚠️ {marketSnapshot.error}
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
              <div className="bg-slate-800/50 rounded-lg p-3">
                <p className="text-xs text-gray-400 mb-1">Block</p>
                <p className="text-white font-semibold">
                  {marketSnapshot.loading ? '...' : marketSnapshot.data?.block_number ?? '—'}
                </p>
                <p className="text-[11px] text-gray-500 mt-1">
                  {marketSnapshot.data?.timestamp
                    ? new Date(marketSnapshot.data.timestamp * 1000).toLocaleString()
                    : '—'}
                </p>
              </div>
              <div className="bg-slate-800/50 rounded-lg p-3">
                <p className="text-xs text-gray-400 mb-1">APY (JediSwap / Ekubo)</p>
                <p className="text-white font-semibold">
                  {marketSnapshot.loading
                    ? '...'
                    : `${marketSnapshot.data?.apys?.jediswap?.toFixed(2) ?? '—'}% / ${marketSnapshot.data?.apys?.ekubo?.toFixed(2) ?? '—'}%`}
                </p>
                <p className="text-[11px] text-gray-500 mt-1">
                  Source: {marketSnapshot.data?.apy_source ?? '—'}
                </p>
              </div>
              <div className="bg-slate-800/50 rounded-lg p-3">
                <p className="text-xs text-gray-400 mb-1">Network</p>
                <p className="text-white font-semibold">
                  {marketSnapshot.data?.network ?? '—'}
                </p>
                <p className="text-[11px] text-gray-500 mt-1">
                  {marketSnapshot.data?.block_hash ? `${marketSnapshot.data.block_hash.slice(0, 12)}...` : '—'}
                </p>
              </div>
            </div>
          </div>

          {/* Derived Metrics */}
          <div className="bg-slate-900/70 border border-white/10 rounded-xl p-6 shadow-lg">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-xl font-bold text-white">Derived Risk Inputs</h2>
                <p className="text-xs text-gray-400">Read‑only proxies (market → metrics)</p>
              </div>
              <button
                onClick={() => marketMetrics.refetch()}
                className="px-3 py-1.5 text-sm bg-gray-700 hover:bg-gray-600 text-white rounded transition-colors flex items-center gap-2"
              >
                🔄 Refresh
              </button>
            </div>

            {marketMetrics.error && (
              <div className="mb-3 text-sm text-red-400 bg-red-500/10 border border-red-500/30 rounded p-2">
                ⚠️ {marketMetrics.error}
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
              {(['jediswap', 'ekubo'] as const).map((protocol) => {
                const metrics = marketMetrics.data?.[protocol];
                return (
                  <div key={protocol} className="bg-slate-800/50 rounded-lg p-3">
                    <p className="text-xs text-gray-400 mb-1">{protocol.toUpperCase()}</p>
                    <p className="text-xs text-gray-300">
                      util: {metrics ? metrics.utilization : '—'} · vol: {metrics ? metrics.volatility : '—'}
                    </p>
                    <p className="text-xs text-gray-300">
                      liq: {metrics ? metrics.liquidity : '—'} · audit: {metrics ? metrics.audit_score : '—'}
                    </p>
                    <p className="text-[11px] text-gray-500 mt-1">
                      source: {metrics?.source ?? '—'} · apy: {metrics ? metrics.apy.toFixed(2) : '—'}%
                    </p>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Allocation Bar */}
          <div className="bg-slate-900/70 border border-white/10 rounded-xl p-6 shadow-lg">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-white">Current Allocation (On-Chain)</h2>
              <button
                onClick={() => {
                  console.log('🔄 Manual refresh triggered');
                  router.refetch();
                }}
                className="px-3 py-1.5 text-sm bg-gray-700 hover:bg-gray-600 text-white rounded transition-colors flex items-center gap-2"
                title="Refresh allocation from contract"
              >
                🔄 Refresh
              </button>
            </div>
            {router.error && (
              <div className="mb-2 text-sm text-red-400 bg-red-500/10 border border-red-500/30 rounded p-2">
                ⚠️ {router.error}
              </div>
            )}
            {router.lastUpdated && (
              <div className="mb-2 text-xs text-gray-400">
                Last updated: {router.lastUpdated.toLocaleTimeString()}
              </div>
            )}
            <div className="h-8 rounded-full overflow-hidden flex mb-4 bg-gray-800">
              <div className="bg-gradient-to-r from-blue-500 to-blue-600 flex items-center justify-center text-white text-sm font-bold" style={{ width: allocation.jediswap + '%' }}>
                {allocation.jediswap >= 15 && allocation.jediswap.toFixed(1) + '%'}
              </div>
              <div className="bg-gradient-to-r from-orange-500 to-orange-600 flex items-center justify-center text-white text-sm font-bold" style={{ width: allocation.ekubo + '%' }}>
                {allocation.ekubo >= 15 && allocation.ekubo.toFixed(1) + '%'}
              </div>
            </div>
            <div className="flex justify-center gap-8 mb-3">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded bg-blue-500"></div>
                <span className="text-gray-300">JediSwap: {allocation.jediswap.toFixed(2)}%</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded bg-orange-500"></div>
                <span className="text-gray-200">Ekubo: {allocation.ekubo.toFixed(2)}%</span>
              </div>
            </div>
            {latestDecision && Math.abs(allocation.jediswap - (latestDecision.jediswap_pct || 0) * 100) > 0.1 && (
              <div className="mt-3 p-3 bg-yellow-500/10 border border-yellow-500/30 rounded text-sm">
                <div className="text-yellow-400 font-semibold mb-1">📊 AI Proposed: JediSwap {((latestDecision.jediswap_pct || 0) * 100).toFixed(1)}% / Ekubo {((latestDecision.ekubo_pct || 0) * 100).toFixed(1)}%</div>
                <div className="text-yellow-300 text-xs mt-1">
                  ⚠️ On-chain allocation differs. Use "AI Risk Engine" button to update via RiskEngine.
                </div>
              </div>
            )}
          </div>

          {/* Pool Selection - Coming Soon */}
          <div className="bg-slate-900/70 border border-white/10 rounded-xl p-6 shadow-lg">
            <h2 className="text-xl font-bold text-white mb-4">Select Your Pool</h2>
            <p className="text-sm text-gray-400 mb-4">Choose a risk profile that matches your investment goals</p>
            <div className="text-center py-8">
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                <span className="text-blue-400">🚧</span>
                <span className="text-blue-300 text-sm">Pool selection feature coming soon</span>
              </div>
              <p className="text-gray-500 text-xs mt-4">
                For now, use the AI Risk Engine orchestration to automatically optimize allocations
              </p>
            </div>
          </div>

          {/* Deposit & Withdraw */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Deposit */}
            <div className="bg-gradient-to-br from-green-900/60 via-slate-900/70 to-slate-900/80 border border-green-400/30 rounded-xl p-6 shadow-lg">
              <div className="flex items-center gap-2 mb-4">
                <span className="text-2xl">💰</span>
                <h2 className="text-xl font-bold text-white">Deposit STRK</h2>
                <span className={`text-xs px-2 py-0.5 rounded-full ${
                  strategyDeposit.contractVersion === 'v2' 
                    ? 'bg-green-500/20 text-green-400' 
                    : strategyDeposit.contractVersion === 'v1'
                    ? 'bg-yellow-500/20 text-yellow-400'
                    : 'bg-gray-500/20 text-gray-400'
                }`}>
                  {strategyDeposit.contractVersion === 'v2' ? '✓ v3.5 Live' : strategyDeposit.contractVersion === 'v1' ? 'V1 (Allocation Only)' : 'Checking...'}
                </span>
              </div>
              
              {/* Status Messages */}
              {strategyDeposit.contractVersion === 'v1' && (
                <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-3 mb-4">
                  <p className="text-yellow-400 text-xs">
                    ⏳ <strong>v3.5 Deployment</strong> Current contract (V1) only manages allocations. 
                    v3.5 with deposits is deployed and ready.
                  </p>
                </div>
              )}
              
              {strategyDeposit.contractVersion === 'v2' && (
                <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-3 mb-4">
                  <p className="text-green-400 text-xs">
                    ✓ <strong>Direct Deposit</strong> — Your STRK goes directly to the Strategy Router.
                    <br/>
                    <span className="text-green-300/70">🔒 Optional privacy adapter coming soon.</span>
                  </p>
                </div>
              )}
              
              <p className="text-sm text-gray-300 mb-2">Deposit STRK to earn optimized yields across DeFi protocols</p>
              <div className="text-xs text-gray-400 mb-4 space-y-1">
                <div className="flex items-center justify-between">
                  <span>STRK Balance:</span>
                  <span className="font-mono text-green-400">
                    {strategyDeposit.isLoadingBalance ? '...' : `${strategyDeposit.userBalance.toFixed(4)} STRK`}
                  </span>
                </div>
                {strategyDeposit.strkBalance !== undefined && (
                  <div className="flex items-center justify-between">
                    <span>STRK Balance (gas):</span>
                    <span className={`font-mono ${strategyDeposit.strkBalance < 0.001 ? 'text-yellow-400' : 'text-green-400'}`}>
                      {strategyDeposit.isLoadingBalance ? '...' : `${strategyDeposit.strkBalance.toFixed(6)} STRK`}
                      {strategyDeposit.strkBalance < 0.001 && (
                        <span className="ml-2 text-xs">⚠️ Low!</span>
                      )}
                    </span>
                  </div>
                )}
              </div>
              <input
                type="number"
                value={depositAmount}
                onChange={(e) => {
                  const val = e.target.value;
                  // Only allow positive numbers
                  if (val === '' || (!isNaN(parseFloat(val)) && parseFloat(val) >= 0)) {
                    setDepositAmount(val);
                  }
                }}
                placeholder="0.0 STRK"
                step="0.01"
                min="0"
                max={strategyDeposit.userBalance}
                className="w-full p-3 mb-4 bg-slate-900/70 border border-green-500/30 rounded-lg text-white placeholder-gray-500"
              />
              
              {/* Show allocation preview when amount is entered */}
              {depositAmount && parseFloat(depositAmount) > 0 && (
                <DepositAllocationPreview
                  depositAmount={parseFloat(depositAmount)}
                  jediswapPct={allocation.jediswap}
                  ekuboPct={allocation.ekubo}
                  latestDecisionId={latestDecision?.decisionId}
                  proofHash={latestDecision?.proofHash}
                  latestRecommendation={latestDecision ? {
                    jediswap_pct: latestDecision.jediswap_pct || 0,
                    ekubo_pct: latestDecision.ekubo_pct || 0,
                  } : null}
                />
              )}
              
              <button
                onClick={handleDeposit}
                disabled={isDepositing || !depositAmount || parseFloat(depositAmount) <= 0 || strategyDeposit.contractVersion === 'v1'}
                className="w-full py-3 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white rounded-xl font-bold disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {isDepositing ? (
                  <><div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div> Processing...</>
                ) : (
                  '💰 Deposit STRK'
                )}
              </button>
            </div>

            {/* Withdraw */}
            <div className="bg-gradient-to-br from-rose-900/60 via-slate-900/70 to-slate-900/80 border border-rose-400/30 rounded-xl p-6 shadow-lg">
              <div className="flex items-center gap-2 mb-4">
                <span className="text-2xl">🏧</span>
                <h2 className="text-xl font-bold text-white">Withdraw STRK</h2>
                <span className={`text-xs px-2 py-0.5 rounded-full ${
                  strategyDeposit.contractVersion === 'v2' 
                    ? 'bg-green-500/20 text-green-400' 
                    : strategyDeposit.contractVersion === 'v1'
                    ? 'bg-yellow-500/20 text-yellow-400'
                    : 'bg-gray-500/20 text-gray-400'
                }`}>
                  {strategyDeposit.contractVersion === 'v2' ? '✓ v3.5 Live' : strategyDeposit.contractVersion === 'v1' ? 'V1 (Allocation Only)' : 'Checking...'}
                </span>
              </div>
              
              {/* Status Messages */}
              {strategyDeposit.contractVersion === 'v1' && (
                <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-3 mb-4">
                  <p className="text-yellow-400 text-xs">
                    ⏳ <strong>v3.5 Required</strong> Withdrawals require v3.5 contract deployment.
                  </p>
                </div>
              )}
              
              {strategyDeposit.contractVersion === 'v2' && (
                <div className="bg-rose-500/10 border border-rose-500/30 rounded-lg p-3 mb-4">
                  <p className="text-rose-300 text-xs">
                    ✓ <strong>Direct Withdrawal</strong> — Withdraw your STRK + accumulated yields.
                    <br/>
                  <span className="text-rose-300/70">🔒 Private withdrawals coming soon.</span>
                  </p>
                </div>
              )}
              
              <p className="text-sm text-gray-300 mb-2">Withdraw your deposited STRK + yields</p>
              <div className="text-xs text-gray-400 mb-4 flex items-center justify-between">
                <span>Your Deposits:</span>
                <span className="font-mono text-rose-400">
                  {strategyDeposit.isLoadingBalance ? '...' : `${strategyDeposit.contractBalance.toFixed(4)} STRK`}
                </span>
              </div>
              <input
                type="number"
                value={withdrawAmount}
                onChange={(e) => setWithdrawAmount(e.target.value)}
                placeholder="0.0 STRK"
                step="0.01"
                max={strategyDeposit.contractBalance}
                className="w-full p-3 mb-4 bg-slate-900/70 border border-red-500/30 rounded-lg text-white placeholder-gray-500"
              />
              <button
                onClick={handleWithdraw}
                disabled={isWithdrawing || !withdrawAmount || parseFloat(withdrawAmount) <= 0 || strategyDeposit.contractVersion === 'v1'}
                className="w-full py-3 bg-gradient-to-r from-red-500 to-rose-600 hover:from-red-600 hover:to-rose-700 text-white rounded-xl font-bold disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {isWithdrawing ? (
                  <><div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div> Processing...</>
                ) : (
                  '🏧 Withdraw STRK'
                )}
              </button>
            </div>
          </div>

          {/* Adjust Allocation */}
          <div className="bg-slate-900/70 border border-white/10 rounded-xl p-6 shadow-lg">
            <h2 className="text-xl font-bold text-white mb-4">Adjust Allocation</h2>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-blue-200">🔄 JediSwap</span>
                  <span className="text-white font-bold">{allocationForm.jediswap}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={allocationForm.jediswap}
                  onChange={(e) => handleSliderChange('jediswap', parseInt(e.target.value))}
                  className="w-full h-2 bg-gray-700 rounded-lg accent-blue-500"
                />
              </div>
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-orange-300">🌀 Ekubo</span>
                  <span className="text-white font-bold">{allocationForm.ekubo}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={allocationForm.ekubo}
                  onChange={(e) => handleSliderChange('ekubo', parseInt(e.target.value))}
                  className="w-full h-2 bg-gray-700 rounded-lg accent-orange-500"
                />
              </div>
              <div className="flex justify-between p-3 bg-gray-800/50 rounded-lg">
                <span className="text-gray-300">Total</span>
                <span className={`font-bold ${Math.abs((allocationForm.jediswap + allocationForm.ekubo) - 100) < 0.1 ? 'text-green-400' : 'text-red-400'}`}>
                  {allocationForm.jediswap + allocationForm.ekubo}%
                </span>
              </div>
              {settlementError && (
                <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3">
                  <p className="text-red-400 text-sm">⚠️ {settlementError}</p>
                </div>
              )}
              <button
                onClick={handleUpdateAllocation}
                disabled={isUpdating}
                className="w-full py-3 bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700 text-white rounded-xl font-bold disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {isUpdating ? (
                  <><div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div> Settling on-chain...</>
                ) : (
                  '🔄 Update Allocation'
                )}
              </button>
            </div>
          </div>

          {/* Risk Engine Calculation */}
          <div className="bg-gradient-to-br from-indigo-900/60 via-slate-900/70 to-slate-900/80 border border-indigo-400/30 rounded-xl p-6 shadow-lg">
            <div className="flex items-center gap-2 mb-4">
              <span className="text-2xl">🧠</span>
              <div>
                <h2 className="text-xl font-bold text-white">Verifiable AI Risk Engine</h2>
                <p className="text-xs text-indigo-300">Cairo-powered risk scoring on Starknet</p>
              </div>
            </div>
            <p className="text-sm text-gray-300 mb-4">
              AI Risk Engine orchestrates the full on-chain flow: calculates risk, queries APY, validates with DAO, and executes allocation. 100% auditable from computation to settlement.
            </p>
            
            <button
              onClick={handleAIOchestration}
              disabled={isCalculatingRisk || riskEngineOrchestration.isLoading}
              className="w-full py-3 bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white rounded-xl font-bold disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 mb-4"
            >
              {(isCalculatingRisk || riskEngineOrchestration.isLoading) ? (
                <><div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div> AI Orchestrating...</>
              ) : (
                '🤖 AI Risk Engine: Orchestrate Allocation'
              )}
            </button>

            <button
              onClick={handleMarketOrchestration}
              disabled={isCalculatingRisk || backendOrchestration.isLoading}
              className="w-full py-3 bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-600 hover:to-cyan-600 text-white rounded-xl font-bold disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 mb-4"
            >
              {(isCalculatingRisk || backendOrchestration.isLoading) ? (
                <><div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div> Using market data...</>
              ) : (
                '🌍 Orchestrate from Market Data (Read‑Only)'
              )}
            </button>

            {/* Risk Error Display */}
            {riskError && (
              <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 mb-4">
                <p className="text-red-400 text-sm">⚠️ {riskError}</p>
              </div>
            )}

            {/* Risk Calculation Results */}
            {riskEngine.lastAllocation && (
              <div className="space-y-3 pt-4 border-t border-indigo-400/20">
                <p className="text-xs text-indigo-300 font-semibold">ALLOCATION RESULTS (from Risk Engine)</p>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div className="bg-slate-800/50 rounded-lg p-3 text-center">
                    <p className="text-gray-400 text-xs mb-1">JediSwap</p>
                    <p className="text-indigo-300 font-bold">{(riskEngine.lastAllocation.jediswapPct / 100).toFixed(1)}%</p>
                  </div>
                  <div className="bg-slate-800/50 rounded-lg p-3 text-center">
                    <p className="text-gray-400 text-xs mb-1">Ekubo</p>
                    <p className="text-indigo-300 font-bold">{(riskEngine.lastAllocation.ekuboPct / 100).toFixed(1)}%</p>
                  </div>
                </div>
              </div>
            )}

            {/* Transaction Status */}
            {txStatus && (
              <div className="mt-4 pt-4 border-t border-indigo-400/20">
                <p className="text-xs text-indigo-300 font-semibold mb-2">CALCULATION STATUS</p>
                <p className="text-sm text-green-400">✅ Risk calculation confirmed on-chain</p>
              </div>
            )}
          </div>

          {/* Latest proof status (L2/L1) */}
          {latestProof && (
            <div className="bg-white/80 border border-white/70 rounded-3xl p-6 shadow-lift backdrop-blur">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <p className="text-xs uppercase tracking-[0.14em] text-slate-500">Latest proof</p>
                  <h3 className="font-display text-xl text-ink mt-1">On-chain verification</h3>
                  <p className="text-sm text-slate-600 mt-1">
                    {latestProof.proof_status} • TX {latestProof.tx_hash?.slice(0, 10) ?? '—'}...
                  </p>
                </div>
                <ProofBadge
                  hash={latestProof.proof_hash}
                  status={latestProof.proof_status as any}
                  txHash={latestProof.tx_hash}
                  factHash={latestProof.fact_hash}
                  l2FactHash={latestProof.l2_fact_hash}
                  l2VerifiedAt={latestProof.l2_verified_at}
                  l1FactHash={latestProof.l1_fact_hash}
                  l1VerifiedAt={latestProof.l1_verified_at}
                  network={latestProof.network}
                  submittedAt={latestProof.timestamp || undefined}
                  verifiedAt={latestProof.l2_verified_at || latestProof.l1_verified_at || undefined}
                />
              </div>
              <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-3 text-sm text-slate-700">
                <div className="bg-white/60 rounded-2xl p-3 border border-white/70">
                  <p className="text-xs text-slate-500 mb-1">Fact (L2)</p>
                  <p className="text-ink break-all text-xs">{latestProof.l2_fact_hash || latestProof.fact_hash || '—'}</p>
                  {latestProof.l2_verified_at && (
                    <p className="text-[11px] text-gray-500 mt-1">Verified {new Date(latestProof.l2_verified_at).toLocaleString()}</p>
                  )}
                </div>
                <div className="bg-white/60 rounded-2xl p-3 border border-white/70">
                  <p className="text-xs text-slate-500 mb-1">Fact (L1)</p>
                  <p className="text-ink break-all text-xs">{latestProof.l1_fact_hash || '—'}</p>
                  {latestProof.l1_verified_at && (
                    <p className="text-[11px] text-gray-500 mt-1">Verified {new Date(latestProof.l1_verified_at).toLocaleString()}</p>
                  )}
                </div>
                <div className="bg-white/60 rounded-2xl p-3 border border-white/70">
                  <p className="text-xs text-slate-500 mb-1">Network</p>
                  <p className="text-ink text-sm">{latestProof.network || 'sepolia'}</p>
                </div>
              </div>
              {proofHistory.error && (
                <p className="text-xs text-red-500 mt-3">History load failed: {proofHistory.error}</p>
              )}
            </div>
          )}

          {/* Rebalance History with Proofs */}
          <div className="bg-gradient-to-br from-slate-900/70 via-purple-900/20 to-slate-900/70 border border-purple-400/30 rounded-xl p-6 shadow-lg">
            <RebalanceHistory />
          </div>

          {/* Error */}
          {router.error && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4">
              <p className="text-red-400 text-sm">⚠️ {router.error}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
