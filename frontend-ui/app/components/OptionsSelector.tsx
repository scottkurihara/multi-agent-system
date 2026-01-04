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
              ...(selectedOption !== null && selectedOption !== option ? styles.optionDisabled : {}),
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
    background: 'white',
    border: '1px solid #e5e7eb',
    borderRadius: '8px',
    padding: '1.5rem',
    marginTop: '1rem',
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
  },
  question: {
    fontSize: '1.125rem',
    fontWeight: '600',
    marginBottom: '1rem',
    color: '#111827',
  },
  options: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.75rem',
  },
  option: {
    display: 'flex',
    alignItems: 'center',
    gap: '1rem',
    padding: '1rem',
    fontSize: '1rem',
    color: '#374151',
    background: '#f9fafb',
    border: '2px solid #e5e7eb',
    borderRadius: '8px',
    cursor: 'pointer',
    textAlign: 'left',
    transition: 'all 0.2s',
  },
  optionSelected: {
    background: '#d1fae5',
    borderColor: '#059669',
    color: '#065f46',
  },
  optionDisabled: {
    background: '#f3f4f6',
    borderColor: '#e5e7eb',
    color: '#9ca3af',
    cursor: 'not-allowed',
  },
  optionNumber: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    width: '32px',
    height: '32px',
    background: '#3b82f6',
    color: 'white',
    borderRadius: '50%',
    fontSize: '0.875rem',
    fontWeight: '600',
  },
  optionText: {
    flex: 1,
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
