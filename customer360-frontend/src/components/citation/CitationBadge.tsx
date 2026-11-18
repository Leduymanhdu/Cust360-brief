import React, {
  useState,
  useRef,
  useEffect,
  useCallback,
  useId,
} from 'react';
import type { Citation } from '../../types/briefing';
import styles from './CitationBadge.module.css';

const PDFIcon = () => (
  <svg
    width="12"
    height="12"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
  >
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
    <polyline points="14 2 14 8 20 8" />
    <line x1="16" y1="13" x2="8" y2="13" />
    <line x1="16" y1="17" x2="8" y2="17" />
    <polyline points="10 9 9 9 8 9" />
  </svg>
);

const CSVIcon = () => (
  <svg
    width="12"
    height="12"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
  >
    <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
    <line x1="3" y1="9" x2="21" y2="9" />
    <line x1="3" y1="15" x2="21" y2="15" />
    <line x1="9" y1="3" x2="9" y2="21" />
  </svg>
);

interface CitationBadgeProps {
  citationNumber: number;
  citation?: Citation;
  isLoading?: boolean;
}

export const CitationBadge: React.FC<CitationBadgeProps> = ({
  citationNumber,
  citation,
  isLoading = false,
}) => {
  const [visible, setVisible] = useState(false);
  const [pinned, setPinned] = useState(false);
  const [placement, setPlacement] = useState<'top' | 'bottom'>('top');

  const badgeRef = useRef<HTMLButtonElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);
  const tooltipId = useId();

  const updatePlacement = useCallback(() => {
    if (!badgeRef.current) return;
    const rect = badgeRef.current.getBoundingClientRect();
    setPlacement(rect.top > 180 ? 'top' : 'bottom');
  }, []);

  const show = useCallback(() => {
    updatePlacement();
    setVisible(true);
  }, [updatePlacement]);

  const hide = useCallback(() => {
    if (!pinned) setVisible(false);
  }, [pinned]);

  const togglePin = useCallback(() => {
    setPinned((prev) => {
      const next = !prev;
      if (!next) setVisible(false);
      return next;
    });
    updatePlacement();
    setVisible(true);
  }, [updatePlacement]);

  useEffect(() => {
    if (!pinned) return;

    const handleClickOutside = (e: MouseEvent) => {
      if (
        badgeRef.current &&
        !badgeRef.current.contains(e.target as Node) &&
        tooltipRef.current &&
        !tooltipRef.current.contains(e.target as Node)
      ) {
        setPinned(false);
        setVisible(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [pinned]);

  useEffect(() => {
    if (!visible) return;
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setPinned(false);
        setVisible(false);
        badgeRef.current?.focus();
      }
    };
    document.addEventListener('keydown', handleEsc);
    return () => document.removeEventListener('keydown', handleEsc);
  }, [visible]);

  if (isLoading) {
    return (
      <span className={styles.badgeSkeleton} aria-hidden="true">
        [·]
      </span>
    );
  }

  if (!citation) {
    return (
      <span
        className={`${styles.badge} ${styles.badgeUnknown}`}
        title={`Không tìm thấy trích dẫn [${citationNumber}]`}
      >
        [{citationNumber}]
      </span>
    );
  }

  const sourceLabel = citation.source_type === 'PDF' ? 'PDF' : 'CSV / Thương mại';
  const SourceIcon = citation.source_type === 'PDF' ? PDFIcon : CSVIcon;

  return (
    <span className={styles.wrapper}>
      <button
        ref={badgeRef}
        type="button"
        className={`${styles.badge} ${pinned ? styles.badgePinned : ''}`}
        aria-label={`Trích dẫn số ${citationNumber}`}
        aria-describedby={visible ? tooltipId : undefined}
        aria-expanded={visible}
        onMouseEnter={show}
        onMouseLeave={hide}
        onFocus={show}
        onBlur={hide}
        onClick={togglePin}
      >
        [{citationNumber}]
      </button>

      {visible && (
        <div
          ref={tooltipRef}
          id={tooltipId}
          role="tooltip"
          className={`${styles.tooltip} ${
            placement === 'bottom' ? styles.tooltipBottom : styles.tooltipTop
          } ${pinned ? styles.tooltipPinned : ''}`}
          onMouseEnter={() => setVisible(true)}
          onMouseLeave={hide}
        >
          <span
            className={`${styles.arrow} ${
              placement === 'bottom' ? styles.arrowBottom : styles.arrowTop
            }`}
          />

          <div className={styles.sourceBadge}>
            <SourceIcon />
            <span>{sourceLabel}</span>
            {citation.source_type === 'PDF' && citation.page_number != null && (
              <span className={styles.pageNumber}>
                · Trang {citation.page_number}
              </span>
            )}
          </div>

          <p className={styles.claimText}>{citation.claim_text}</p>

          {citation.source_excerpt && (
            <blockquote className={styles.excerpt}>
              "{citation.source_excerpt}"
            </blockquote>
          )}

          {citation.source_name && (
            <div className={styles.sourceName}>
              📄 {citation.source_name}
            </div>
          )}

          {citation.validation_status !== 'PENDING' && (
            <div
              className={`${styles.validationBadge} ${
                styles[`validation_${citation.validation_status.toLowerCase()}`]
              }`}
            >
              {citation.validation_status === 'VALID' && '✓ Đã xác minh'}
              {citation.validation_status === 'INVALID' && '✗ Không hợp lệ'}
              {citation.validation_status === 'REJECTED' && '⊘ Bị từ chối'}
            </div>
          )}
        </div>
      )}
    </span>
  );
};

export default CitationBadge;
