import React from 'react';

interface ErrorBannerProps {
  message: string;
  onRetry?: () => void;
}

export const ErrorBanner: React.FC<ErrorBannerProps> = ({ message, onRetry }) => (
  <div style={styles.container} role="alert">
    <span style={styles.icon}>⚠️</span>
    <div style={styles.body}>
      <p style={styles.message}>{message}</p>
      {onRetry && (
        <button style={styles.retryBtn} onClick={onRetry} type="button">
          Thử lại
        </button>
      )}
    </div>
  </div>
);

const styles: Record<string, React.CSSProperties> = {
  container: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: 12,
    padding: '14px 18px',
    background: '#fce8e6',
    border: '1px solid #f5c6c2',
    borderRadius: 8,
    margin: '12px 0',
  },
  icon: { fontSize: 18, lineHeight: 1.4 },
  body: { flex: 1 },
  message: { margin: 0, color: '#c5221f', fontSize: '0.875rem', lineHeight: 1.5 },
  retryBtn: {
    marginTop: 8,
    padding: '4px 12px',
    fontSize: '0.8rem',
    background: '#c5221f',
    color: '#fff',
    border: 'none',
    borderRadius: 4,
    cursor: 'pointer',
  },
};

export default ErrorBanner;
