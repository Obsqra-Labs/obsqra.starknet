'use client';

import { useAccount } from '@starknet-react/core';
import { Contract, RpcProvider, uint256, AccountInterface, Call } from 'starknet';
import { getConfig } from '@/lib/config';
import { useState } from 'react';

// Protocol addresses (Sepolia)
const JEDISWAP_NFT_MANAGER = '0x024fd9721eea36cf8cebc226fd9414057bbf895b47739822f849f622029f9399';
const EKUBO_CORE = '0x0444a09d96389aa7148f1aada508e30b71299ffe650d9c97fdaae38cb9a23384';
const STRK_TOKEN = '0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d';
const ETH_TOKEN = '0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7';
const STRATEGY_ROUTER = '0x00a7ab889739eeb5ab99c68abe062bec7f8adcece85633c2f6977659e9f3d29a';

// ERC20 ABI
const ERC20_ABI = [
  {
    name: 'approve',
    type: 'function',
    inputs: [
      { name: 'spender', type: 'core::starknet::contract_address::ContractAddress' },
      { name: 'amount', type: 'core::integer::u256' },
    ],
    outputs: [{ type: 'core::bool' }],
    state_mutability: 'external',
  },
  {
    name: 'balanceOf',
    type: 'function',
    inputs: [{ name: 'account', type: 'core::starknet::contract_address::ContractAddress' }],
    outputs: [{ type: 'core::integer::u256' }],
    state_mutability: 'view',
  },
];

export function ProtocolTester() {
  const { account, address } = useAccount();
  const config = getConfig();
  const [testingJediSwap, setTestingJediSwap] = useState(false);
  const [testingEkubo, setTestingEkubo] = useState(false);
  const [testAmount, setTestAmount] = useState('1'); // Default 1 STRK
  const [testResult, setTestResult] = useState<string | null>(null);
  const [testError, setTestError] = useState<string | null>(null);

  const provider = new RpcProvider({ nodeUrl: config.rpcUrl });

  // Test JediSwap liquidity addition
  const testJediSwap = async () => {
    if (!account || !address) {
      setTestError('Wallet not connected');
      return;
    }

    setTestingJediSwap(true);
    setTestError(null);
    setTestResult(null);

    try {
      const amountWei = BigInt(Math.floor(parseFloat(testAmount) * 1e18));
      const amountU256 = uint256.bnToUint256(amountWei);

      // Step 1: Approve NFT Manager to spend STRK from Strategy Router
      const strkContract = new Contract(ERC20_ABI, STRK_TOKEN, provider);
      strkContract.connect(account);

      const maxApproval = uint256.bnToUint256(BigInt('0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'));
      const approveCall = strkContract.populate('approve', [JEDISWAP_NFT_MANAGER, maxApproval]);

      console.log('🔍 Testing JediSwap...');
      console.log('  Approving NFT Manager to spend STRK...');

      const approveTx = await account.execute([approveCall]);
      await provider.waitForTransaction(approveTx.transaction_hash);
      console.log('  ✅ Approved');

      // Step 2: Call mint() on NFT Manager
      // Note: This is simplified - you'll need the full JediSwap NFT Manager ABI
      // For now, this is a template showing the approach

      setTestResult(`✅ JediSwap test initiated! Transaction: ${approveTx.transaction_hash}`);
      setTestResult((prev) => prev + '\n⚠️ Note: Full mint() call needs JediSwap NFT Manager ABI');

    } catch (error: any) {
      console.error('JediSwap test error:', error);
      setTestError(error.message || 'JediSwap test failed');
    } finally {
      setTestingJediSwap(false);
    }
  };

  // Test Ekubo liquidity deposit
  const testEkubo = async () => {
    if (!account || !address) {
      setTestError('Wallet not connected');
      return;
    }

    setTestingEkubo(true);
    setTestError(null);
    setTestResult(null);

    try {
      const amountWei = BigInt(Math.floor(parseFloat(testAmount) * 1e18));
      const amountU256 = uint256.bnToUint256(amountWei);

      // Step 1: Approve Ekubo Core to spend STRK from Strategy Router
      const strkContract = new Contract(ERC20_ABI, STRK_TOKEN, provider);
      strkContract.connect(account);

      const maxApproval = uint256.bnToUint256(BigInt('0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'));
      const approveCall = strkContract.populate('approve', [EKUBO_CORE, maxApproval]);

      console.log('🔍 Testing Ekubo...');
      console.log('  Approving Ekubo Core to spend STRK...');

      const approveTx = await account.execute([approveCall]);
      await provider.waitForTransaction(approveTx.transaction_hash);
      console.log('  ✅ Approved');

      // Step 2: Call deposit_liquidity() on Ekubo Core
      // Note: This is simplified - you'll need the full Ekubo Core ABI
      // For now, this is a template showing the approach

      setTestResult(`✅ Ekubo test initiated! Transaction: ${approveTx.transaction_hash}`);
      setTestResult((prev) => prev + '\n⚠️ Note: Full deposit_liquidity() call needs Ekubo Core ABI');

    } catch (error: any) {
      console.error('Ekubo test error:', error);
      setTestError(error.message || 'Ekubo test failed');
    } finally {
      setTestingEkubo(false);
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6 mb-6">
      <h2 className="text-2xl font-bold mb-4">🧪 Protocol Testing (Individual)</h2>
      <p className="text-gray-400 mb-4">
        Test each protocol individually before integrating into Strategy Router
      </p>

      <div className="mb-4">
        <label className="block text-sm font-medium mb-2">Test Amount (STRK)</label>
        <input
          type="number"
          value={testAmount}
          onChange={(e) => setTestAmount(e.target.value)}
          className="w-full px-4 py-2 bg-gray-700 rounded text-white"
          placeholder="1.0"
          step="0.1"
          min="0.1"
        />
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <button
          onClick={testJediSwap}
          disabled={testingJediSwap || !account}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {testingJediSwap ? 'Testing...' : '🧪 Test JediSwap'}
        </button>

        <button
          onClick={testEkubo}
          disabled={testingEkubo || !account}
          className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {testingEkubo ? 'Testing...' : '🧪 Test Ekubo'}
        </button>
      </div>

      {testResult && (
        <div className="mt-4 p-4 bg-green-900/30 rounded">
          <pre className="text-sm text-green-400 whitespace-pre-wrap">{testResult}</pre>
        </div>
      )}

      {testError && (
        <div className="mt-4 p-4 bg-red-900/30 rounded">
          <pre className="text-sm text-red-400 whitespace-pre-wrap">{testError}</pre>
        </div>
      )}

      <div className="mt-4 text-sm text-gray-400">
        <p>📋 Contract with STRK: {STRATEGY_ROUTER}</p>
        <p>💡 These tests approve protocols to spend STRK from the Strategy Router contract</p>
      </div>
    </div>
  );
}

