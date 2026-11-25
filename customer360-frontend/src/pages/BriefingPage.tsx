import React, { useState } from 'react';
import { useBriefing } from '../../hooks/useBriefing';
import { useCitations } from '../../hooks/useCitations';
import { useExportPdf } from '../../hooks/useExportPdf';
import { BriefingCard } from '../../components/briefing/BriefingCard';
import { BriefingView } from '../../components/briefing/BriefingView';
import { CitationsPanel } from '../../components/briefing/CitationsPanel';
import { LoadingSpinner } from '../../components/ui/LoadingSpinner';
import { ErrorBanner } from '../../components/ui/ErrorBanner';
import { EmptyState } from '../../components/ui/EmptyState';

const DEMO_TOKEN = 'demo-sales-token';
const DEMO_BRIEFING_ID = '40000000-0000-4000-8000-000000000001';

type TabId = 'briefing' | 'citations';

export default function BriefingPage() {
  const [briefingId, setBriefingId] = useState<string>(DEMO_BRIEFING_ID);
  const [inputId, setInputId] = useState(DEMO_BRIEFING_ID);
  const [activeTab, setActiveTab] = useState<TabId>('briefing');

  const { briefing, isLoading, error, refetch } = useBriefing(briefingId, DEMO_TOKEN);
  const { citations, citationMap, isLoading: citationsLoading, error: citationsError } =
    useCitations(briefingId, DEMO_TOKEN);
  const { exportPdf, isExporting, error: exportError } = useExportPdf();

  const handleExport = () => exportPdf(briefingId, DEMO_TOKEN);
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setBriefingId(inputId.trim());
  };

  return (
    <div style={s.page}>
      <div style={s.topbar}>
        <h1 style={s.pageTitle}>📋 Briefing Assistant</h1>
        <form style={s.searchForm} onSubmit={handleSearch}>
          <input
            style={s.input}
            value={inputId}
            onChange={(e) => setInputId(e.target.value)}
            placeholder="Nhập Briefing ID..."
            aria-label="Briefing ID"
          />
          <button style={s.searchBtn} type="submit">Tìm</button>
        </form>
      </div>

      <div style={s.content}>
        {isLoading && (
          <LoadingSpinner message="Đang tải briefing..." />
        )}

        {!isLoading && error && (
          <ErrorBanner
            message={`Không thể tải briefing: ${error}`}
            onRetry={refetch}
          />
        )}

        {!isLoading && !error && !briefing && (
          <EmptyState
            title="Không tìm thấy Briefing"
            description="Vui lòng kiểm tra lại Briefing ID hoặc tạo briefing mới."
          />
        )}

        {!isLoading && !error && briefing && (
          <>
            <BriefingCard
              briefing={briefing}
              accountName="ABC Vietnam Ltd"
              onView={() => setActiveTab('briefing')}
              onExport={handleExport}
              isExporting={isExporting}
            />

            {exportError && (
              <ErrorBanner message={`Xuất PDF thất bại: ${exportError}`} />
            )}

            {briefing.status === 'GENERATING' && (
              <div style={s.generatingBanner}>
                <LoadingSpinner message="Briefing đang được tạo, vui lòng chờ..." />
              </div>
            )}

            {briefing.status === 'FAILED' && (
              <ErrorBanner
                message="Tạo briefing thất bại. Vui lòng thử lại."
                onRetry={refetch}
              />
            )}

            {briefing.status === 'BLOCKED' && (
              <ErrorBanner message="Briefing bị chặn do vi phạm chính sách bảo mật." />
            )}

            {briefing.status === 'COMPLETED' && (
              <>
                <div style={s.tabs} role="tablist">
                  {(['briefing', 'citations'] as TabId[]).map((tab) => (
                    <button
                      key={tab}
                      role="tab"
                      aria-selected={activeTab === tab}
                      style={activeTab === tab ? { ...s.tab, ...s.tabActive } : s.tab}
                      onClick={() => setActiveTab(tab)}
                      type="button"
                    >
                      {tab === 'briefing' ? '📄 Nội dung' : `📎 Nguồn tham chiếu (${citations.length})`}
                    </button>
                  ))}
                </div>

                <div role="tabpanel" style={s.tabPanel}>
                  {activeTab === 'briefing' && (
                    <div style={s.card}>
                      {briefing.is_stale && (
                        <ErrorBanner message="⚠ Dữ liệu briefing này có thể đã cũ so với dữ liệu nguồn mới nhất." />
                      )}
                      <BriefingView
                        briefing={briefing}
                        citationMap={citationMap}
                        isLoadingCitations={citationsLoading}
                      />
                      {citationsError && (
                        <ErrorBanner message={`Không thể tải citations: ${citationsError}`} />
                      )}
                    </div>
                  )}

                  {activeTab === 'citations' && (
                    <CitationsPanel
                      citations={citations}
                      isLoading={citationsLoading}
                    />
                  )}
                </div>
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
}

const s: Record<string, React.CSSProperties> = {
  page: {
    minHeight: '100vh',
    background: '#f8f9fa',
    fontFamily: "'Inter', 'Roboto', system-ui, sans-serif",
  },
  topbar: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '14px 32px',
    background: '#fff',
    borderBottom: '1px solid #dadce0',
    flexWrap: 'wrap',
    gap: 12,
    position: 'sticky',
    top: 0,
    zIndex: 100,
  },
  pageTitle: {
    margin: 0,
    fontSize: '1.2rem',
    fontWeight: 700,
    color: '#202124',
  },
  searchForm: {
    display: 'flex',
    gap: 8,
  },
  input: {
    padding: '7px 12px',
    border: '1px solid #dadce0',
    borderRadius: 6,
    fontSize: '0.85rem',
    width: 300,
    color: '#202124',
    outline: 'none',
  },
  searchBtn: {
    padding: '7px 16px',
    background: '#1a73e8',
    color: '#fff',
    border: 'none',
    borderRadius: 6,
    fontSize: '0.85rem',
    cursor: 'pointer',
  },
  content: {
    maxWidth: 900,
    margin: '0 auto',
    padding: '28px 24px',
    display: 'flex',
    flexDirection: 'column',
    gap: 20,
  },
  generatingBanner: {
    background: '#fff',
    border: '1px solid #dadce0',
    borderRadius: 10,
    padding: 12,
  },
  tabs: {
    display: 'flex',
    gap: 4,
    borderBottom: '2px solid #e8eaed',
  },
  tab: {
    padding: '10px 20px',
    border: 'none',
    background: 'none',
    cursor: 'pointer',
    fontSize: '0.875rem',
    fontWeight: 500,
    color: '#5f6368',
    borderBottom: '2px solid transparent',
    marginBottom: -2,
    transition: 'color 0.15s',
  },
  tabActive: {
    color: '#1a73e8',
    borderBottom: '2px solid #1a73e8',
  },
  tabPanel: {
    marginTop: 4,
  },
  card: {
    background: '#fff',
    border: '1px solid #dadce0',
    borderRadius: 10,
    padding: '20px 24px',
    boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
  },
};
