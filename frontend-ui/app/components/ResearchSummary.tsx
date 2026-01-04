'use client';

interface ResearchSummaryProps {
  title: string;
  findings: string[];
}

export default function ResearchSummary({ title, findings }: ResearchSummaryProps) {
  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <span style={styles.icon}>🔍</span>
        <h3 style={styles.title}>{title}</h3>
      </div>
      <div style={styles.findings}>
        {findings.map((finding, idx) => (
          <div key={idx} style={styles.finding}>
            <span style={styles.bullet}>•</span>
            <span style={styles.findingText}>{finding}</span>
          </div>
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
  header: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem',
    marginBottom: '1rem',
  },
  icon: {
    fontSize: '1.5rem',
  },
  title: {
    fontSize: '1.25rem',
    fontWeight: '600',
    color: '#111827',
  },
  findings: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.75rem',
  },
  finding: {
    display: 'flex',
    gap: '0.75rem',
    padding: '0.75rem',
    background: '#f0f9ff',
    borderLeft: '3px solid #3b82f6',
    borderRadius: '4px',
  },
  bullet: {
    color: '#3b82f6',
    fontWeight: 'bold',
    fontSize: '1.25rem',
  },
  findingText: {
    flex: 1,
    color: '#374151',
    lineHeight: '1.5',
  },
};
