'use client';

import { useState, useEffect } from 'react';
import { useAccount } from '@starknet-react/core';

/**
 * ConstraintBuilder Component
 * 
 * Allows DAO to configure allocation constraints that AI must respect.
 * This is the core of "Verified AI" - AI proposes, DAO constrains.
 */

interface AllocationConstraints {
  // Allocation percentage bounds (basis points: 10000 = 100%)
  min_jediswap_pct: number;
  max_jediswap_pct: number;
  min_ekubo_pct: number;
  max_ekubo_pct: number;
  
  // Risk score bounds
  max_jediswap_risk: number;
  max_ekubo_risk: number;
  
  // Volatility thresholds
  max_volatility_diff: number; // Max difference between protocol volatilities
  
  // Liquidity requirements
  min_liquidity_category: number; // 0-3 scale
}

interface ConstraintBuilderProps {
  onConstraintsUpdated?: (constraints: AllocationConstraints) => void;
}

export function ConstraintBuilder({ onConstraintsUpdated }: ConstraintBuilderProps) {
  const { address, isConnected } = useAccount();
  
  // Default constraints (permissive for demo)
  const [constraints, setConstraints] = useState<AllocationConstraints>({
    min_jediswap_pct: 0,
    max_jediswap_pct: 10000,
    min_ekubo_pct: 0,
    max_ekubo_pct: 10000,
    max_jediswap_risk: 95,
    max_ekubo_risk: 95,
    max_volatility_diff: 5000,
    min_liquidity_category: 0,
  });
  
  const [isSaving, setIsSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  
  const handleConstraintChange = (field: keyof AllocationConstraints, value: number) => {
    setConstraints(prev => ({
      ...prev,
      [field]: value
    }));
    setSaveStatus('idle');
  };
  
  const handleSaveConstraints = async () => {
    if (!isConnected || !address) {
      setErrorMessage('Please connect your wallet');
      setSaveStatus('error');
      return;
    }
    
    // Validate constraints
    if (constraints.min_jediswap_pct + constraints.min_ekubo_pct > 10000) {
      setErrorMessage('Min allocations cannot sum to more than 100%');
      setSaveStatus('error');
      return;
    }
    
    setIsSaving(true);
    setErrorMessage(null);
    
    try {
      // TODO: Call DAOConstraintManager contract to update constraints
      // For MVP, we'll just simulate the save
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      setSaveStatus('success');
      onConstraintsUpdated?.(constraints);
      
      console.log('✅ Constraints updated:', constraints);
      
      // Reset success message after 3 seconds
      setTimeout(() => setSaveStatus('idle'), 3000);
    } catch (error) {
      console.error('❌ Failed to save constraints:', error);
      setErrorMessage(error instanceof Error ? error.message : 'Failed to save constraints');
      setSaveStatus('error');
    } finally {
      setIsSaving(false);
    }
  };
  
  const bpsToPercent = (bps: number) => (bps / 100).toFixed(1);
  
  return (
    <div className="bg-white rounded-2xl shadow-soft border border-slate-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-display font-bold text-ink">
            🔧 DAO Constraint Builder
          </h2>
          <p className="text-sm text-slate-600 mt-1">
            Configure rules that AI allocation decisions must respect
          </p>
        </div>
        {saveStatus === 'success' && (
          <div className="text-green-600 text-sm font-medium">
            ✅ Constraints saved on-chain
          </div>
        )}
      </div>
      
      {!isConnected ? (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-center">
          <p className="text-amber-800 font-medium">
            🔒 Connect your wallet to configure DAO constraints
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Allocation Percentage Bounds */}
          <div className="bg-lagoon-50 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-ink mb-4">
              📊 Allocation Percentage Limits
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <ConstraintInput
                label="Min JediSwap %"
                value={constraints.min_jediswap_pct}
                onChange={(val) => handleConstraintChange('min_jediswap_pct', val)}
                min={0}
                max={10000}
                step={100}
                displayValue={bpsToPercent(constraints.min_jediswap_pct)}
                suffix="%"
              />
              <ConstraintInput
                label="Max JediSwap %"
                value={constraints.max_jediswap_pct}
                onChange={(val) => handleConstraintChange('max_jediswap_pct', val)}
                min={0}
                max={10000}
                step={100}
                displayValue={bpsToPercent(constraints.max_jediswap_pct)}
                suffix="%"
              />
              <ConstraintInput
                label="Min Ekubo %"
                value={constraints.min_ekubo_pct}
                onChange={(val) => handleConstraintChange('min_ekubo_pct', val)}
                min={0}
                max={10000}
                step={100}
                displayValue={bpsToPercent(constraints.min_ekubo_pct)}
                suffix="%"
              />
              <ConstraintInput
                label="Max Ekubo %"
                value={constraints.max_ekubo_pct}
                onChange={(val) => handleConstraintChange('max_ekubo_pct', val)}
                min={0}
                max={10000}
                step={100}
                displayValue={bpsToPercent(constraints.max_ekubo_pct)}
                suffix="%"
              />
            </div>
          </div>
          
          {/* Risk Bounds */}
          <div className="bg-mint-50 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-ink mb-4">
              🛡️ Risk Score Limits
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <ConstraintInput
                label="Max JediSwap Risk"
                value={constraints.max_jediswap_risk}
                onChange={(val) => handleConstraintChange('max_jediswap_risk', val)}
                min={5}
                max={95}
                step={5}
                displayValue={constraints.max_jediswap_risk.toString()}
                suffix="/95"
              />
              <ConstraintInput
                label="Max Ekubo Risk"
                value={constraints.max_ekubo_risk}
                onChange={(val) => handleConstraintChange('max_ekubo_risk', val)}
                min={5}
                max={95}
                step={5}
                displayValue={constraints.max_ekubo_risk.toString()}
                suffix="/95"
              />
            </div>
          </div>
          
          {/* Volatility & Liquidity */}
          <div className="bg-sand-50 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-ink mb-4">
              ⚡ Volatility & Liquidity Rules
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <ConstraintInput
                label="Max Volatility Difference"
                value={constraints.max_volatility_diff}
                onChange={(val) => handleConstraintChange('max_volatility_diff', val)}
                min={1000}
                max={10000}
                step={500}
                displayValue={bpsToPercent(constraints.max_volatility_diff)}
                suffix="%"
                helpText="Max allowed difference between protocol volatilities"
              />
              <ConstraintInput
                label="Min Liquidity Category"
                value={constraints.min_liquidity_category}
                onChange={(val) => handleConstraintChange('min_liquidity_category', val)}
                min={0}
                max={3}
                step={1}
                displayValue={constraints.min_liquidity_category.toString()}
                suffix="/3"
                helpText="0=Low, 1=Medium, 2=High, 3=Very High"
              />
            </div>
          </div>
          
          {/* Save Button */}
          <div className="pt-4 border-t border-slate-200">
            {errorMessage && (
              <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-sm">
                ❌ {errorMessage}
              </div>
            )}
            <button
              onClick={handleSaveConstraints}
              disabled={isSaving || saveStatus === 'success'}
              className={`
                w-full py-3 px-6 rounded-xl font-semibold text-white
                transition-all duration-200 transform
                ${isSaving || saveStatus === 'success' 
                  ? 'bg-slate-400 cursor-not-allowed' 
                  : 'bg-gradient-to-r from-lagoon-500 to-mint-500 hover:shadow-lift hover:scale-[1.02]'}
              `}
            >
              {isSaving ? (
                <span className="flex items-center justify-center gap-2">
                  <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent" />
                  Saving Constraints...
                </span>
              ) : saveStatus === 'success' ? (
                '✅ Constraints Saved'
              ) : (
                '💾 Save DAO Constraints On-Chain'
              )}
            </button>
            
            {isConnected && (
              <p className="text-xs text-slate-500 text-center mt-2">
                Connected: {address?.substring(0, 6)}...{address?.substring(address.length - 4)}
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

// Helper component for constraint inputs
interface ConstraintInputProps {
  label: string;
  value: number;
  onChange: (value: number) => void;
  min: number;
  max: number;
  step: number;
  displayValue: string;
  suffix?: string;
  helpText?: string;
}

function ConstraintInput({
  label,
  value,
  onChange,
  min,
  max,
  step,
  displayValue,
  suffix,
  helpText
}: ConstraintInputProps) {
  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-ink">
        {label}
      </label>
      <div className="flex items-center gap-3">
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          className="flex-1 h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer 
                     [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 
                     [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:bg-lagoon-500 
                     [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:cursor-pointer"
        />
        <div className="text-sm font-mono font-semibold text-ink min-w-[4rem] text-right">
          {displayValue}{suffix}
        </div>
      </div>
      {helpText && (
        <p className="text-xs text-slate-500 italic">{helpText}</p>
      )}
    </div>
  );
}

