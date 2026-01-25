"use client";

import { useCallback, useState } from "react";

export interface ZkmlVerificationResult {
  verified: boolean;
  calldata_source: string;
  profile?: string;
}

export function useZkmlVerification() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ZkmlVerificationResult | null>(null);

  const verify = useCallback(async (profile: "cairo0" | "cairo1" = "cairo0") => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await fetch(`/api/v1/zkml/verify-demo?profile=${profile}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      if (!res.ok) {
        const payload = await res.json().catch(() => ({}));
        throw new Error(payload.detail || `Verification failed: ${res.statusText}`);
      }
      const json = await res.json();
      setResult(json);
      return json as ZkmlVerificationResult;
    } catch (err) {
      const message = err instanceof Error ? err.message : "Verification failed";
      setError(message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    verify,
    loading,
    error,
    result,
  };
}
