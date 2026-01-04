'use client';

interface DocumentViewerProps {
  title: string;
  content: string;
  metadata?: Record<string, any>;
}

export default function DocumentViewer({ title, content, metadata }: DocumentViewerProps) {
  return (
    <div style={styles.container}>
      <h3 style={styles.title}>{title}</h3>
      {metadata && Object.keys(metadata).length > 0 && (
        <div style={styles.metadata}>
          {Object.entries(metadata).map(([key, value]) => (
            <div key={key} style={styles.metadataItem}>
              <span style={styles.metadataKey}>{key}:</span>
              <span style={styles.metadataValue}>{String(value)}</span>
            </div>
          ))}
        </div>
      )}
      <div style={styles.content}>
        {content.split('\n').map((line, idx) => (
          <p key={idx} style={styles.paragraph}>
            {line}
          </p>
        ))}
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    background: 'white',
    border: '1px solid #e5e7eb',
    borderRadius: '8px',
    padding: '1.5rem',
    marginTop: '1rem',
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
  },
  title: {
    fontSize: '1.25rem',
    fontWeight: '600',
    marginBottom: '1rem',
    color: '#111827',
  },
  metadata: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.5rem',
    padding: '1rem',
    background: '#f9fafb',
    borderRadius: '6px',
    marginBottom: '1rem',
  },
  metadataItem: {
    display: 'flex',
    gap: '0.5rem',
    fontSize: '0.875rem',
  },
  metadataKey: {
    fontWeight: '600',
    color: '#6b7280',
    minWidth: '100px',
  },
  metadataValue: {
    color: '#374151',
  },
  content: {
    lineHeight: '1.6',
    color: '#374151',
  },
  paragraph: {
    marginBottom: '0.75rem',
  },
};
