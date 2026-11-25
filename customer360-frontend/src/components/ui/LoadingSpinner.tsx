import React from 'react';

export const LoadingSpinner: React.FC<{ message?: string }> = ({
  message = 'Đang tải...',
}) => (
  <div style={styles.container}>
    <div style={styles.spinner} />
    <p style={styles.text}>{message}</p>
  </div>
);

const styles: Record<string, React.CSSProperties> = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '48px 24px',
    gap: 16,
  },
  spinner: {
    width: 40,
    height: 40,
    border: '3px solid #e8f0fe',
    borderTop: '3px solid #1a73e8',
    borderRadius: '50%',
    animation: 'spin 0.8s linear infinite',
  },
  text: {
    color: '#5f6368',
    fontSize: '0.9rem',
    margin: 0,
  },
};

export default LoadingSpinner;
