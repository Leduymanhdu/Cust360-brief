import { useEffect, useState } from "react";
import { BriefingStatement } from "../components/citation/BriefingStatement";
import { useCitations } from "../hooks/useCitations";
import type { ApiBriefingResponse } from "../types/briefing";
import "../styles/briefing.css";

interface BriefingPageProps {
  briefingId: string;
  token: string;
}

const API_BASE =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

export default function BriefingPage({ briefingId, token }: BriefingPageProps) {
  const [briefing, setBriefing] = useState<ApiBriefingResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { citationMap, isLoading: isLoadingCitations, error: citationsError } =
    useCitations(briefingId, token);

  useEffect(() => {
    const controller = new AbortController();
    setIsLoading(true);
    setError(null);
    fetch(`${API_BASE}/briefings/${encodeURIComponent(briefingId)}`, {
      headers: { Authorization: `Bearer ${token}` },
      signal: controller.signal,
    })
      .then(async (response) => {
        if (!response.ok) {
          const body = await response.json().catch(() => ({}));
          throw new Error(body.detail ?? `Không thể tải briefing (${response.status}).`);
        }
        return response.json() as Promise<ApiBriefingResponse>;
      })
      .then(setBriefing)
      .catch((cause: Error) => {
        if (cause.name !== "AbortError") setError(cause.message);
      })
      .finally(() => {
        if (!controller.signal.aborted) setIsLoading(false);
      });

    return () => controller.abort();
  }, [briefingId, token]);

  if (isLoading) return <main className="briefing-page">Đang tải briefing...</main>;
  if (error) return <main className="briefing-page" role="alert">{error}</main>;
  if (!briefing) return <main className="briefing-page">Không tìm thấy briefing.</main>;

  return (
    <main className="briefing-page">
      <header className="briefing-header">
        <h1>Customer 360 Briefing</h1>
        <p>Account: {briefing.account_id}</p>
        <p>Status: {briefing.status} · Validation: {briefing.validation_status}</p>
      </header>
      <div className="briefing-content">
        {Object.entries(briefing.sections).map(([key, section]) => (
          <section className="card" key={key}>
            <h2>{key.replaceAll("_", " ")}</h2>
            <BriefingStatement
              text={section.content}
              citationNumbers={section.citations}
              citationMap={citationMap}
              isLoadingCitations={isLoadingCitations}
            />
          </section>
        ))}
        {citationsError ? <p role="alert">{citationsError}</p> : null}
      </div>
      <footer className="briefing-footer briefing-screen-only">
        <span>Briefing reference {briefing.briefing_id}</span>
        <span>Created {new Date(briefing.created_at).toLocaleString()}</span>
      </footer>
    </main>
  );
}
