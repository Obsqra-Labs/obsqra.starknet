'use client';

import { useState, useMemo } from 'react';

export type PoolType = 'conservative' | 'balanced' | 'aggressive';

export interface Pool {
  id: PoolType;
  name: string;
  allocation: string;
  riskLevel: 'Low' | 'Medium' | 'High';
  targetAPY: string;
  address: string;
}

const POOLS: Record<PoolType, Pool> = {
  conservative: {
    id: 'conservative',
    name: 'Conservative',
    allocation: '70% JediSwap, 30% Ekubo',
    riskLevel: 'Low',
    targetAPY: '5-8%',
    address: process.env.NEXT_PUBLIC_POOL_CONSERVATIVE || '',
  },
  balanced: {
    id: 'balanced',
    name: 'Balanced',
    allocation: '50% JediSwap, 50% Ekubo',
    riskLevel: 'Medium',
    targetAPY: '8-12%',
    address: process.env.NEXT_PUBLIC_POOL_BALANCED || '',
  },
  aggressive: {
    id: 'aggressive',
    name: 'Aggressive',
    allocation: '30% JediSwap, 70% Ekubo',
    riskLevel: 'High',
    targetAPY: '12-20%',
    address: process.env.NEXT_PUBLIC_POOL_AGGRESSIVE || '',
  },
};

export function usePoolSelection() {
  const [selectedPool, setSelectedPool] = useState<PoolType>('balanced');

  const pool = useMemo(() => POOLS[selectedPool], [selectedPool]);
  const allPools = useMemo(() => Object.values(POOLS), []);

  return {
    selectedPool,
    setSelectedPool,
    pool,
    allPools,
    pools: POOLS,
  };
}

