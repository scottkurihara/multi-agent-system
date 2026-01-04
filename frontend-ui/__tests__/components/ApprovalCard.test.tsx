/**
 * Tests for ApprovalCard component - Generative UI
 */

import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import ApprovalCard from '../../app/components/ApprovalCard';

describe('ApprovalCard - Generative UI Component', () => {
  const mockOnResponse = jest.fn();

  const defaultProps = {
    title: 'Test Approval',
    description: 'Please approve this test action',
    options: ['Approve', 'Edit', 'Reject'],
    onResponse: mockOnResponse,
  };

  beforeEach(() => {
    mockOnResponse.mockClear();
  });

  it('renders approval card with title and description', () => {
    render(<ApprovalCard {...defaultProps} />);

    expect(screen.getByText('Test Approval')).toBeInTheDocument();
    expect(screen.getByText('Please approve this test action')).toBeInTheDocument();
  });

  it('displays all option buttons', () => {
    render(<ApprovalCard {...defaultProps} />);

    expect(screen.getByText('Approve')).toBeInTheDocument();
    expect(screen.getByText('Edit')).toBeInTheDocument();
    expect(screen.getByText('Reject')).toBeInTheDocument();
  });

  it('calls onResponse when an option is clicked', () => {
    render(<ApprovalCard {...defaultProps} />);

    const approveButton = screen.getByText('Approve');
    fireEvent.click(approveButton);

    expect(mockOnResponse).toHaveBeenCalledWith('Approve');
    expect(mockOnResponse).toHaveBeenCalledTimes(1);
  });

  it('displays confirmation message after selection', () => {
    render(<ApprovalCard {...defaultProps} />);

    const editButton = screen.getByText('Edit');
    fireEvent.click(editButton);

    expect(screen.getByText(/You selected: Edit/i)).toBeInTheDocument();
  });

  it('disables buttons after selection', () => {
    render(<ApprovalCard {...defaultProps} />);

    const rejectButton = screen.getByText('Reject');
    fireEvent.click(rejectButton);

    // All buttons should be disabled after selection
    const buttons = screen.getAllByRole('button');
    buttons.forEach((button) => {
      expect(button).toBeDisabled();
    });
  });

  it('handles empty options array gracefully', () => {
    render(<ApprovalCard {...defaultProps} options={[]} />);

    expect(screen.getByText('Test Approval')).toBeInTheDocument();
    // Should not crash, even with empty options
  });
});
