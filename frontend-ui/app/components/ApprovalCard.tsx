'use client';

import { useState } from 'react';

interface ApprovalCardProps {
  title: string;
  description: string;
  options: string[];
  onResponse: (option: string) => void;
}

export default function ApprovalCard({
  title,
  description,
  options,
  onResponse,
}: ApprovalCardProps) {
  const [selectedOption, setSelectedOption] = useState<string | null>(null);

  const handleSelect = (option: string) => {
    setSelectedOption(option);
    onResponse(option);
  };

  return (
    <div style={styles.card}>
      <h3 style={styles.title}>{title}</h3>
      <p style={styles.description}>{description}</p>
      <div style={styles.options}>
        {options.map((option, idx) => (
          <button
            key={idx}
            onClick={() => handleSelect(option)}
            disabled={selectedOption !== null}
            style={{
              ...styles.button,
              ...(selectedOption === option ? styles.buttonSelected : {}),
              ...(selectedOption !== null && selectedOption !== option
                ? styles.buttonDisabled
                : {}),
            }}
          >
            {option}
          </button>
        ))}
      </div>
      {selectedOption && (
        <div style={styles.confirmation}>
          Selected: <strong>{selectedOption}</strong>
        </div>
      )}
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  card: {
    background: 'rgba(26, 31, 46, 0.8)',
    border: '2px solid rgba(0, 245, 212, 0.3)',
    padding: '2rem',
    marginTop: '1rem',
    boxShadow: '0 8px 24px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(0, 245, 212, 0.1)',
    backdropFilter: 'blur(10px)',
    clipPath: 'polygon(0 0, calc(100% - 16px) 0, 100% 16px, 100% 100%, 0 100%)',
  },
  title: {
    fontSize: '1.25rem',
    fontWeight: '700',
    marginBottom: '0.75rem',
    color: '#00f5d4',
    fontFamily: '"Syne", sans-serif',
    letterSpacing: '-0.01em',
    textTransform: 'uppercase',
  },
  description: {
    fontSize: '1rem',
    color: '#e8ecf4',
    marginBottom: '1.5rem',
    lineHeight: '1.6',
  },
  options: {
    display: 'flex',
    gap: '1rem',
    flexWrap: 'wrap',
  },
  button: {
    padding: '0.875rem 1.75rem',
    fontSize: '0.875rem',
    fontWeight: '600',
    color: '#0a0e1a',
    background: 'linear-gradient(135deg, #00f5d4 0%, #00d4aa 100%)',
    border: '2px solid transparent',
    cursor: 'pointer',
    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
    fontFamily: '"JetBrains Mono", monospace',
    letterSpacing: '0.02em',
    textTransform: 'uppercase',
    clipPath: 'polygon(8px 0, 100% 0, 100% 100%, 0 100%, 0 8px)',
    boxShadow: '0 4px 12px rgba(0, 245, 212, 0.3)',
  },
  buttonSelected: {
    background: 'linear-gradient(135deg, #fee440 0%, #f9d423 100%)',
    boxShadow: '0 4px 16px rgba(254, 228, 64, 0.5)',
  },
  buttonDisabled: {
    background: 'rgba(136, 146, 166, 0.2)',
    cursor: 'not-allowed',
    boxShadow: 'none',
    color: '#8892a6',
  },
  confirmation: {
    marginTop: '1.5rem',
    padding: '1rem 1.25rem',
    background: 'rgba(254, 228, 64, 0.1)',
    border: '2px solid rgba(254, 228, 64, 0.3)',
    fontSize: '0.875rem',
    color: '#fee440',
    fontFamily: '"JetBrains Mono", monospace',
    clipPath: 'polygon(8px 0, 100% 0, 100% 100%, 0 100%, 0 8px)',
  },
};
