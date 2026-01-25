'use client';

import { useEffect, useState } from 'react';
import { RpcProvider } from 'starknet';
import { getConfig } from '@/lib/config';

interface StrategyRouterData {
  totalValueLocked: string; // Vault TVL (total deposits)
  jediswapAllocation: number; // percentage (0-100)
  ekuboAllocation: number; // percentage (0-100)
  jediswapTvl: string; // Protocol TVL (deployed to JediSwap)
  ekuboTvl: string; // Protocol TVL (deployed to Ekubo)
  totalYieldAccrued: string; // v3.5: total yield accrued
  jediswapProjectedApy: number; // Projected APY from backend
  ekuboProjectedApy: number; // Projected APY from backend
  jediswapActualApy: number; // Actual APY calculated from on-chain data
  ekuboActualApy: number; // Actual APY calculated from on-chain data
  pendingFees: { jediswap: string; ekubo: string }; // Pending fees available to collect
  jediswapRouter: string;
  ekuboCore: string;
  isLoading: boolean;
  error: string | null;
  lastUpdated: Date | null;
}

// Parse felt value - handles both hex (0x...) and decimal strings
function parseFelt(value: string | undefined, defaultValue: number = 0): number {
  if (!value) return defaultValue;
  const str = value.toString().trim();
  
  // If it starts with 0x, parse as hex
  if (str.startsWith('0x') || str.startsWith('0X')) {
    const parsed = parseInt(str, 16);
    return isNaN(parsed) ? defaultValue : parsed;
  }
  
  // Try to parse as decimal
  const decimal = parseInt(str, 10);
  if (!isNaN(decimal)) {
    return decimal;
  }
  
  // Fallback: try hex without 0x prefix
  const hex = parseInt(str, 16);
  return isNaN(hex) ? defaultValue : hex;
}

// Parse u256 (two felts: low, high)
function parseU256(result: string[]): bigint {
  if (result.length < 1) return 0n;
  const low = BigInt(result[0] || '0');
  if (result.length < 2) return low;
  const high = BigInt(result[1] || '0');
  return low + (high << 128n);
}

