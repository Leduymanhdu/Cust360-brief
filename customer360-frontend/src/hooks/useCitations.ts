import { useState, useEffect, useCallback } from 'react';
import { briefingsApi } from '../services/api';
import type { CitationItem, CitationMap } from '../types/briefing';

const cache = new Map<string, CitationItem[]>();

interface UseCitationsResult {
  citations: CitationItem[];
  citationMap: CitationMap;
  isLoading: boolean;
  error: string | null;
}

export function useCitations(
  briefingId: string | undefined,
  token: string | undefined
): UseCitationsResult {
  const [citations, setCitations] = useState<CitationItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const citationMap: CitationMap = Object.fromEntries(
    citations.map((c) => [c.citation_number, c])
  );

  useEffect(() => {
    if (!briefingId || !token) return;
    let cancelled = false;

    if (cache.has(briefingId)) {
      setCitations(cache.get(briefingId)!);
      return;
    }

    setIsLoading(true);
    setError(null);

    briefingsApi
      .getCitations(briefingId, token)
      .then((res) => {
        if (!cancelled) {
          cache.set(briefingId, res.citations);
          setCitations(res.citations);
        }
      })
      .catch((err: Error) => { if (!cancelled) setError(err.message); })
      .finally(() => { if (!cancelled) setIsLoading(false); });

    return () => { cancelled = true; };
  }, [briefingId, token]);

  return { citations, citationMap, isLoading, error };
}
