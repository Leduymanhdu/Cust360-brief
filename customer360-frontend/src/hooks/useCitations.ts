import { useState, useEffect, useRef } from 'react';
import { fetchCitations, buildCitationMap } from '../services/citationService';
import type { CitationMap } from '../types/briefing';

interface UseCitationsResult {
  citationMap: CitationMap;
  isLoading: boolean;
  error: string | null;
}

const cache = new Map<string, CitationMap>();

export function useCitations(
  briefingId: string | undefined,
  token: string | undefined
): UseCitationsResult {
  const [citationMap, setCitationMap] = useState<CitationMap>({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    if (!briefingId || !token) return;

    if (cache.has(briefingId)) {
      setCitationMap(cache.get(briefingId)!);
      return;
    }

    abortRef.current?.abort();
    abortRef.current = new AbortController();

    setIsLoading(true);
    setError(null);

    fetchCitations(briefingId, token)
      .then((res) => {
        const map = buildCitationMap(res);
        cache.set(briefingId, map);
        setCitationMap(map);
      })
      .catch((err: Error) => {
        if (err.name !== 'AbortError') {
          setError(err.message);
        }
      })
      .finally(() => setIsLoading(false));

    return () => abortRef.current?.abort();
  }, [briefingId, token]);

  return { citationMap, isLoading, error };
}
