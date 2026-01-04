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
    marginBottom: '0.5rem',
    color: '#111827',
  },
  description: {
    fontSize: '1rem',
    color: '#4b5563',
    marginBottom: '1rem',
    lineHeight: '1.5',
  },
  options: {
    display: 'flex',
    gap: '0.75rem',
    flexWrap: 'wrap',
  },
  button: {
    padding: '0.75rem 1.5rem',
    fontSize: '0.875rem',
    fontWeight: '500',
    color: 'white',
    background: '#3b82f6',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    transition: 'all 0.2s',
  },
  buttonSelected: {
    background: '#059669',
  },
  buttonDisabled: {
    background: '#d1d5db',
    cursor: 'not-allowed',
  },
  confirmation: {
    marginTop: '1rem',
    padding: '0.75rem',
    background: '#d1fae5',
    borderRadius: '6px',
    fontSize: '0.875rem',
    color: '#065f46',
  },
};
