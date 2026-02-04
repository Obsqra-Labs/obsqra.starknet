'use client';

import { useState, useEffect, useCallback } from 'react';
import { getConfig } from '@/lib/config';

interface ModelVersion {
  version: string;
  version_felt: string;
  model_hash: string;
  model_hash_felt: string;
  deployed_at: number;
  description: string;
  is_active: boolean;
}

interface ModelRegistryData {
  registry_address: string;
  version: string;
  version_felt: string;
  model_hash: string;
  model_hash_felt: string;
  deployed_at: number;
  description: string;
  is_active: boolean;
}

interface ModelHistory {
  registry_address: string;
  versions: ModelVersion[];
}

interface RegisterModelRequest {
  version?: string;
  description?: string;
  model_hash?: string;
}

export function useModelRegistry() {
  const [current, setCurrent] = useState<ModelRegistryData | null>(null);
  const [history, setHistory] = useState<ModelVersion[]>([]);
  const [loading, setLoading] = useState(true);
  const [registering, setRegistering] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const config = getConfig();
  const apiBase = config.backendUrl ? `${config.backendUrl}/api/v1` : '/api/v1';

  const fetchCurrent = useCallback(async () => {
    try {
      const response = await fetch(`${apiBase}/model-registry/current`);
      if (!response.ok) {
        throw new Error(`Failed to fetch current model: ${response.statusText}`);
      }
      const data = await response.json();
      setCurrent(data);
      setError(null);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      console.error('Error fetching current model:', err);
    } finally {
      setLoading(false);
    }
  }, [apiBase]);

  const fetchHistory = useCallback(async () => {
    try {
      const response = await fetch(`${apiBase}/model-registry/history`);
      if (!response.ok) {
        throw new Error(`Failed to fetch model history: ${response.statusText}`);
      }
      const data: ModelHistory = await response.json();
      setHistory(data.versions || []);
      setError(null);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      console.error('Error fetching model history:', err);
    }
  }, [apiBase]);

  const registerModel = useCallback(async (request: RegisterModelRequest, adminKey?: string) => {
    setRegistering(true);
    setError(null);
    try {
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };
      if (adminKey) {
        headers['X-Admin-Key'] = adminKey;
      }
      const response = await fetch(`${apiBase}/model-registry/register`, {
        method: 'POST',
        headers,
        body: JSON.stringify(request),
      });
      if (!response.ok) {
        const text = await response.text();
        throw new Error(text || 'Failed to register model');
      }
      const data = await response.json();
      setCurrent(data.model);
      await fetchHistory();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      console.error('Error registering model:', err);
    } finally {
      setRegistering(false);
    }
  }, [apiBase, fetchHistory]);

  useEffect(() => {
    fetchCurrent();
    fetchHistory();
  }, [fetchCurrent, fetchHistory]);

  return {
    current,
    history,
    loading,
    registering,
    error,
    fetchCurrent,
    fetchHistory,
    registerModel,
  };
}
