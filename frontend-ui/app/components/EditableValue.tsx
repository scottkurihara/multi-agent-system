'use client';

import { useState } from 'react';

interface EditableValueProps {
  label: string;
  value: string;
  field_type?: 'text' | 'number' | 'date';
  onSave: (newValue: string) => void;
}

export default function EditableValue({
  label,
  value,
  field_type = 'text',
  onSave,
}: EditableValueProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [currentValue, setCurrentValue] = useState(value);
  const [savedValue, setSavedValue] = useState(value);

  const handleSave = () => {
    setSavedValue(currentValue);
    setIsEditing(false);
    onSave(currentValue);
  };

  const handleCancel = () => {
    setCurrentValue(savedValue);
    setIsEditing(false);
  };

  return (
    <div style={styles.container}>
      <label style={styles.label}>{label}</label>
      {isEditing ? (
        <div style={styles.editContainer}>
          <input
            type={field_type}
            value={currentValue}
            onChange={(e) => setCurrentValue(e.target.value)}
            style={styles.input}
            autoFocus
          />
          <div style={styles.buttons}>
            <button onClick={handleSave} style={styles.saveButton}>
              Save
            </button>
            <button onClick={handleCancel} style={styles.cancelButton}>
              Cancel
            </button>
          </div>
        </div>
      ) : (
        <div style={styles.valueContainer}>
          <span style={styles.value}>{savedValue}</span>
          <button onClick={() => setIsEditing(true)} style={styles.editButton}>
            Edit
          </button>
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
  label: {
    display: 'block',
    fontSize: '0.75rem',
    fontWeight: '700',
    color: '#00f5d4',
    marginBottom: '0.75rem',
    fontFamily: '"JetBrains Mono", monospace',
    letterSpacing: '0.1em',
    textTransform: 'uppercase',
  },
  valueContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: '1.25rem',
  },
  value: {
    fontSize: '1.125rem',
    color: '#e8ecf4',
    flex: 1,
    fontWeight: '500',
  },
  editButton: {
    padding: '0.625rem 1.25rem',
    fontSize: '0.8rem',
    fontWeight: '600',
    color: '#00f5d4',
    background: 'rgba(0, 245, 212, 0.1)',
    border: '2px solid #00f5d4',
    cursor: 'pointer',
    fontFamily: '"JetBrains Mono", monospace',
    letterSpacing: '0.05em',
    textTransform: 'uppercase',
    transition: 'all 0.3s',
    clipPath: 'polygon(6px 0, 100% 0, 100% 100%, 0 100%, 0 6px)',
  },
  editContainer: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem',
  },
  input: {
    width: '100%',
    padding: '1rem',
    fontSize: '1rem',
    border: '2px solid #00f5d4',
    background: 'rgba(10, 14, 26, 0.5)',
    color: '#e8ecf4',
    outline: 'none',
    fontFamily: 'inherit',
    clipPath: 'polygon(8px 0, 100% 0, 100% 100%, 0 100%, 0 8px)',
  },
  buttons: {
    display: 'flex',
    gap: '0.75rem',
  },
  saveButton: {
    padding: '0.75rem 1.5rem',
    fontSize: '0.8rem',
    fontWeight: '600',
    color: '#0a0e1a',
    background: 'linear-gradient(135deg, #fee440 0%, #f9d423 100%)',
    border: 'none',
    cursor: 'pointer',
    fontFamily: '"JetBrains Mono", monospace',
    letterSpacing: '0.05em',
    textTransform: 'uppercase',
    clipPath: 'polygon(6px 0, 100% 0, 100% 100%, 0 100%, 0 6px)',
    boxShadow: '0 4px 12px rgba(254, 228, 64, 0.3)',
  },
  cancelButton: {
    padding: '0.75rem 1.5rem',
    fontSize: '0.8rem',
    fontWeight: '600',
    color: '#8892a6',
    background: 'rgba(136, 146, 166, 0.1)',
    border: '2px solid rgba(136, 146, 166, 0.3)',
    cursor: 'pointer',
    fontFamily: '"JetBrains Mono", monospace',
    letterSpacing: '0.05em',
    textTransform: 'uppercase',
    clipPath: 'polygon(6px 0, 100% 0, 100% 100%, 0 100%, 0 6px)',
  },
};
