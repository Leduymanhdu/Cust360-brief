import React, { useState } from 'react';
import type { CitationItem } from '../../types/briefing';
import { EmptyState } from '../ui/EmptyState';

const SOURCE_CONFIG = {
  PDF: { label: 'PDF', color: '#c5221f', bg: '#fce8e6' },
  COMMERCIAL: { label: 'CSV / Thương mại', color: '#1a73e8', bg: '#e8f0fe' },
};

const VALIDATION_CONFIG: Record<string, { label: string; color: string }> = {
  VALID: { label: '✓ Hợp lệ', color: '#137333' },
  INVALID: { label: '✗ Không hợp lệ', color: '#c5221f' },
  REJECTED: { label: '⊘ Bị từ chối', color: '#b06000' },
  PENDING: { label: '⏳ Chờ xác minh', color: '#5f6368' },
};

interface CitationRowProps {
  item: CitationItem;
}

const CitationRow: React.FC<CitationRowProps> = ({ item }) => {
  const [expanded, setExpanded] = useState(false);
  const srcCfg = SOURCE_CONFIG[item.source_type];
  const valCfg = VALIDATION_CONFIG[item.validation_status] ?? VALIDATION_CONFIG.PENDING;

  return (
    <div style={s.row}>
      <div style={s.rowHeader}>
        <span style={s.number}>[{item.citation_number}]</span>

        <div style={s.rowMeta}>
          <span style={{ ...s.srcBadge, color: srcCfg.color, background: srcCfg.bg }}>
            {srcCfg.label}
          </span>
          {item.source_type === 'PDF' && item.page_number != null && (
            <span style={s.page}>Trang {item.page_number}</span>
          )}
          <span style={{ ...s.valBadge, color: valCfg.color }}>{valCfg.label}</span>
        </div>

        <button
          style={s.expandBtn}
          onClick={() => setExpanded((p) => !p)}
          type="button"
          aria-expanded={expanded}
        >
          {expanded ? '▲' : '▼'}
        </button>
      </div>

      <p style={s.claimText}>{item.claim_text}</p>

      {expanded && (
        <div style={s.detail}>
          {item.source_excerpt ? (
            <blockquote style={s.excerpt}>"{item.source_excerpt}"</blockquote>
          ) : (
            <p style={s.noExcerpt}>Không có đoạn trích.</p>
          )}
        </div>
      )}
    </div>
  );
};

interface CitationsPanelProps {
  citations: CitationItem[];
  isLoading?: boolean;
}

export const CitationsPanel: React.FC<CitationsPanelProps> = ({
  citations,
  isLoading = false,
}) => {
  if (isLoading) {
    return (
      <div style={s.panel}>
        {[1, 2, 3].map((i) => (
          <div key={i} style={s.skeleton} />
        ))}
      </div>
    );
  }

  if (!citations.length) {
    return (
      <div style={s.panel}>
        <EmptyState
          title="Không có trích dẫn"
          description="Briefing này chưa có nguồn tham chiếu nào."
        />
      </div>
    );
  }

  return (
    <div style={s.panel}>
      <h3 style={s.panelTitle}>Nguồn tham chiếu ({citations.length})</h3>
      {citations.map((item) => (
        <CitationRow key={item.citation_number} item={item} />
      ))}
    </div>
  );
};

const s: Record<string, React.CSSProperties> = {
  panel: {
    background: '#fff',
    border: '1px solid #dadce0',
    borderRadius: 10,
    padding: '16px 20px',
    boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
  },
  panelTitle: {
    margin: '0 0 14px',
    fontSize: '0.9rem',
    fontWeight: 700,
    color: '#3c4043',
    textTransform: 'uppercase',
    letterSpacing: '0.04em',
  },
  row: {
    padding: '12px 0',
    borderBottom: '1px solid #f1f3f4',
  },
  rowHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: 10,
    flexWrap: 'wrap',
  },
  number: {
    fontSize: '0.75rem',
    fontWeight: 700,
    color: '#1a73e8',
    background: '#e8f0fe',
    padding: '1px 6px',
    borderRadius: 4,
    whiteSpace: 'nowrap',
  },
  rowMeta: { display: 'flex', gap: 8, alignItems: 'center', flex: 1, flexWrap: 'wrap' },
  srcBadge: {
    fontSize: '0.68rem',
    fontWeight: 700,
    textTransform: 'uppercase',
    padding: '2px 8px',
    borderRadius: 999,
  },
  page: { fontSize: '0.72rem', color: '#5f6368' },
  valBadge: { fontSize: '0.72rem', fontWeight: 500 },
  expandBtn: {
    marginLeft: 'auto',
    background: 'none',
    border: 'none',
    cursor: 'pointer',
    color: '#5f6368',
    fontSize: '0.7rem',
    padding: '2px 6px',
  },
  claimText: {
    margin: '8px 0 0',
    fontSize: '0.85rem',
    color: '#202124',
    lineHeight: 1.5,
  },
  detail: { marginTop: 10 },
  excerpt: {
    margin: 0,
    padding: '6px 12px',
    borderLeft: '3px solid #dadce0',
    background: '#f8f9fa',
    fontSize: '0.8rem',
    color: '#5f6368',
    fontStyle: 'italic',
    borderRadius: '0 4px 4px 0',
  },
  noExcerpt: { margin: 0, fontSize: '0.78rem', color: '#9aa0a6', fontStyle: 'italic' },
  skeleton: {
    height: 60,
    background: 'linear-gradient(90deg, #f1f3f4 25%, #e8eaed 50%, #f1f3f4 75%)',
    backgroundSize: '200% 100%',
    animation: 'shimmer 1.2s infinite',
    borderRadius: 6,
    marginBottom: 10,
  },
};

export default CitationsPanel;
