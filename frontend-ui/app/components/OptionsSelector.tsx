'use client';

import { useState } from 'react';

interface OptionsSelectorProps {
  question: string;
  options: string[];
  onSelect: (option: string) => void;
}

export default function OptionsSelector({ question, options, onSelect }: OptionsSelectorProps) {
  const [selectedOption, setSelectedOption] = useState<string | null>(null);

  const handleSelect = (option: string) => {
    setSelectedOption(option);
    onSelect(option);
  };

  return (
    <div style={styles.container}>
      <h3 style={styles.question}>{question}</h3>
      <div style={styles.options}>
        {options.map((option, idx) => (
          <button
            key={idx}
            onClick={() => handleSelect(option)}
            disabled={selectedOption !== null}
            style={{
              ...styles.option,
              ...(selectedOption === option ? styles.optionSelected : {}),
              ...(selectedOption !== null && selectedOption !== option
                ? styles.optionDisabled
                : {}),
            }}
          >
            <span style={styles.optionNumber}>{idx + 1}</span>
            <span style={styles.optionText}>{option}</span>
          </button>
        ))}
      </div>
      {selectedOption && (
        <div style={styles.confirmation}>
          You selected: <strong>{selectedOption}</strong>
        </div>
      )}
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
  question: {
    fontSize: '1.25rem',
    fontWeight: '700',
    marginBottom: '1.5rem',
    color: '#00f5d4',
    fontFamily: '"Syne", sans-serif',
    letterSpacing: '-0.01em',
    textTransform: 'uppercase',
  },
  options: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem',
  },
  option: {
    display: 'flex',
    alignItems: 'center',
    gap: '1.25rem',
    padding: '1.25rem',
    fontSize: '1rem',
    color: '#e8ecf4',
    background: 'rgba(10, 14, 26, 0.5)',
    border: '2px solid rgba(0, 245, 212, 0.2)',
    cursor: 'pointer',
    textAlign: 'left',
    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
    clipPath: 'polygon(8px 0, 100% 0, 100% 100%, 0 100%, 0 8px)',
  },
  optionSelected: {
    background:
      'linear-gradient(135deg, rgba(254, 228, 64, 0.15) 0%, rgba(0, 245, 212, 0.15) 100%)',
    borderColor: '#fee440',
    color: '#e8ecf4',
    boxShadow: '0 4px 12px rgba(254, 228, 64, 0.3)',
  },
  optionDisabled: {
    background: 'rgba(26, 31, 46, 0.3)',
    borderColor: 'rgba(136, 146, 166, 0.2)',
    color: '#8892a6',
    cursor: 'not-allowed',
  },
  optionNumber: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    width: '40px',
    height: '40px',
    background: 'linear-gradient(135deg, #00f5d4 0%, #00d4aa 100%)',
    color: '#0a0e1a',
    fontSize: '0.875rem',
    fontWeight: '700',
    fontFamily: '"JetBrains Mono", monospace',
    clipPath: 'polygon(30% 0%, 70% 0%, 100% 30%, 100% 70%, 70% 100%, 30% 100%, 0% 70%, 0% 30%)',
  },
  optionText: {
    flex: 1,
    lineHeight: '1.5',
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
