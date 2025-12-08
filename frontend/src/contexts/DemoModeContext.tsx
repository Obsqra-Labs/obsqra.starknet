'use client';

import { createContext, useContext, useState, ReactNode, useEffect } from 'react';

interface DemoModeContextType {
  isDemoMode: boolean;
  toggleDemoMode: () => void;
  mockData: {
    allocation: { jediswap: number; ekubo: number };
    tvl: string;
  };
  updateMockAllocation: (jediswap: number, ekubo: number) => void;
}

const DemoModeContext = createContext<DemoModeContextType | undefined>(undefined);

export function DemoModeProvider({ children }: { children: ReactNode }) {
  const [isDemoMode, setIsDemoMode] = useState(false);
  const [mockData, setMockData] = useState({
    allocation: { jediswap: 50, ekubo: 50 },
    tvl: '1000',
  });

  const toggleDemoMode = () => {
    setIsDemoMode(prev => !prev);
  };

  const updateMockAllocation = (jediswap: number, ekubo: number) => {
    setMockData(prev => ({
      ...prev,
      allocation: { jediswap, ekubo },
    }));
  };

  // Load demo mode preference from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('obsqra_demo_mode');
    if (saved === 'true') {
      setIsDemoMode(true);
    }
  }, []);

  // Save demo mode preference
  useEffect(() => {
    localStorage.setItem('obsqra_demo_mode', isDemoMode ? 'true' : 'false');
  }, [isDemoMode]);

  return (
    <DemoModeContext.Provider
      value={{
        isDemoMode,
        toggleDemoMode,
        mockData,
        updateMockAllocation,
      }}
    >
      {children}
    </DemoModeContext.Provider>
  );
}

export function useDemoMode() {
  const context = useContext(DemoModeContext);
  if (context === undefined) {
    throw new Error('useDemoMode must be used within a DemoModeProvider');
  }
  return context;
}
