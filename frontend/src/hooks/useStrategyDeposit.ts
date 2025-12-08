import { useState, useCallback } from 'react';
import { useAccount } from '@starknet-react/core';
import { Contract, RpcProvider, uint256 } from 'starknet';
import { getConfig } from '@/lib/config';

// Simplified ABI for STRK token (ERC20)
const STRK_TOKEN_ABI = [
  {
    name: 'balanceOf',
    type: 'function',
    inputs: [{ name: 'account', type: 'core::starknet::contract_address::ContractAddress' }],
    outputs: [{ type: 'core::integer::u256' }],
    state_mutability: 'view',
  },
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
    name: 'transfer',
    type: 'function',
    inputs: [
      { name: 'recipient', type: 'core::starknet::contract_address::ContractAddress' },
      { name: 'amount', type: 'core::integer::u256' },
    ],
    outputs: [{ type: 'core::bool' }],
    state_mutability: 'external',
  },
];

// Strategy Router V2 ABI (with deposit/withdraw functions)
const STRATEGY_ROUTER_V2_ABI = [
  {
    name: 'deposit',
    type: 'function',
    inputs: [{ name: 'amount', type: 'core::integer::u256' }],
    outputs: [],
    state_mutability: 'external',
  },
  {
    name: 'withdraw',
    type: 'function',
    inputs: [{ name: 'amount', type: 'core::integer::u256' }],
    outputs: [{ type: 'core::integer::u256' }],
    state_mutability: 'external',
  },
  {
    name: 'get_user_balance',
    type: 'function',
    inputs: [{ name: 'user', type: 'core::starknet::contract_address::ContractAddress' }],
    outputs: [{ type: 'core::integer::u256' }],
    state_mutability: 'view',
  },
  {
    name: 'get_total_value_locked',
    type: 'function',
    inputs: [],
    outputs: [{ type: 'core::integer::u256' }],
    state_mutability: 'view',
  },
];

const STRK_TOKEN_ADDRESS = '0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d'; // Sepolia STRK

