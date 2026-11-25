import React from 'react';

interface EmptyStateProps {
  title?: string;
  description?: string;
  action?: React.ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title = 'Không có dữ liệu',
  description,
  action,
}) => (
  <div style={styles.container}>
    <span style={styles.icon}>📭</span>
    <h3 style={styles.title}>{title}</h3>
    {description && <p style={styles.description}>{description}</p>}
    {action && <div style={styles.action}>{action}</div>}
  </div>
);

const styles: Record<string, React.CSSProperties> = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: '48px 24px',
    gap: 10,
    textAlign: 'center',
    color: '#5f6368',
  },
  icon: { fontSize: 48, lineHeight: 1 },
  title: { margin: 0, fontSize: '1rem', fontWeight: 600, color: '#3c4043' },
  description: { margin: 0, fontSize: '0.85rem', maxWidth: 360 },
  action: { marginTop: 8 },
};

export default EmptyState;
