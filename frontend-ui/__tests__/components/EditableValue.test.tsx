/**
 * Tests for EditableValue component - Generative UI
 */

import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import EditableValue from '../../app/components/EditableValue';

describe('EditableValue - Generative UI Component', () => {
  const mockOnSave = jest.fn();

  const defaultProps = {
    label: 'Username',
    value: 'john_doe',
    fieldType: 'text' as const,
    onSave: mockOnSave,
  };

  beforeEach(() => {
    mockOnSave.mockClear();
  });

  it('renders label and initial value', () => {
    render(<EditableValue {...defaultProps} />);

    expect(screen.getByText('Username')).toBeInTheDocument();
    expect(screen.getByDisplayValue('john_doe')).toBeInTheDocument();
  });

  it('enables editing when Edit button is clicked', () => {
    render(<EditableValue {...defaultProps} />);

    const editButton = screen.getByText('Edit');
    fireEvent.click(editButton);

    expect(screen.getByText('Save')).toBeInTheDocument();
    expect(screen.getByText('Cancel')).toBeInTheDocument();
  });

  it('calls onSave with new value when Save is clicked', () => {
    render(<EditableValue {...defaultProps} />);

    // Enter edit mode
    fireEvent.click(screen.getByText('Edit'));

    // Change the value
    const input = screen.getByDisplayValue('john_doe');
    fireEvent.change(input, { target: { value: 'jane_doe' } });

    // Save
    fireEvent.click(screen.getByText('Save'));

    expect(mockOnSave).toHaveBeenCalledWith('jane_doe');
  });

  it('cancels editing when Cancel button is clicked', () => {
    render(<EditableValue {...defaultProps} />);

    // Enter edit mode
    fireEvent.click(screen.getByText('Edit'));

    // Change the value
    const input = screen.getByDisplayValue('john_doe');
    fireEvent.change(input, { target: { value: 'jane_doe' } });

    // Cancel
    fireEvent.click(screen.getByText('Cancel'));

    // Should revert to original value
    expect(screen.getByDisplayValue('john_doe')).toBeInTheDocument();
    expect(mockOnSave).not.toHaveBeenCalled();
  });

  it('renders with number field type', () => {
    render(<EditableValue {...defaultProps} value="42" fieldType="number" />);

    const input = screen.getByDisplayValue('42');
    expect(input).toHaveAttribute('type', 'number');
  });

  it('renders with date field type', () => {
    render(<EditableValue {...defaultProps} value="2024-01-01" fieldType="date" />);

    const input = screen.getByDisplayValue('2024-01-01');
    expect(input).toHaveAttribute('type', 'date');
  });
});
