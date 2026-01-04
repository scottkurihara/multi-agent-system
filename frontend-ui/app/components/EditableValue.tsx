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
    background: 'white',
    border: '1px solid #e5e7eb',
    borderRadius: '8px',
    padding: '1.5rem',
    marginTop: '1rem',
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
  },
  label: {
    display: 'block',
    fontSize: '0.875rem',
    fontWeight: '600',
    color: '#374151',
    marginBottom: '0.5rem',
  },
  valueContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: '1rem',
  },
  value: {
    fontSize: '1rem',
    color: '#111827',
    flex: 1,
  },
  editButton: {
    padding: '0.5rem 1rem',
    fontSize: '0.875rem',
    fontWeight: '500',
    color: '#3b82f6',
    background: 'white',
    border: '1px solid #3b82f6',
    borderRadius: '6px',
    cursor: 'pointer',
  },
  editContainer: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.75rem',
  },
  input: {
    width: '100%',
    padding: '0.75rem',
    fontSize: '1rem',
    border: '2px solid #3b82f6',
    borderRadius: '6px',
    outline: 'none',
  },
  buttons: {
    display: 'flex',
    gap: '0.5rem',
  },
  saveButton: {
    padding: '0.5rem 1rem',
    fontSize: '0.875rem',
    fontWeight: '500',
    color: 'white',
    background: '#059669',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
  },
  cancelButton: {
    padding: '0.5rem 1rem',
    fontSize: '0.875rem',
    fontWeight: '500',
    color: '#6b7280',
    background: '#f3f4f6',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
  },
};
