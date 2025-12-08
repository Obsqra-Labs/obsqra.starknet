'use client';

import { useEffect, useState } from 'react';
import { RpcProvider } from 'starknet';

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

const RPC_URL = process.env.NEXT_PUBLIC_RPC_URL || 'https://starknet-sepolia.g.alchemy.com/starknet/version/rpc/v0_7/EvhYN6geLrdvbYHVRgPJ7';
const STRATEGY_ROUTER_ADDRESS = process.env.NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS || '';

// Parse felt value - handles both hex (0x...) and decimal strings
function parseFelt(value: string | undefined, defaultValue: number = 0): number {
  if (!value) return defaultValue;
  const str = value.toString();
  
  // If it starts with 0x, parse as hex
  if (str.startsWith('0x')) {
    return parseInt(str, 16);
  }
  
  // Try to parse as decimal first, then hex
  const decimal = parseInt(str, 10);
  if (!isNaN(decimal) && decimal < 10001) {
    // Likely a basis point value (0-10000)
    return decimal;
  }
  
  // Fallback: try hex
  const hex = parseInt(str, 16);
  return isNaN(hex) ? defaultValue : hex;
}

export function useStrategyRouterV2(): StrategyRouterData {
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

  useEffect(() => {
    const fetchData = async () => {
      if (!STRATEGY_ROUTER_ADDRESS) {
        setData(prev => ({
          ...prev,
          isLoading: false,
          error: 'No contract address configured',
        }));
        return;
      }

      try {
        const provider = new RpcProvider({ nodeUrl: RPC_URL });

        // Fetch all data in parallel
        const [tvlResult, allocationResult, addressesResult] = await Promise.all([
          provider.callContract({
            contractAddress: STRATEGY_ROUTER_ADDRESS,
            entrypoint: 'get_total_value_locked',
            calldata: [],
          }).catch(() => ({ result: ['0'] })),
          
          provider.callContract({
            contractAddress: STRATEGY_ROUTER_ADDRESS,
            entrypoint: 'get_allocation',
            calldata: [],
          }).catch(() => ({ result: ['5000', '5000'] })),
          
          provider.callContract({
            contractAddress: STRATEGY_ROUTER_ADDRESS,
            entrypoint: 'get_protocol_addresses',
            calldata: [],
          }).catch(() => ({ result: ['', ''] })),
        ]);

        const toResultArray = (res: string[] | { result: string[] }) =>
          Array.isArray(res) ? res : res.result || [];

        const tvlArray = toResultArray(tvlResult);
        const allocationArray = toResultArray(allocationResult);
        const addressesArray = toResultArray(addressesResult);

        // Parse TVL (u256, might be two felts)
        const tvlLow = tvlArray[0] || '0';
        const tvlValue = parseFelt(tvlLow, 0);

        // Parse allocations (basis points: 5000 = 50%)
        const jediAllocBps = parseFelt(allocationArray[0], 5000);
        const ekuboAllocBps = parseFelt(allocationArray[1], 5000);
        
        // Convert from basis points to percentage
        const jediPercent = jediAllocBps / 100;
        const ekuboPercent = ekuboAllocBps / 100;

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
        console.error('Failed to fetch StrategyRouterV2 data:', err);
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

    fetchData();
    
    // Refresh every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  return data;
}
