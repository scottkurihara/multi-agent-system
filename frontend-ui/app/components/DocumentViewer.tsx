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
    background: 'rgba(26, 31, 46, 0.8)',
    border: '2px solid rgba(0, 245, 212, 0.3)',
    padding: '2rem',
    marginTop: '1rem',
    boxShadow: '0 8px 24px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(0, 245, 212, 0.1)',
    backdropFilter: 'blur(10px)',
    clipPath: 'polygon(0 0, calc(100% - 16px) 0, 100% 16px, 100% 100%, 0 100%)',
  },
  title: {
    fontSize: '1.5rem',
    fontWeight: '700',
    marginBottom: '1.25rem',
    color: '#00f5d4',
    fontFamily: '"Syne", sans-serif',
    letterSpacing: '-0.01em',
    textTransform: 'uppercase',
  },
  metadata: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.625rem',
    padding: '1.25rem',
    background: 'rgba(10, 14, 26, 0.5)',
    border: '2px solid rgba(0, 245, 212, 0.2)',
    marginBottom: '1.5rem',
    clipPath: 'polygon(8px 0, 100% 0, 100% 100%, 0 100%, 0 8px)',
  },
  metadataItem: {
    display: 'flex',
    gap: '1rem',
    fontSize: '0.875rem',
    fontFamily: '"JetBrains Mono", monospace',
  },
  metadataKey: {
    fontWeight: '700',
    color: '#8892a6',
    minWidth: '120px',
    letterSpacing: '0.05em',
    textTransform: 'uppercase',
  },
  metadataValue: {
    color: '#e8ecf4',
  },
  content: {
    lineHeight: '1.7',
    color: '#e8ecf4',
  },
  paragraph: {
    marginBottom: '1rem',
  },
};
