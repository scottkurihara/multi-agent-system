/**
 * Tests for DocumentViewer component - Generative UI
 */

import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import DocumentViewer from '../../app/components/DocumentViewer';

describe('DocumentViewer - Generative UI Component', () => {
  const defaultProps = {
    title: 'Project Requirements',
    content: 'This is the main content of the document. It contains important information.',
    metadata: {
      author: 'John Doe',
      created: '2024-01-15',
    },
  };

  it('renders document title', () => {
    render(<DocumentViewer {...defaultProps} />);

    expect(screen.getByText('Project Requirements')).toBeInTheDocument();
  });

  it('displays document content', () => {
    render(<DocumentViewer {...defaultProps} />);

    expect(screen.getByText(/This is the main content/)).toBeInTheDocument();
  });

  it('shows metadata when provided', () => {
    render(<DocumentViewer {...defaultProps} />);

    expect(screen.getByText(/John Doe/)).toBeInTheDocument();
    expect(screen.getByText(/2024-01-15/)).toBeInTheDocument();
  });

  it('renders without metadata', () => {
    const propsWithoutMetadata = {
      title: 'Simple Document',
      content: 'Content only',
    };

    render(<DocumentViewer {...propsWithoutMetadata} />);

    expect(screen.getByText('Simple Document')).toBeInTheDocument();
    expect(screen.getByText('Content only')).toBeInTheDocument();
  });

  it('handles multiline content', () => {
    const multilineProps = {
      ...defaultProps,
      content: 'Line 1\nLine 2\nLine 3',
    };

    render(<DocumentViewer {...multilineProps} />);

    expect(screen.getByText(/Line 1/)).toBeInTheDocument();
  });

  it('renders metadata object with multiple fields', () => {
    const propsWithExtendedMetadata = {
      ...defaultProps,
      metadata: {
        author: 'Jane Smith',
        created: '2024-02-20',
        version: '1.2.3',
        status: 'draft',
      },
    };

    render(<DocumentViewer {...propsWithExtendedMetadata} />);

    expect(screen.getByText(/Jane Smith/)).toBeInTheDocument();
    expect(screen.getByText(/2024-02-20/)).toBeInTheDocument();
    expect(screen.getByText(/1\.2\.3/)).toBeInTheDocument();
    expect(screen.getByText(/draft/)).toBeInTheDocument();
  });
});
