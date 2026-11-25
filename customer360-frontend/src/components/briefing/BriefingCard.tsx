import React from 'react';
import type { BriefingResponse } from '../../types/briefing';

const STATUS_CONFIG: Record<
  string,
  { label: string; color: string; bg: string }
> = {
  COMPLETED: { label: 'Hoàn thành', color: '#137333', bg: '#e6f4ea' },
  GENERATING: { label: 'Đang tạo...', color: '#b06000', bg: '#fef7e0' },
  FAILED: { label: 'Thất bại', color: '#c5221f', bg: '#fce8e6' },
  BLOCKED: { label: 'Bị chặn', color: '#5f6368', bg: '#f1f3f4' },
};

const VALIDATION_CONFIG: Record<string, { label: string; color: string }> = {
  PASSED: { label: '✓ Đã xác minh', color: '#137333' },
  FAILED: { label: '✗ Xác minh thất bại', color: '#c5221f' },
  BLOCKED: { label: '⊘ Bị chặn', color: '#b06000' },
  PENDING: { label: '⏳ Chờ xác minh', color: '#5f6368' },
};

interface BriefingCardProps {
  briefing: BriefingResponse;
  accountName?: string;
  onView?: () => void;
  onExport?: () => void;
  isExporting?: boolean;
}

export const BriefingCard: React.FC<BriefingCardProps> = ({
  briefing,
  accountName,
  onView,
  onExport,
  isExporting = false,
}) => {
  const statusCfg = STATUS_CONFIG[briefing.status] ?? STATUS_CONFIG.FAILED;
  const validCfg =
    VALIDATION_CONFIG[briefing.validation_status] ?? VALIDATION_CONFIG.PENDING;
  const createdAt = new Date(briefing.created_at).toLocaleString('vi-VN');

  return (
    <div style={s.card}>
      <div style={s.header}>
        <div style={s.headerLeft}>
          <h2 style={s.accountName}>
            {accountName ?? briefing.account_id}
          </h2>
          {briefing.is_stale && (
            <span style={s.staleTag}>⚠ Dữ liệu cũ</span>
          )}
        </div>
        <div style={s.badges}>
          <span
            style={{
              ...s.badge,
              color: statusCfg.color,
              background: statusCfg.bg,
            }}
          >
            {statusCfg.label}
          </span>
          <span style={{ ...s.validBadge, color: validCfg.color }}>
            {validCfg.label}
          </span>
        </div>
      </div>

      <div style={s.meta}>
        <span>🕐 {createdAt}</span>
        {briefing.site_id && <span>📍 Site: {briefing.site_id}</span>}
      </div>

      {briefing.status === 'COMPLETED' && (
        <div style={s.actions}>
          {onView && (
            <button style={s.btnPrimary} onClick={onView} type="button">
              Xem Briefing
            </button>
          )}
          {onExport && (
            <button
              style={isExporting ? { ...s.btnSecondary, opacity: 0.6 } : s.btnSecondary}
              onClick={onExport}
              disabled={isExporting}
              type="button"
            >
              {isExporting ? '⏳ Đang xuất...' : '⬇ Xuất PDF'}
            </button>
          )}
        </div>
      )}
    </div>
  );
};

const s: Record<string, React.CSSProperties> = {
  card: {
    background: '#fff',
    border: '1px solid #dadce0',
    borderRadius: 10,
    padding: '20px 24px',
    boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    gap: 12,
    flexWrap: 'wrap',
  },
  headerLeft: { display: 'flex', alignItems: 'center', gap: 10 },
  accountName: { margin: 0, fontSize: '1.1rem', fontWeight: 700, color: '#202124' },
  staleTag: {
    fontSize: '0.72rem',
    padding: '2px 8px',
    background: '#fef7e0',
    color: '#b06000',
    borderRadius: 4,
    border: '1px solid #f9d05e',
  },
  badges: { display: 'flex', gap: 8, flexWrap: 'wrap' },
  badge: {
    fontSize: '0.72rem',
    fontWeight: 600,
    padding: '3px 10px',
    borderRadius: 999,
  },
  validBadge: {
    fontSize: '0.75rem',
    fontWeight: 500,
    padding: '3px 0',
  },
  meta: {
    display: 'flex',
    gap: 20,
    marginTop: 10,
    fontSize: '0.78rem',
    color: '#5f6368',
  },
  actions: { display: 'flex', gap: 10, marginTop: 16 },
  btnPrimary: {
    padding: '8px 18px',
    background: '#1a73e8',
    color: '#fff',
    border: 'none',
    borderRadius: 6,
    fontSize: '0.875rem',
    fontWeight: 500,
    cursor: 'pointer',
  },
  btnSecondary: {
    padding: '8px 18px',
    background: '#fff',
    color: '#1a73e8',
    border: '1px solid #1a73e8',
    borderRadius: 6,
    fontSize: '0.875rem',
    fontWeight: 500,
    cursor: 'pointer',
  },
};

export default BriefingCard;
