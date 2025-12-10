'use client';

import { useEffect, useState } from 'react';
import { RpcProvider } from 'starknet';
import { getConfig } from '@/lib/config';

interface StrategyRouterData {
  totalValueLocked: string;
  jediswapAllocation: number; // percentage (0-100)
  ekuboAllocation: number; // percentage (0-100)
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

export function useStrategyRouterV2(): StrategyRouterData & { refetch: () => void } {
  const [data, setData] = useState<StrategyRouterData>({
    totalValueLocked: '0',
    jediswapAllocation: 50, // Default 50%
    ekuboAllocation: 50, // Default 50%
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
      console.log('📊 Fetching allocation from contract:', strategyRouterAddress);
      const provider = new RpcProvider({ nodeUrl: rpcUrl });

      // Fetch all data in parallel
      const [tvlResult, allocationResult, addressesResult] = await Promise.all([
        provider.callContract({
          contractAddress: strategyRouterAddress,
          entrypoint: 'get_total_value_locked',
          calldata: [],
        }).catch((err) => {
          console.warn('Failed to fetch TVL:', err);
          return { result: ['0'] };
        }),
        
        provider.callContract({
          contractAddress: strategyRouterAddress,
          entrypoint: 'get_allocation',
          calldata: [],
        }).catch((err) => {
          console.warn('Failed to fetch allocation:', err);
          return { result: ['5000', '5000'] };
        }),
        
        provider.callContract({
          contractAddress: strategyRouterAddress,
          entrypoint: 'get_protocol_addresses',
          calldata: [],
        }).catch((err) => {
          console.warn('Failed to fetch protocol addresses:', err);
          return { result: ['', ''] };
        }),
      ]);

      const toResultArray = (res: any): string[] => {
        if (Array.isArray(res)) {
          return res.map(String);
        }
        if (res && typeof res === 'object' && 'result' in res) {
          return Array.isArray(res.result) ? res.result.map(String) : [];
        }
        return [];
      };

      const tvlArray = toResultArray(tvlResult);
      const allocationArray = toResultArray(allocationResult);
      const addressesArray = toResultArray(addressesResult);

      console.log('🔍 Raw allocation result:', allocationResult);
      console.log('🔍 Parsed allocation array:', allocationArray);

      // Parse TVL (u256, might be two felts)
      const tvlLow = tvlArray[0] || '0';
      const tvlValue = parseFelt(tvlLow, 0);

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
      const jediAddr = allocationArray[0] ? addressesArray[0]?.toString() || '' : '';
      const ekuboAddr = addressesArray[1] ? addressesArray[1]?.toString() || '' : '';

      setData({
        totalValueLocked: tvlValue.toString(),
        jediswapAllocation: jediPercent,
        ekuboAllocation: ekuboPercent,
        jediswapRouter: jediAddr,
        ekuboCore: ekuboAddr,
        isLoading: false,
        error: null,
        lastUpdated: new Date(),
      });
    } catch (err) {
      console.error('❌ Failed to fetch StrategyRouterV2 data:', err);
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
      console.log('🔄 Auto-refreshing allocation (15s interval)...');
      fetchData();
    }, 15000);
    return () => clearInterval(interval);
  }, []);

  return {
    ...data,
    refetch: fetchData,
  };
}
