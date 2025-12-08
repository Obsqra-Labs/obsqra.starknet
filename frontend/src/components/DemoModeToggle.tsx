'use client';

import { useDemoMode } from '@/contexts/DemoModeContext';

export function DemoModeToggle() {
  const { isDemoMode, toggleDemoMode } = useDemoMode();

  return (
    <button
      onClick={toggleDemoMode}
      className={`
        relative inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-all
        ${isDemoMode 
          ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/40 hover:bg-yellow-500/30' 
          : 'bg-green-500/20 text-green-400 border border-green-500/40 hover:bg-green-500/30'
        }
      `}
      title={isDemoMode ? 'Click to switch to Live mode' : 'Click to enable Demo mode'}
    >
      <span>{isDemoMode ? '🎮' : '✅'}</span>
      <span>{isDemoMode ? 'Demo' : 'Live'}</span>
    </button>
  );
}
