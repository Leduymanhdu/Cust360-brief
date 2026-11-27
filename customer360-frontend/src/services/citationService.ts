import type { CitationsResponse, CitationMap } from '../types/briefing';

const API_BASE =
  import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1';

export async function fetchCitations(
  briefingId: string,
  token: string,
  signal?: AbortSignal
): Promise<CitationsResponse> {
  const res = await fetch(`${API_BASE}/briefings/${briefingId}/citations`, {
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    signal,
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(`fetchCitations [${res.status}]: ${body}`);
  }

  return res.json() as Promise<CitationsResponse>;
}

export function buildCitationMap(response: CitationsResponse): CitationMap {
  return Object.fromEntries(
    response.citations.map((c) => [c.citation_number, c])
  );
}
