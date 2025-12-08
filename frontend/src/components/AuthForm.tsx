'use client';

import React, { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useAccount, useConnect } from '@starknet-react/core';

interface AuthFormProps {
  mode: 'signup' | 'login';
  onSuccess?: () => void;
}

export function AuthForm({ mode, onSuccess }: AuthFormProps) {
  const { signup, login, isLoading, error, clearError } = useAuth();
  const { address: walletAddress } = useAccount();
  const { connect, connectors } = useConnect();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [localError, setLocalError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    setLocalError(null);

    // Validation
    if (!email || !password) {
      setLocalError('Email and password are required');
      return;
    }

    if (mode === 'signup' && password !== confirmPassword) {
      setLocalError('Passwords do not match');
      return;
    }

    if (password.length < 8) {
      setLocalError('Password must be at least 8 characters');
      return;
    }

    try {
      if (mode === 'signup') {
        await signup(email, password);
      } else {
        await login(email, password);
      }

      setEmail('');
      setPassword('');
      setConfirmPassword('');

      onSuccess?.();
    } catch (err) {
      // Error is already set by auth context
      console.error('Auth error:', err);
    }
  };

  const displayError = localError || error;

  return (
    <div className="w-full max-w-md mx-auto">
      <div className="bg-gradient-to-br from-slate-900/80 to-slate-800/80 border border-blue-400/20 rounded-2xl p-8 shadow-xl">
        {/* Header */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-white mb-2">
            {mode === 'signup' ? '🚀 Get Started' : '🔐 Welcome Back'}
          </h2>
          <p className="text-gray-400 text-sm">
            {mode === 'signup'
              ? 'Create your Obsqra account to access verifiable AI'
              : 'Sign in to your Obsqra account'}
          </p>
        </div>

        {/* Error Display */}
        {displayError && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 mb-6">
            <p className="text-red-400 text-sm">⚠️ {displayError}</p>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Email */}
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-300 mb-2">
              Email Address
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              className="w-full px-4 py-3 bg-slate-800/50 border border-blue-400/20 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-400/50 focus:ring-1 focus:ring-blue-400/50 transition-all"
              disabled={isLoading}
            />
          </div>

          {/* Password */}
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-300 mb-2">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full px-4 py-3 bg-slate-800/50 border border-blue-400/20 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-400/50 focus:ring-1 focus:ring-blue-400/50 transition-all"
              disabled={isLoading}
            />
            {mode === 'signup' && (
              <p className="text-xs text-gray-500 mt-1">Minimum 8 characters</p>
            )}
          </div>

          {/* Confirm Password (signup only) */}
          {mode === 'signup' && (
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-300 mb-2">
                Confirm Password
              </label>
              <input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-4 py-3 bg-slate-800/50 border border-blue-400/20 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-400/50 focus:ring-1 focus:ring-blue-400/50 transition-all"
                disabled={isLoading}
              />
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white rounded-lg font-bold disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-all mt-6"
          >
            {isLoading ? (
              <>
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                {mode === 'signup' ? 'Creating Account...' : 'Signing In...'}
              </>
            ) : (
              <>
                {mode === 'signup' ? '✨ Create Account' : '🔓 Sign In'}
              </>
            )}
          </button>
        </form>

        {/* Wallet Connection Info */}
        {walletAddress && (
          <div className="mt-6 pt-6 border-t border-blue-400/10">
            <p className="text-xs text-gray-400 mb-3">
              💳 Wallet Connected:
            </p>
            <p className="text-xs font-mono text-blue-400 break-all bg-slate-800/30 p-2 rounded border border-blue-400/10">
              {walletAddress}
            </p>
            <p className="text-xs text-gray-500 mt-2">
              Your wallet will be linked after {mode === 'signup' ? 'account creation' : 'login'}
            </p>
          </div>
        )}

        {/* Divider */}
        <div className="my-6 flex items-center gap-3">
          <div className="flex-1 h-px bg-blue-400/10"></div>
          <span className="text-xs text-gray-500">OR</span>
          <div className="flex-1 h-px bg-blue-400/10"></div>
        </div>

        {/* Wallet Connect */}
        <div>
          <p className="text-xs text-gray-400 mb-3">Connect with Web3 Wallet</p>
          <div className="space-y-2">
            {connectors.map((connector) => (
              <button
                key={connector.id}
                onClick={() => connect({ connector })}
                disabled={isLoading}
                className="w-full py-3 bg-slate-800/50 hover:bg-slate-800 border border-blue-400/20 rounded-lg text-gray-300 hover:text-white font-medium text-sm disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                🔗 {connector.name}
              </button>
            ))}
          </div>
          <p className="text-xs text-gray-500 mt-3">
            You can use this to sign transactions after creating your account
          </p>
        </div>
      </div>
    </div>
  );
}

