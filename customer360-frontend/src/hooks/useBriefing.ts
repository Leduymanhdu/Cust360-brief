import { useState, useEffect, useCallback } from 'react';
import { briefingsApi } from '../services/api';
import type { BriefingResponse } from '../types/briefing';

interface UseBriefingResult {
  briefing: BriefingResponse | null;
  isLoading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useBriefing(briefingId: string | undefined, token: string | undefined): UseBriefingResult {
  const [briefing, setBriefing] = useState<BriefingResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tick, setTick] = useState(0);

  const refetch = useCallback(() => setTick((t) => t + 1), []);

  useEffect(() => {
    if (!briefingId || !token) return;
    let cancelled = false;

    setIsLoading(true);
    setError(null);

    briefingsApi
      .get(briefingId, token)
      .then((data) => { if (!cancelled) setBriefing(data); })
      .catch((err: Error) => { if (!cancelled) setError(err.message); })
      .finally(() => { if (!cancelled) setIsLoading(false); });

    return () => { cancelled = true; };
  }, [briefingId, token, tick]);

  return { briefing, isLoading, error, refetch };
}
