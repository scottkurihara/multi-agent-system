/**
 * Tests for OptionsSelector component - Generative UI
 */

import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import OptionsSelector from '../../app/components/OptionsSelector';

describe('OptionsSelector - Generative UI Component', () => {
  const mockOnSelect = jest.fn();

  const defaultProps = {
    question: 'Which option do you prefer?',
    options: ['Option A', 'Option B', 'Option C'],
    onSelect: mockOnSelect,
  };

  beforeEach(() => {
    mockOnSelect.mockClear();
  });

  it('renders question text', () => {
    render(<OptionsSelector {...defaultProps} />);

    expect(screen.getByText('Which option do you prefer?')).toBeInTheDocument();
  });

  it('displays all options with numbers', () => {
    render(<OptionsSelector {...defaultProps} />);

    expect(screen.getByText(/1\./)).toBeInTheDocument();
    expect(screen.getByText('Option A')).toBeInTheDocument();
    expect(screen.getByText(/2\./)).toBeInTheDocument();
    expect(screen.getByText('Option B')).toBeInTheDocument();
    expect(screen.getByText(/3\./)).toBeInTheDocument();
    expect(screen.getByText('Option C')).toBeInTheDocument();
  });

  it('calls onSelect when an option is clicked', () => {
    render(<OptionsSelector {...defaultProps} />);

    const optionB = screen.getByText('Option B');
    fireEvent.click(optionB.closest('button')!);

    expect(mockOnSelect).toHaveBeenCalledWith('Option B');
    expect(mockOnSelect).toHaveBeenCalledTimes(1);
  });

  it('displays selected option', () => {
    render(<OptionsSelector {...defaultProps} />);

    const optionA = screen.getByText('Option A');
    fireEvent.click(optionA.closest('button')!);

    expect(screen.getByText(/You selected: Option A/i)).toBeInTheDocument();
  });

  it('disables all options after selection', () => {
    render(<OptionsSelector {...defaultProps} />);

    const optionC = screen.getByText('Option C');
    fireEvent.click(optionC.closest('button')!);

    const buttons = screen.getAllByRole('button');
    buttons.forEach((button) => {
      expect(button).toBeDisabled();
    });
  });

  it('handles single option', () => {
    render(<OptionsSelector {...defaultProps} options={['Only Option']} />);

    expect(screen.getByText('Only Option')).toBeInTheDocument();
    expect(screen.getByText(/1\./)).toBeInTheDocument();
  });
});
