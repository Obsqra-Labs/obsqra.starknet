import { useState, useCallback, useEffect, useMemo, useRef } from 'react';
import { useAccount } from '@starknet-react/core';
import { Contract, RpcProvider, uint256, AccountInterface, Call, hash } from 'starknet';
import { getConfig } from '@/lib/config';

// Simplified ABI for STRK token (ERC20) - Users deposit STRK
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
  {
    name: 'allowance',
    type: 'function',
    inputs: [
      { name: 'owner', type: 'core::starknet::contract_address::ContractAddress' },
      { name: 'spender', type: 'core::starknet::contract_address::ContractAddress' },
    ],
    outputs: [{ type: 'core::integer::u256' }],
    state_mutability: 'view',
  },
];

// Strategy Router V3.5 ABI (minimal - only deposit/withdraw/get_user_balance needed here)
const STRATEGY_ROUTER_V35_ABI = [
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

// STRK token address on Starknet Sepolia (users deposit STRK - THIS WORKS!)
const STRK_TOKEN_ADDRESS = '0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d'; // Sepolia STRK

export function useStrategyDeposit(strategyRouterAddress: string) {
  const { account, address } = useAccount();
  const config = getConfig();
  const [userBalance, setUserBalance] = useState<number>(0); // User's STRK wallet balance
  const [contractBalance, setContractBalance] = useState<number>(0); // User's deposited balance in Strategy Router
  const [strkBalance, setStrkBalance] = useState<number>(0); // User's STRK balance (same as userBalance, kept for compatibility)
  const [isLoadingBalance, setIsLoadingBalance] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [contractVersion, setContractVersion] = useState<'v1' | 'v2' | 'unknown'>('unknown');
  const checkingVersionRef = useRef(false); // Prevent multiple simultaneous version checks

  // Memoize provider to prevent recreation on every render
  const provider = useMemo(() => new RpcProvider({ nodeUrl: config.rpcUrl }), [config.rpcUrl]);

  // Check if contract has deposit function (V2)
  const checkContractVersion = useCallback(async () => {
    if (!strategyRouterAddress || strategyRouterAddress === '0x0') {
      setContractVersion('unknown');
      return;
    }

    // Prevent multiple simultaneous checks
    if (checkingVersionRef.current) {
      return;
    }

    checkingVersionRef.current = true;
    try {
      // Try to get class and check for deposit function
      const classAt = await provider.getClassAt(strategyRouterAddress);
      const abiStr = JSON.stringify(classAt.abi || []);
      
      if (abiStr.includes('"deposit"')) {
        setContractVersion('v2');
        console.log('📋 Strategy Router v3.5 detected (with deposit/withdraw)');
      } else {
        setContractVersion('v1');
        console.log('📋 Strategy Router V1 detected (allocation only, no deposit/withdraw)');
      }
    } catch (error) {
      console.warn('Could not detect contract version:', error);
      setContractVersion('unknown');
    } finally {
      checkingVersionRef.current = false;
    }
  }, [strategyRouterAddress, provider]);

  // Fetch user's STRK balance
  const fetchBalance = useCallback(async () => {
    if (!address) {
      setUserBalance(0);
      setContractBalance(0);
      setStrkBalance(0);
      return;
    }

    setIsLoadingBalance(true);

    try {
      // Fetch STRK wallet balance (users deposit STRK)
      const strkContract = new Contract(STRK_TOKEN_ABI, STRK_TOKEN_ADDRESS, provider);
      const balanceResult = await strkContract.balanceOf(address);
      
      // Handle different response formats (including u256 with low/high)
      let balanceValue: bigint;
      if (typeof balanceResult === 'bigint') {
        balanceValue = balanceResult;
      } else if (balanceResult?.balance) {
        // Handle nested balance object
        const bal = balanceResult.balance;
        if (bal.low !== undefined && bal.high !== undefined) {
          balanceValue = BigInt(bal.low || 0) + (BigInt(bal.high || 0) << 128n);
        } else {
          balanceValue = BigInt(bal || 0);
        }
      } else if (balanceResult?.low !== undefined) {
        // Handle u256 format (low + high)
        const low = BigInt(balanceResult.low || 0);
        const high = BigInt(balanceResult.high || 0);
        balanceValue = low + (high << 128n);
      } else {
        balanceValue = BigInt(balanceResult || 0);
      }
      
      const newBalance = Number(balanceValue) / 1e18;
      setUserBalance((prev) => {
        // Only log if balance actually changed
        if (prev !== newBalance) {
          console.log('💰 STRK wallet balance:', newBalance);
        }
        return newBalance;
      });
      setStrkBalance(newBalance); // Same as userBalance for STRK

      // Only try to fetch contract balance if V2 is detected
      // Use current state value, but don't depend on it in the callback
      if (contractVersion === 'v2' && strategyRouterAddress && strategyRouterAddress !== '0x0') {
        try {
          const routerContract = new Contract(STRATEGY_ROUTER_V35_ABI, strategyRouterAddress, provider);
          const depositedResult = await routerContract.get_user_balance(address);
          
          // Parse u256 result (can be string, number, or {low, high} object)
          let deposited: bigint;
          if (typeof depositedResult === 'string' || typeof depositedResult === 'number') {
            deposited = BigInt(depositedResult || 0);
          } else if (depositedResult && typeof depositedResult === 'object') {
            // Handle u256 format: {low: string, high: string} or nested structure
            if (depositedResult.low !== undefined && depositedResult.high !== undefined) {
              const low = BigInt(String(depositedResult.low || 0));
              const high = BigInt(String(depositedResult.high || 0));
              deposited = low + (high << 128n);
            } else if (depositedResult.balance) {
              // Handle nested balance object
              const bal = depositedResult.balance;
              if (bal.low !== undefined && bal.high !== undefined) {
                deposited = BigInt(String(bal.low || 0)) + (BigInt(String(bal.high || 0)) << 128n);
              } else {
                deposited = BigInt(String(bal || 0));
              }
            } else {
              deposited = BigInt(String(depositedResult || 0));
            }
          } else {
            deposited = BigInt(0);
          }
          
          const balanceNum = Number(deposited) / 1e18;
          setContractBalance(balanceNum);
          console.log(`📊 Contract balance (deposited): ${balanceNum.toFixed(6)} STRK`);
        } catch (error: any) {
          console.warn('Could not fetch contract balance:', error?.message || error);
          setContractBalance(0);
        }
      } else {
        setContractBalance(0);
      }
    } catch (error) {
      console.error('Failed to fetch balance:', error);
      setUserBalance(0);
      setContractBalance(0);
      setStrkBalance(0);
    } finally {
      setIsLoadingBalance(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [address, provider, strategyRouterAddress]); // Removed contractVersion and checkContractVersion to prevent infinite loop

  // Deposit STRK to Strategy Router
  const deposit = useCallback(
    async (amount: number): Promise<string | null> => {
      if (!account || !address || !strategyRouterAddress) {
        throw new Error('Wallet not connected or Strategy Router not configured');
      }

      setIsLoading(true);

      try {
        // Convert amount to u256
        const amountWei = BigInt(Math.floor(amount * 1e18));
        const amountU256 = uint256.bnToUint256(amountWei);
        
        // Check allowance and approve if needed
        const strkContract = new Contract(STRK_TOKEN_ABI, STRK_TOKEN_ADDRESS, provider);
        strkContract.connect(account);
        const allowance = await strkContract.allowance(address, strategyRouterAddress);
        const allowanceValue = typeof allowance === 'bigint' 
          ? allowance 
          : BigInt(allowance?.low || 0) + (BigInt(allowance?.high || 0) << 128n);

        if (allowanceValue < amountWei) {
          const maxApproval = uint256.bnToUint256(BigInt('0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'));
          const approveCall = strkContract.populate('approve', [strategyRouterAddress, maxApproval]);
        const approveTx = await account.execute([approveCall]);
        await provider.waitForTransaction(approveTx.transaction_hash);
        }

        // Deposit - verify contract first
        const routerContract = new Contract(STRATEGY_ROUTER_V35_ABI, strategyRouterAddress, provider);
        
        // Verify contract has deposit function by checking class
        try {
          const contractClass = await provider.getClassAt(strategyRouterAddress);
          const hasDeposit = contractClass?.abi?.some((item: any) => 
            item.name === 'deposit' && item.type === 'function'
          );
          if (!hasDeposit) {
            throw new Error(
              `❌ Contract at ${strategyRouterAddress} does not have a 'deposit' function.\n` +
              `This contract may be V1 or incorrectly deployed. Please check the deployment.`
            );
          }
        } catch (verifyError: any) {
          console.warn('Could not verify contract class:', verifyError);
          // Continue anyway - the execute will fail with a clearer error
        }
        
        routerContract.connect(account);
        
        // According to starknet.js docs, we can pass BigInt directly to populate()
        // populate() will automatically convert BigInt to u256 calldata format [low, high]
        // This is simpler and more reliable than using uint256.bnToUint256()
        const depositCall = routerContract.populate('deposit', [amountWei]);
        
        // Debug: Log the exact call being made
        console.log('🔍 Deposit call details:');
        console.log('  Contract:', depositCall.contractAddress);
        console.log('  Entrypoint:', depositCall.entrypoint);
        console.log('  Calldata:', depositCall.calldata);
        console.log('  amountU256:', amountU256);
        console.log('  amountU256.low:', amountU256.low.toString());
        console.log('  amountU256.high:', amountU256.high.toString());
        if (Array.isArray(depositCall.calldata)) {
          console.log('  Calldata length:', depositCall.calldata.length);
          console.log('  Calldata values:', depositCall.calldata);
          console.log('  Calldata types:', depositCall.calldata.map((c: any) => typeof c));
        }
        
        const depositTx = await account.execute([depositCall]);
        const receipt = await provider.waitForTransaction(depositTx.transaction_hash);
        
        // Track gas fees (non-blocking - don't fail deposit if fee extraction fails)
        try {
          const actualFee = (receipt as any).actual_fee;
          if (actualFee) {
            // Handle both string and U256 object formats
            let gasFeeWei: bigint;
            if (typeof actualFee === 'string') {
              gasFeeWei = BigInt(actualFee);
            } else if (actualFee && typeof actualFee === 'object') {
              // Handle new format: { amount: string; unit: "WEI" | "FRI" }
              if (actualFee.amount !== undefined) {
                gasFeeWei = BigInt(actualFee.amount);
              } else if (actualFee.low !== undefined && actualFee.high !== undefined) {
                // Handle old U256 format: {low: string, high: string}
                const low = BigInt(String(actualFee.low));
                const high = BigInt(String(actualFee.high));
                gasFeeWei = low + (high * BigInt(2 ** 128));
              } else {
                // Fallback: try to convert to string first
                gasFeeWei = BigInt(String(actualFee));
              }
            } else {
              // Fallback: try to convert to string first
              gasFeeWei = BigInt(String(actualFee));
            }
            const gasFeeStrk = Number(gasFeeWei) / 1e18;
            console.log(`💰 Deposit gas fee: ${gasFeeStrk.toFixed(6)} STRK (${gasFeeWei.toString()} wei)`);
          }
        } catch (feeError: any) {
          // Don't fail the deposit if gas fee extraction fails
          console.warn('⚠️ Could not extract gas fee from receipt:', feeError.message);
        }
        
        // Wait a bit for state to update, then refresh balance
        await new Promise(resolve => setTimeout(resolve, 1000));
        await fetchBalance();

        return depositTx.transaction_hash;
      } catch (error: any) {
        console.error('Deposit error:', error);
        console.error('Error details:', {
          message: error.message,
          code: error.code,
          name: error.name,
          stack: error.stack?.substring(0, 500),
        });
        
        const errorMsg = error.message || error.toString();
        const errorStr = error.toString();
        
        // Check if it's an Unauthorized error - deposit shouldn't have auth checks!
        if (errorMsg.includes('Unauthorized') || errorStr.includes('Unauthorized')) {
          throw new Error(
            `❌ Unauthorized: The deposit function failed with an authorization error.\n\n` +
            `This is unexpected - the deposit function should be open to all users.\n\n` +
            `Possible causes:\n` +
            `1. The contract may have been updated with authorization checks\n` +
            `2. There may be an issue with the ERC20 transfer_from call\n` +
            `3. The contract address may be incorrect\n\n` +
            `Contract: ${strategyRouterAddress}\n` +
            `Please check the contract deployment and verify the address is correct.`
          );
        }
        
        // Check if it's an ENTRYPOINT_NOT_FOUND error (most critical)
        if (errorMsg.includes('ENTRYPOINT_NOT_FOUND') || errorStr.includes('ENTRYPOINT_NOT_FOUND')) {
          throw new Error(
            `❌ ENTRYPOINT_NOT_FOUND: The Strategy Router contract doesn't recognize the 'deposit' function.\n\n` +
            `Contract: ${strategyRouterAddress}\n` +
            `This could mean:\n` +
            `1. The contract address is wrong or points to a V1 contract (which doesn't have deposit)\n` +
            `2. The account connection is stale - try disconnecting and reconnecting your wallet\n` +
            `3. The contract was not properly deployed\n\n` +
            `Please verify the contract address and try disconnecting/reconnecting your wallet.`
          );
        }
        
        // Check if it's a USER_REFUSED_OP error
        if (errorMsg.includes('USER_REFUSED_OP') || errorStr.includes('USER_REFUSED_OP')) {
          throw new Error(
            `❌ Transaction was refused by your wallet.\n\n` +
            `This usually means:\n` +
            `1. You clicked "Reject" in the wallet popup\n` +
            `2. The wallet detected an invalid transaction\n` +
            `3. The account connection is stale - try disconnecting and reconnecting\n\n` +
            `Please try disconnecting and reconnecting your wallet, then try again.`
          );
        }
        
        // Check if it's a gas/STRK issue
        if (errorMsg.includes('u256_sub') || errorMsg.includes('Overflow') || errorMsg.includes('argent/multicall-failed')) {
          console.error('❌ Transaction failed with u256_sub Overflow (from Argent account contract)');
          console.error('💡 This means your Argent wallet tried to pay gas fees but failed.');
          console.error('💡 Most likely cause: Insufficient STRK for gas fees');
          console.error('');
          console.error('🔧 How to fix:');
          console.error('   1. Open your Argent X wallet');
          console.error('   2. Make sure you\'re on Starknet Sepolia testnet');
          console.error('   3. Check your STRK balance (should show in wallet)');
          console.error('   4. If STRK balance is low or zero, get more from:');
          console.error('      - https://starknet-faucet.vercel.app/');
          console.error('      - https://www.alchemy.com/faucets/starknet-sepolia');
          console.error('      - https://sepolia-faucet.starknet.io/');
          console.error('');
          console.error('💡 You need at least 0.001 STRK for a single transaction');
          console.error('💡 Recommended: Get 0.01 STRK to have buffer for multiple transactions');
          
          // Try to get current STRK balance for error message (optional - may fail if contract doesn't exist)
          let currentStrk = 0;
          let strkCheckFailed = false;
          try {
            const strkContract = new Contract(STRK_TOKEN_ABI, STRK_TOKEN_ADDRESS, provider);
            const strkResult = await strkContract.balanceOf(address);
            if (typeof strkResult === 'bigint') {
              currentStrk = Number(strkResult) / 1e18;
            } else if (strkResult?.low !== undefined) {
              const low = BigInt(strkResult.low || 0);
              const high = BigInt(strkResult.high || 0);
              currentStrk = Number(low + (high << 128n)) / 1e18;
            }
          } catch (e) {
            strkCheckFailed = true;
            console.warn('Could not check STRK balance for error message:', e);
          }
          
          if (!strkCheckFailed && currentStrk > 0) {
            throw new Error(
              `❌ Transaction failed: Insufficient STRK for gas fees.\n\n` +
              `Your STRK balance: ${currentStrk.toFixed(6)} STRK\n` +
              `You need at least 0.001 STRK for gas fees.\n\n` +
              `Get STRK from:\n` +
              `• https://starknet-faucet.vercel.app/\n` +
              `• https://www.alchemy.com/faucets/starknet-sepolia\n` +
              `• https://sepolia-faucet.starknet.io/`
            );
          } else {
            throw new Error(
              `❌ Transaction failed: Insufficient STRK for gas fees.\n\n` +
              `The error "u256_sub Overflow" from your Argent wallet means you don't have enough STRK to pay for gas.\n\n` +
              `Get STRK from:\n` +
              `• https://starknet-faucet.vercel.app/\n` +
              `• https://www.alchemy.com/faucets/starknet-sepolia\n` +
              `• https://sepolia-faucet.starknet.io/\n\n` +
              `You need at least 0.001 STRK for a single transaction.`
            );
          }
        }
        
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
          'Please wait for Strategy Router v3.5 to be deployed, or use Demo Mode to test the UI.'
        );
      }

      setIsLoading(true);

      try {
        // Convert amount to u256 format
        const amountWei = BigInt(Math.floor(amount * 1e18));
        const amountU256 = uint256.bnToUint256(amountWei);

        const routerContract = new Contract(STRATEGY_ROUTER_V35_ABI, strategyRouterAddress, provider);
        routerContract.connect(account);

        const withdrawCall = routerContract.populate('withdraw', [amountU256]);

        const withdrawTx = await account.execute([withdrawCall]);
        console.log('✅ Withdraw tx:', withdrawTx.transaction_hash);

        // Refresh balance after withdrawal
        const receipt = await provider.waitForTransaction(withdrawTx.transaction_hash);
        
        // Track gas fees (non-blocking - don't fail withdraw if fee extraction fails)
        try {
          const actualFee = (receipt as any).actual_fee;
          if (actualFee) {
            // Handle both string and U256 object formats
            let gasFeeWei: bigint;
            if (typeof actualFee === 'string') {
              gasFeeWei = BigInt(actualFee);
            } else if (actualFee && typeof actualFee === 'object') {
              // Handle new format: { amount: string; unit: "WEI" | "FRI" }
              if (actualFee.amount !== undefined) {
                gasFeeWei = BigInt(actualFee.amount);
              } else if (actualFee.low !== undefined && actualFee.high !== undefined) {
                // Handle old U256 format: {low: string, high: string}
                const low = BigInt(String(actualFee.low));
                const high = BigInt(String(actualFee.high));
                gasFeeWei = low + (high * BigInt(2 ** 128));
              } else {
                // Fallback: try to convert to string first
                gasFeeWei = BigInt(String(actualFee));
              }
            } else {
              // Fallback: try to convert to string first
              gasFeeWei = BigInt(String(actualFee));
            }
            const gasFeeStrk = Number(gasFeeWei) / 1e18;
            console.log(`💰 Withdraw gas fee: ${gasFeeStrk.toFixed(6)} STRK (${gasFeeWei.toString()} wei)`);
          }
        } catch (feeError: any) {
          // Don't fail the withdraw if gas fee extraction fails
          console.warn('⚠️ Could not extract gas fee from receipt:', feeError.message);
        }
        
        // Wait a bit for state to update, then refresh balance
        await new Promise(resolve => setTimeout(resolve, 1000));
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

  // Check contract version once on mount or when router address changes
  useEffect(() => {
    if (strategyRouterAddress && strategyRouterAddress !== '0x0' && contractVersion === 'unknown') {
      checkContractVersion();
    }
  }, [strategyRouterAddress, checkContractVersion, contractVersion]);

  return {
    userBalance,
    contractBalance,
    strkBalance,
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
