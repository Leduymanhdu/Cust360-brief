// ============================================================
// citationService.ts – API calls cho Citations
// KAN-20: FR-BRF-003 – GET /briefings/{id}/citations
// ============================================================

import type { CitationsResponse, CitationMap } from '../types/briefing';

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';

/**
 * Lấy danh sách citations của một briefing.
 * Endpoint: GET /briefings/{briefingId}/citations
 * Auth: Bearer token (JWT) – phải truyền trong header Authorization.
 */
export async function fetchCitations(
  briefingId: string,
  token: string
): Promise<CitationsResponse> {
  const res = await fetch(`${API_BASE}/briefings/${briefingId}/citations`, {
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(`fetchCitations [${res.status}]: ${body}`);
  }

  return res.json() as Promise<CitationsResponse>;
}

/**
 * Chuyển đổi mảng citations thành map citation_number → Citation
 * để lookup O(1) khi render tooltip.
 */
export function buildCitationMap(response: CitationsResponse): CitationMap {
  return Object.fromEntries(
    response.citations.map((c) => [c.citation_number, c])
  );
}
