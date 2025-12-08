'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { AuthForm } from '@/components/AuthForm';

export default function AuthPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [mode, setMode] = useState<'signup' | 'login'>('signup');

  // Redirect if already authenticated
  if (user) {
    router.push('/dashboard');
    return null;
  }

  const handleAuthSuccess = () => {
    router.push('/dashboard');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute top-0 left-0 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl"></div>
      <div className="absolute bottom-0 right-0 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl"></div>

      {/* Content */}
      <div className="relative z-10 min-h-screen flex flex-col items-center justify-center px-4 py-12">
        {/* Logo/Branding */}
        <div className="mb-12 text-center">
          <h1 className="text-5xl font-bold text-white mb-2">obsqra</h1>
          <p className="text-gray-400">Verifiable AI Infrastructure for DeFi</p>
        </div>

        {/* Auth Form */}
        <AuthForm mode={mode} onSuccess={handleAuthSuccess} />

        {/* Mode Toggle */}
        <div className="mt-8 text-center">
          <p className="text-gray-400 mb-3">
            {mode === 'signup'
              ? 'Already have an account?'
              : "Don't have an account?"}
          </p>
          <button
            onClick={() => setMode(mode === 'signup' ? 'login' : 'signup')}
            className="text-blue-400 hover:text-blue-300 font-medium transition-colors"
          >
            {mode === 'signup' ? 'Sign In' : 'Create Account'}
          </button>
        </div>

        {/* Features Info */}
        <div className="mt-16 max-w-2xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-slate-900/50 border border-blue-400/10 rounded-lg p-4">
            <div className="text-2xl mb-2">🔐</div>
            <h3 className="font-semibold text-white mb-1">Email Signup</h3>
            <p className="text-xs text-gray-400">Create account with email & password</p>
          </div>

          <div className="bg-slate-900/50 border border-blue-400/10 rounded-lg p-4">
            <div className="text-2xl mb-2">🔗</div>
            <h3 className="font-semibold text-white mb-1">Wallet Linking</h3>
            <p className="text-xs text-gray-400">Connect wallet for transactions</p>
          </div>

          <div className="bg-slate-900/50 border border-blue-400/10 rounded-lg p-4">
            <div className="text-2xl mb-2">✅</div>
            <h3 className="font-semibold text-white mb-1">Verified Proofs</h3>
            <p className="text-xs text-gray-400">All AI logic is cryptographically proven</p>
          </div>
        </div>
      </div>
    </div>
  );
}

