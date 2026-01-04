/**
 * Tests for ResearchSummary component - Generative UI
 */

import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import ResearchSummary from '../../app/components/ResearchSummary';

describe('ResearchSummary - Generative UI Component', () => {
  const defaultProps = {
    title: 'Research Findings',
    findings: ['Finding number one', 'Finding number two', 'Finding number three'],
  };

  it('renders research summary with title', () => {
    render(<ResearchSummary {...defaultProps} />);

    expect(screen.getByText('Research Findings')).toBeInTheDocument();
  });

  it('displays all findings as list items', () => {
    render(<ResearchSummary {...defaultProps} />);

    expect(screen.getByText('Finding number one')).toBeInTheDocument();
    expect(screen.getByText('Finding number two')).toBeInTheDocument();
    expect(screen.getByText('Finding number three')).toBeInTheDocument();
  });

  it('renders findings in correct order', () => {
    render(<ResearchSummary {...defaultProps} />);

    const listItems = screen.getAllByRole('listitem');
    expect(listItems).toHaveLength(3);
    expect(listItems[0]).toHaveTextContent('Finding number one');
    expect(listItems[1]).toHaveTextContent('Finding number two');
    expect(listItems[2]).toHaveTextContent('Finding number three');
  });

  it('handles empty findings array', () => {
    render(<ResearchSummary {...defaultProps} findings={[]} />);

    expect(screen.getByText('Research Findings')).toBeInTheDocument();
    // Should not crash with empty findings
  });

  it('handles single finding', () => {
    render(<ResearchSummary {...defaultProps} findings={['Single finding']} />);

    expect(screen.getByText('Single finding')).toBeInTheDocument();
    const listItems = screen.getAllByRole('listitem');
    expect(listItems).toHaveLength(1);
  });
});
