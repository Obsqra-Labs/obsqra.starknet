'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useWalletKit } from 'obsqra.kit';

export interface User {
  id: string;
  email: string;
  wallet_address?: string;
  created_at: string;
  updated_at: string;
}

export interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Auth methods
  signup: (email: string, password: string) => Promise<void>;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  connectWallet: (wallet_address: string) => Promise<void>;
  
  // State management
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const { address: walletAddress, disconnect } = useWalletKit();

  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);

  const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8001';

  // Check if user is already logged in on mount
  useEffect(() => {
    const storedUser = localStorage.getItem('obsqra_user');
    const storedToken = localStorage.getItem('obsqra_token');
    if (storedUser && storedToken) {
      try {
        setUser(JSON.parse(storedUser));
        setAccessToken(storedToken);
      } catch (err) {
        console.error('Failed to restore auth state:', err);
        localStorage.removeItem('obsqra_user');
        localStorage.removeItem('obsqra_token');
      }
    }
  }, []);

  // Auto-connect wallet if user is logged in
  useEffect(() => {
    if (user && walletAddress && !user.wallet_address) {
      connectWallet(walletAddress).catch(err => console.error('Failed to link wallet:', err));
    }
  }, [walletAddress, user]);

  const signup = async (email: string, password: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${BACKEND_URL}/api/v1/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Signup failed');
      }

      const data = await response.json();
      setUser(data.user);
      setAccessToken(data.access_token);

      localStorage.setItem('obsqra_user', JSON.stringify(data.user));
      localStorage.setItem('obsqra_token', data.access_token);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Signup failed';
      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${BACKEND_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Login failed');
      }

      const data = await response.json();
      setUser(data.user);
      setAccessToken(data.access_token);

      localStorage.setItem('obsqra_user', JSON.stringify(data.user));
      localStorage.setItem('obsqra_token', data.access_token);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Login failed';
      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    try {
      setUser(null);
      setAccessToken(null);
      localStorage.removeItem('obsqra_user');
      localStorage.removeItem('obsqra_token');
      
      // Disconnect wallet too
      try {
        disconnect();
      } catch (err) {
        console.warn('Failed to disconnect wallet:', err);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const connectWallet = async (wallet_address: string) => {
    if (!user || !accessToken) {
      setError('Must be logged in to connect wallet');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${BACKEND_URL}/api/v1/auth/connect-wallet`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ wallet_address }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to connect wallet');
      }

      const data = await response.json();
      setUser(data.user);
      localStorage.setItem('obsqra_user', JSON.stringify(data.user));
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to connect wallet';
      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const clearError = () => setError(null);

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    error,
    signup,
    login,
    logout,
    connectWallet,
    clearError,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