export function useStrategyDeposit(strategyRouterAddress: string) {
  const { account, address } = useAccount();
  const config = getConfig();
  const [userBalance, setUserBalance] = useState<number>(0); // User's STRK wallet balance
  const [contractBalance, setContractBalance] = useState<number>(0); // User's deposited balance in Strategy Router
  const [isLoadingBalance, setIsLoadingBalance] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [contractVersion, setContractVersion] = useState<'v1' | 'v2' | 'unknown'>('unknown');

  const provider = new RpcProvider({ nodeUrl: config.rpcUrl });

  // Check if contract has deposit function (V2)
  const checkContractVersion = useCallback(async () => {
    if (!strategyRouterAddress || strategyRouterAddress === '0x0') {
      setContractVersion('unknown');
      return;
    }

    try {
      // Try to get class and check for deposit function
      const classAt = await provider.getClassAt(strategyRouterAddress);
      const abiStr = JSON.stringify(classAt.abi || []);
      
      if (abiStr.includes('"deposit"')) {
        setContractVersion('v2');
        console.log('📋 Strategy Router V2 detected (with deposit/withdraw)');
      } else {
        setContractVersion('v1');
        console.log('📋 Strategy Router V1 detected (allocation only, no deposit/withdraw)');
      }
    } catch (error) {
      console.warn('Could not detect contract version:', error);
      setContractVersion('unknown');
    }
  }, [strategyRouterAddress, provider]);

  // Fetch user's STRK balance
  const fetchBalance = useCallback(async () => {
    if (!address) {
      setUserBalance(0);
      setContractBalance(0);
      return;
    }

    setIsLoadingBalance(true);

    try {
      // Check contract version first
      await checkContractVersion();

      // Fetch STRK wallet balance
      const strkContract = new Contract(STRK_TOKEN_ABI, STRK_TOKEN_ADDRESS, provider);
      const balanceResult = await strkContract.balanceOf(address);
      
      // Handle different response formats
      let balanceValue: bigint;
      if (typeof balanceResult === 'bigint') {
        balanceValue = balanceResult;
      } else if (balanceResult?.balance) {
        balanceValue = BigInt(balanceResult.balance.low || balanceResult.balance || 0);
      } else if (balanceResult?.low !== undefined) {
        balanceValue = BigInt(balanceResult.low);
      } else {
        balanceValue = BigInt(balanceResult || 0);
      }
      
      setUserBalance(Number(balanceValue) / 1e18);
      console.log('💰 STRK wallet balance:', Number(balanceValue) / 1e18);

      // Only try to fetch contract balance if V2 is detected
      if (contractVersion === 'v2' && strategyRouterAddress && strategyRouterAddress !== '0x0') {
        try {
          const routerContract = new Contract(STRATEGY_ROUTER_V2_ABI, strategyRouterAddress, provider);
          const depositedResult = await routerContract.get_user_balance(address);
          const deposited = BigInt(depositedResult || 0);
          setContractBalance(Number(deposited) / 1e18);
        } catch (error) {
          console.warn('Could not fetch contract balance (V1 contract):', error);
          setContractBalance(0);
        }
      } else {
        setContractBalance(0);
      }
    } catch (error) {
      console.error('Failed to fetch balance:', error);
      setUserBalance(0);
      setContractBalance(0);
    } finally {
      setIsLoadingBalance(false);
    }
  }, [address, provider, strategyRouterAddress, checkContractVersion, contractVersion]);

  // Deposit STRK to Strategy Router
  const deposit = useCallback(
    async (amount: number): Promise<string | null> => {
      if (!account || !address) {
        throw new Error('Wallet not connected');
      }

      if (!strategyRouterAddress || strategyRouterAddress === '0x0' || strategyRouterAddress === '') {
        throw new Error('Strategy Router address not configured');
      }

      // Check if contract version supports deposits
      if (contractVersion === 'v1') {
        throw new Error(
          'The deployed Strategy Router (V1) does not support deposits yet. ' +
          'Please wait for Strategy Router V2 to be deployed, or use Demo Mode to test the UI.'
        );
      }

      setIsLoading(true);

      try {
        // Convert amount to u256 format using starknet.js helper
        const amountWei = BigInt(Math.floor(amount * 1e18));
        const amountU256 = uint256.bnToUint256(amountWei);

        // Step 1: Approve STRK token for Strategy Router
        console.log('📝 Step 1: Approving STRK token...');
        const strkContract = new Contract(STRK_TOKEN_ABI, STRK_TOKEN_ADDRESS, provider);
        strkContract.connect(account);

        const approveCall = strkContract.populate('approve', [
          strategyRouterAddress,
          amountU256,
        ]);

        const approveTx = await account.execute([approveCall]);
        console.log('✅ Approve tx:', approveTx.transaction_hash);

        // Wait for approval to be confirmed
        await provider.waitForTransaction(approveTx.transaction_hash);
        console.log('✅ Approval confirmed');

        // Step 2: Deposit to Strategy Router
        console.log('📝 Step 2: Depositing to Strategy Router...');
        const routerContract = new Contract(STRATEGY_ROUTER_V2_ABI, strategyRouterAddress, provider);
        routerContract.connect(account);

        const depositCall = routerContract.populate('deposit', [amountU256]);

        const depositTx = await account.execute([depositCall]);
        console.log('✅ Deposit tx:', depositTx.transaction_hash);

        // Refresh balance after deposit
        await provider.waitForTransaction(depositTx.transaction_hash);
        await fetchBalance();

        return depositTx.transaction_hash;
      } catch (error: any) {
        console.error('Deposit error:', error);
        throw new Error(error.message || 'Deposit failed');
      } finally {
        setIsLoading(false);
      }
    },
    [account, address, provider, strategyRouterAddress, fetchBalance, contractVersion]
  );

  // Withdraw STRK from Strategy Router
  const withdraw = useCallback(
    async (amount: number): Promise<string | null> => {
      if (!account || !address) {
        throw new Error('Wallet not connected');
      }

      if (!strategyRouterAddress || strategyRouterAddress === '0x0' || strategyRouterAddress === '') {
        throw new Error('Strategy Router address not configured');
      }

      // Check if contract version supports withdrawals
      if (contractVersion === 'v1') {
        throw new Error(
          'The deployed Strategy Router (V1) does not support withdrawals yet. ' +
          'Please wait for Strategy Router V2 to be deployed, or use Demo Mode to test the UI.'
        );
      }

      setIsLoading(true);

      try {
        // Convert amount to u256 format
        const amountWei = BigInt(Math.floor(amount * 1e18));
        const amountU256 = uint256.bnToUint256(amountWei);

        const routerContract = new Contract(STRATEGY_ROUTER_V2_ABI, strategyRouterAddress, provider);
        routerContract.connect(account);

        const withdrawCall = routerContract.populate('withdraw', [amountU256]);

        const withdrawTx = await account.execute([withdrawCall]);
        console.log('✅ Withdraw tx:', withdrawTx.transaction_hash);

        // Refresh balance after withdrawal
        await provider.waitForTransaction(withdrawTx.transaction_hash);
        await fetchBalance();

        return withdrawTx.transaction_hash;
      } catch (error: any) {
        console.error('Withdrawal error:', error);
        throw new Error(error.message || 'Withdrawal failed');
      } finally {
        setIsLoading(false);
      }
    },
    [account, address, provider, strategyRouterAddress, fetchBalance, contractVersion]
  );

  return {
    userBalance,
    contractBalance,
    isLoadingBalance,
    isLoading,
    fetchBalance,
    deposit,
    withdraw,
    contractVersion,
    isReady: !!account && !!strategyRouterAddress && strategyRouterAddress !== '0x0',
    // V2 is only ready if contract actually supports deposits
    isV2Ready: !!account && !!strategyRouterAddress && strategyRouterAddress !== '0x0' && contractVersion === 'v2',
  };
}
