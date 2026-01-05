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
    background: 'rgba(26, 31, 46, 0.8)',
    border: '2px solid rgba(0, 245, 212, 0.3)',
    padding: '2rem',
    marginTop: '1rem',
    boxShadow: '0 8px 24px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(0, 245, 212, 0.1)',
    backdropFilter: 'blur(10px)',
    clipPath: 'polygon(0 0, calc(100% - 16px) 0, 100% 16px, 100% 100%, 0 100%)',
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    gap: '1rem',
    marginBottom: '1.5rem',
  },
  icon: {
    fontSize: '2rem',
    filter: 'drop-shadow(0 0 8px rgba(0, 245, 212, 0.5))',
  },
  title: {
    fontSize: '1.5rem',
    fontWeight: '700',
    color: '#00f5d4',
    fontFamily: '"Syne", sans-serif',
    letterSpacing: '-0.01em',
    textTransform: 'uppercase',
  },
  findings: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem',
  },
  finding: {
    display: 'flex',
    gap: '1rem',
    padding: '1rem 1.25rem',
    background: 'rgba(10, 14, 26, 0.5)',
    borderLeft: '4px solid #00f5d4',
    clipPath: 'polygon(8px 0, 100% 0, 100% 100%, 0 100%, 0 8px)',
  },
  bullet: {
    color: '#fee440',
    fontWeight: 'bold',
    fontSize: '1.5rem',
    lineHeight: '1',
  },
  findingText: {
    flex: 1,
    color: '#e8ecf4',
    lineHeight: '1.6',
  },
};