export function useStrategyRouter(): StrategyRouterData & { refetch: () => void } {
  const [data, setData] = useState<StrategyRouterData>({
    totalValueLocked: '0',
    jediswapAllocation: 50, // Default 50%
    ekuboAllocation: 50, // Default 50%
    jediswapTvl: '0',
    ekuboTvl: '0',
    totalYieldAccrued: '0',
    jediswapProjectedApy: 5.2, // Default, will fetch from backend
    ekuboProjectedApy: 8.5, // Default, will fetch from backend
    jediswapActualApy: 0, // Calculated from on-chain data
    ekuboActualApy: 0, // Calculated from on-chain data
    pendingFees: { jediswap: '0', ekubo: '0' },
    jediswapRouter: '',
    ekuboCore: '',
    isLoading: true,
    error: null,
    lastUpdated: null,
  });

  const fetchData = async () => {
    const config = getConfig();
    const strategyRouterAddress = config.strategyRouterAddress;
    const rpcUrl = config.rpcUrl;

    if (!strategyRouterAddress) {
      setData(prev => ({
        ...prev,
        isLoading: false,
        error: 'No contract address configured',
      }));
      return;
    }

    try {
      console.log('📊 Fetching data from Strategy Router v3.5:', strategyRouterAddress);
      const provider = new RpcProvider({ nodeUrl: rpcUrl });

      // Helper to check if error indicates missing function
      const isFunctionNotFound = (error: any): boolean => {
        const msg = error?.message || String(error || '');
        return msg.includes('Contract not found') || 
               msg.includes('ENTRYPOINT_NOT_FOUND') ||
               msg.includes('Entry point') ||
               msg.includes('undefined');
      };

      // Helper to extract result array from RPC response
      // RpcProvider.callContract can return results in different formats:
      // - Direct array: [felt1, felt2, ...]
      // - Wrapped: { result: [felt1, felt2, ...] }
      // - For tuples: might be nested arrays
      const toResultArray = (res: any): string[] => {
        // If it's already an array, use it directly
        if (Array.isArray(res)) {
          // Flatten nested arrays (for tuples)
          const flattened: string[] = [];
          const flatten = (arr: any[]): void => {
            for (const item of arr) {
              if (Array.isArray(item)) {
                flatten(item);
              } else {
                flattened.push(String(item));
              }
            }
          };
          flatten(res);
          return flattened.length > 0 ? flattened : res.map(String);
        }
        // Sometimes wrapped in result field
        if (res && typeof res === 'object') {
          if ('result' in res && Array.isArray(res.result)) {
            // Flatten nested arrays
            const flattened: string[] = [];
            const flatten = (arr: any[]): void => {
              for (const item of arr) {
                if (Array.isArray(item)) {
                  flatten(item);
                } else {
                  flattened.push(String(item));
                }
              }
            };
            flatten(res.result);
            return flattened.length > 0 ? flattened : res.result.map(String);
          }
        }
        return [];
      };
      
      // Fetch VAULT TVL (total deposits) - separate from protocol TVL
      let vaultTvl = '0';
      try {
        const vaultTvlResult = await provider.callContract({
          contractAddress: strategyRouterAddress,
          entrypoint: 'get_total_value_locked',
          calldata: [],
        });
        const vaultArray = toResultArray(vaultTvlResult);
        vaultTvl = parseU256(vaultArray).toString();
        console.log('✅ Vault TVL (total deposits):', vaultTvl);
      } catch (vaultErr) {
        console.warn('⚠️ Could not fetch vault TVL:', vaultErr);
      }
      
      // Fetch PROTOCOL TVL (deployed to protocols) - separate from vault TVL
      let jediswapTvl = '0';
      let ekuboTvl = '0';
      
      // Try v3.5 get_protocol_tvl first (returns both protocol TVLs)
      try {
        const protocolTvlResult = await provider.callContract({
          contractAddress: strategyRouterAddress,
          entrypoint: 'get_protocol_tvl',
          calldata: [],
        });
        
        const tvlArray = toResultArray(protocolTvlResult);
        console.log('🔍 Raw get_protocol_tvl response:', {
          raw: protocolTvlResult,
          rawType: typeof protocolTvlResult,
          isArray: Array.isArray(protocolTvlResult),
          array: tvlArray,
          length: tvlArray.length,
          firstFew: tvlArray.slice(0, 6)
        });
        
        if (tvlArray.length >= 4) {
          // Contract returns (u256, u256) = 4 felts: [jedi_low, jedi_high, ekubo_low, ekubo_high]
          jediswapTvl = parseU256([tvlArray[0], tvlArray[1] || '0']).toString();
          ekuboTvl = parseU256([tvlArray[2] || '0', tvlArray[3] || '0']).toString();
          console.log('✅ Parsed protocol TVL (4-felt format):', { 
            jediswapTvl, 
            ekuboTvl,
            jediLow: tvlArray[0],
            jediHigh: tvlArray[1],
            ekuboLow: tvlArray[2],
            ekuboHigh: tvlArray[3]
          });
        } else if (tvlArray.length === 2) {
          // Try parsing as if each element is a u256 (each u256 = 2 felts, but response might be flattened)
          // This shouldn't happen, but handle it defensively
          jediswapTvl = parseU256([tvlArray[0], '0']).toString();
          ekuboTvl = parseU256([tvlArray[1] || '0', '0']).toString();
          console.log('⚠️ Parsed protocol TVL (2-element format - unexpected):', { jediswapTvl, ekuboTvl });
        } else if (tvlArray.length > 0) {
          // Try to parse whatever we got
          console.warn('⚠️ get_protocol_tvl returned unexpected format, length:', tvlArray.length, 'array:', tvlArray);
          // Try to extract first two u256s if possible
          if (tvlArray.length >= 2) {
            jediswapTvl = parseU256([tvlArray[0], tvlArray[1] || '0']).toString();
          }
          if (tvlArray.length >= 4) {
            ekuboTvl = parseU256([tvlArray[2] || '0', tvlArray[3] || '0']).toString();
          }
        } else {
          console.warn('⚠️ get_protocol_tvl returned empty array. Raw response:', protocolTvlResult);
        }
      } catch (err) {
        if (isFunctionNotFound(err)) {
          console.log('⚠️ v3.5 get_protocol_tvl not found, trying individual getters...');
          
          // Fallback: try individual getters
          try {
            const jediTvlResult = await provider.callContract({
              contractAddress: strategyRouterAddress,
              entrypoint: 'get_jediswap_tvl',
              calldata: [],
            });
            const ekuboTvlResult = await provider.callContract({
              contractAddress: strategyRouterAddress,
              entrypoint: 'get_ekubo_tvl',
              calldata: [],
            });
            
            const jediArray = toResultArray(jediTvlResult);
            const ekuboArray = toResultArray(ekuboTvlResult);
            jediswapTvl = parseU256(jediArray).toString();
            ekuboTvl = parseU256(ekuboArray).toString();
            console.log('✅ Using individual protocol TVL getters:', { jediswapTvl, ekuboTvl });
          } catch (indErr) {
            console.warn('⚠️ Individual protocol TVL getters also failed:', indErr);
          }
        } else {
          console.warn('⚠️ Error fetching get_protocol_tvl:', err);
        }
      }
      
      // Use vault TVL as total TVL (total deposits)
      const totalTvl = vaultTvl;

      // Fetch allocation (always try this)
      const allocationResult = await provider.callContract({
        contractAddress: strategyRouterAddress,
        entrypoint: 'get_allocation',
        calldata: [],
      }).catch((err) => {
        console.warn('Failed to fetch allocation:', err);
        return { result: ['5000', '5000'] };
      });

      // Fetch protocol addresses
      const addressesResult = await provider.callContract({
        contractAddress: strategyRouterAddress,
        entrypoint: 'get_protocol_addresses',
        calldata: [],
      }).catch((err) => {
        if (isFunctionNotFound(err)) {
          console.warn('⚠️ get_protocol_addresses not found on contract');
        } else {
          console.warn('Failed to fetch protocol addresses:', err);
        }
        return { result: ['', ''] };
      });

      const allocationArray = toResultArray(allocationResult);
      const addressesArray = toResultArray(addressesResult);

      console.log('🔍 Raw allocation result:', allocationResult);
      console.log('🔍 Parsed allocation array:', allocationArray);

      // Parse allocations (basis points: 5000 = 50%)
      // Contract returns (felt252, felt252) which are the basis point values
      const jediAllocBps = parseFelt(allocationArray[0], 5000);
      const ekuboAllocBps = parseFelt(allocationArray[1], 5000);
      
      console.log('📊 Allocation from contract (basis points):', { 
        jedi: jediAllocBps, 
        ekubo: ekuboAllocBps,
        jediRaw: allocationArray[0],
        ekuboRaw: allocationArray[1]
      });
      
      // Convert from basis points to percentage
      const jediPercent = jediAllocBps / 100;
      const ekuboPercent = ekuboAllocBps / 100;

      console.log('📊 Allocation percentages:', { jediswap: jediPercent, ekubo: ekuboPercent });
      
      // Validate: allocations should sum to 100%
      const total = jediPercent + ekuboPercent;
      if (Math.abs(total - 100) > 0.1) {
        console.warn(`⚠️ Allocation doesn't sum to 100%: ${jediPercent}% + ${ekuboPercent}% = ${total}%`);
      }

      // Parse addresses
      const jediAddr = addressesArray[0]?.toString() || '';
      const ekuboAddr = addressesArray[1]?.toString() || '';

      // Fetch total yield accrued (v3.5 function)
      let totalYield = '0';
      try {
        const yieldResult = await provider.callContract({
          contractAddress: strategyRouterAddress,
          entrypoint: 'get_total_yield_accrued',
          calldata: [],
        });
        const yieldArray = toResultArray(yieldResult);
        if (yieldArray.length >= 1) {
          totalYield = parseU256(yieldArray).toString();
          console.log('✅ Fetched total yield accrued:', totalYield);
        }
      } catch (yieldErr) {
        if (isFunctionNotFound(yieldErr)) {
          console.log('⚠️ get_total_yield_accrued not found (v2 contract), using 0');
        } else {
          console.warn('⚠️ Failed to fetch total yield:', yieldErr);
        }
      }

      // Fetch projected APY from backend API
      let jediswapProjectedApy = 5.2; // Default
      let ekuboProjectedApy = 8.5; // Default
      try {
        const config = getConfig();
        const backendUrl = config.backendUrl || 'http://localhost:8001';
        const apyResponse = await fetch(`${backendUrl}/api/v1/analytics/protocol-apys`, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
        });
        
        if (apyResponse.ok) {
          const apyData = await apyResponse.json();
          jediswapProjectedApy = apyData.jediswap || 5.2;
          ekuboProjectedApy = apyData.ekubo || 8.5;
          console.log('✅ Fetched projected APY from backend:', { jediswapProjectedApy, ekuboProjectedApy });
        } else {
          console.warn('⚠️ Failed to fetch projected APY from backend, using defaults');
        }
      } catch (apyErr) {
        console.warn('⚠️ Error fetching projected APY:', apyErr);
      }

      // Calculate actual APY from on-chain data (if we have yield and TVL)
      let jediswapActualApy = 0;
      let ekuboActualApy = 0;
      try {
        // Calculate actual APY: (yield / tvl) * 100 * (365 / days)
        // For now, use projected APY as actual (can be enhanced with historical data)
        // TODO: Calculate from historical yield data
        jediswapActualApy = jediswapProjectedApy; // Placeholder
        ekuboActualApy = ekuboProjectedApy; // Placeholder
      } catch (apyCalcErr) {
        console.warn('⚠️ Error calculating actual APY:', apyCalcErr);
      }

      // Fetch pending fees from contract
      let pendingFees = { jediswap: '0', ekubo: '0' };
      try {
        // Try to fetch pending fees (if contract has this function)
        const feesResult = await provider.callContract({
          contractAddress: strategyRouterAddress,
          entrypoint: 'get_pending_fees',
          calldata: [],
        }).catch(() => null);
        
        if (feesResult) {
          const feesArray = toResultArray(feesResult);
          if (feesArray.length >= 2) {
            pendingFees = {
              jediswap: parseU256([feesArray[0], feesArray[1] || '0']).toString(),
              ekubo: parseU256([feesArray[2] || '0', feesArray[3] || '0']).toString(),
            };
            console.log('✅ Fetched pending fees:', pendingFees);
          }
        }
      } catch (feesErr) {
        if (isFunctionNotFound(feesErr)) {
          console.log('⚠️ get_pending_fees not found on contract, using defaults');
        } else {
          console.warn('⚠️ Error fetching pending fees:', feesErr);
        }
      }

      setData({
        totalValueLocked: vaultTvl || '0', // Vault TVL (total deposits)
        jediswapAllocation: jediPercent,
        ekuboAllocation: ekuboPercent,
        jediswapTvl: jediswapTvl || '0', // Protocol TVL (deployed to JediSwap)
        ekuboTvl: ekuboTvl || '0', // Protocol TVL (deployed to Ekubo)
        totalYieldAccrued: totalYield,
        jediswapProjectedApy,
        ekuboProjectedApy,
        jediswapActualApy,
        ekuboActualApy,
        pendingFees,
        jediswapRouter: jediAddr,
        ekuboCore: ekuboAddr,
        isLoading: false,
        error: null,
        lastUpdated: new Date(),
      });
    } catch (err) {
      console.error('❌ Failed to fetch StrategyRouter data:', err);
      setData(prev => ({
        ...prev,
        jediswapAllocation: 50,
        ekuboAllocation: 50,
        isLoading: false,
        error: err instanceof Error ? err.message : 'Failed to fetch data',
        lastUpdated: new Date(),
      }));
    }
  };

  useEffect(() => {
    fetchData();
    
    // Refresh every 15 seconds (more frequent to catch updates faster)
    const interval = setInterval(() => {
      console.log('🔄 Auto-refreshing Strategy Router data (15s interval)...');
      fetchData();
    }, 15000);
    return () => clearInterval(interval);
  }, []);

  return {
    ...data,
    refetch: fetchData,
  };
}
