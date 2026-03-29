import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DocumentPreview } from '../DocumentPreview';
import { Document } from '@/types/api';

describe('DocumentPreview Component', () => {
  const mockOnClose = vi.fn();
  const mockOnDownload = vi.fn();

  const mockImageDocument: Document = {
    id: 1,
    user_id: 1,
    file_name: 'receipt.jpg',
    file_path: '/documents/receipt.jpg',
    file_size: 512000,
    file_type: 'image/jpeg',
    file_extension: 'jpg',
    uploaded_by: 'John Doe',
    description: 'Store receipt',
    tags: ['receipt', '2024'],
    is_public: false,
    created_at: '2024-01-15T10:00:00Z',
    updated_at: '2024-01-15T10:00:00Z',
  };

  const mockPdfDocument: Document = {
    id: 2,
    user_id: 1,
    file_name: 'invoice.pdf',
    file_path: '/documents/invoice.pdf',
    file_size: 1024000,
    file_type: 'application/pdf',
    file_extension: 'pdf',
    uploaded_by: 'John Doe',
    description: 'Monthly invoice',
    tags: ['invoice'],
    is_public: false,
    created_at: '2024-01-15T10:00:00Z',
    updated_at: '2024-01-15T10:00:00Z',
  };

  const mockUnsupportedDocument: Document = {
    id: 3,
    user_id: 1,
    file_name: 'document.docx',
    file_path: '/documents/document.docx',
    file_size: 2048000,
    file_type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    file_extension: 'docx',
    uploaded_by: 'John Doe',
    description: 'Word document',
    tags: [],
    is_public: false,
    created_at: '2024-01-15T10:00:00Z',
    updated_at: '2024-01-15T10:00:00Z',
  };

  beforeEach(() => {
    mockOnClose.mockClear();
    mockOnDownload.mockClear();
  });

  it('does not render when isOpen is false', () => {
    render(
      <DocumentPreview
        isOpen={false}
        onClose={mockOnClose}
        document={mockImageDocument}
      />
    );
    expect(screen.queryByText('Document Preview')).not.toBeInTheDocument();
  });

  it('does not render when document is null', () => {
    render(
      <DocumentPreview
        isOpen={true}
        onClose={mockOnClose}
        document={null}
      />
    );
    expect(screen.queryByText('Document Preview')).not.toBeInTheDocument();
  });

  it('renders document info header', () => {
    render(
      <DocumentPreview
        isOpen={true}
        onClose={mockOnClose}
        document={mockImageDocument}
      />
    );

    expect(screen.getByText('receipt.jpg')).toBeInTheDocument();
    expect(screen.getByText(/Store receipt/)).toBeInTheDocument();
  });

  it('displays image preview for image files', () => {
    const { container } = render(
      <DocumentPreview
        isOpen={true}
        onClose={mockOnClose}
        document={mockImageDocument}
      />
    );

    const img = container.querySelector('img');
    expect(img).toBeInTheDocument();
    expect(img?.src).toContain('/documents/receipt.jpg');
  });

  it('displays PDF message for PDF files', () => {
    render(
      <DocumentPreview
        isOpen={true}
        onClose={mockOnClose}
        document={mockPdfDocument}
      />
    );

    expect(screen.getByText('PDF Preview')).toBeInTheDocument();
    expect(screen.getByText(/Full PDF preview in browser coming soon/)).toBeInTheDocument();
  });

  it('shows preview not available for unsupported file types', () => {
    render(
      <DocumentPreview
        isOpen={true}
        onClose={mockOnClose}
        document={mockUnsupportedDocument}
      />
    );

    expect(
      screen.getByText(/Preview not available for this file type/)
    ).toBeInTheDocument();
  });

  it('displays download button when onDownload is provided', () => {
    render(
      <DocumentPreview
        isOpen={true}
        onClose={mockOnClose}
        document={mockImageDocument}
        onDownload={mockOnDownload}
      />
    );

    expect(screen.getByRole('button', { name: /Download/i })).toBeInTheDocument();
  });

  it('calls onDownload when download button is clicked', async () => {
    const user = userEvent.setup();
    mockOnDownload.mockResolvedValue(undefined);

    render(
      <DocumentPreview
        isOpen={true}
        onClose={mockOnClose}
        document={mockImageDocument}
        onDownload={mockOnDownload}
      />
    );

    const downloadButton = screen.getByRole('button', { name: /Download/i });
    await user.click(downloadButton);

    expect(mockOnDownload).toHaveBeenCalledWith(1);
  });

  it('calls onClose when close button is clicked', async () => {
    const user = userEvent.setup();
    render(
      <DocumentPreview
        isOpen={true}
        onClose={mockOnClose}
        document={mockImageDocument}
      />
    );

    const closeButton = screen.getByRole('button', { name: /Close/i });
    await user.click(closeButton);

    expect(mockOnClose).toHaveBeenCalled();
  });

  it('displays document tags', () => {
    render(
      <DocumentPreview
        isOpen={true}
        onClose={mockOnClose}
        document={mockImageDocument}
      />
    );

    expect(screen.getByText('receipt')).toBeInTheDocument();
    expect(screen.getByText('2024')).toBeInTheDocument();
  });

  it('displays document metadata', () => {
    render(
      <DocumentPreview
        isOpen={true}
        onClose={mockOnClose}
        document={mockImageDocument}
      />
    );

    expect(screen.getByText(/JPG/)).toBeInTheDocument();
    expect(screen.getByText(/MB/)).toBeInTheDocument();
    expect(screen.getByText(/Private/)).toBeInTheDocument();
  });

  it('displays uploader and upload date', () => {
    render(
      <DocumentPreview
        isOpen={true}
        onClose={mockOnClose}
        document={mockImageDocument}
      />
    );

    expect(screen.getByText(/John Doe/)).toBeInTheDocument();
  });

  it('does not display tags section when tags are empty', () => {
    const docNoTags = { ...mockImageDocument, tags: [] };
    render(
      <DocumentPreview
        isOpen={true}
        onClose={mockOnClose}
        document={docNoTags}
      />
    );

    // Should still show the metadata section
    expect(screen.getByText(/JPG/)).toBeInTheDocument();
  });

  it('displays public visibility status', () => {
    const publicDoc = { ...mockImageDocument, is_public: true };
    render(
      <DocumentPreview
        isOpen={true}
        onClose={mockOnClose}
        document={publicDoc}
      />
    );

    expect(screen.getByText(/Public/)).toBeInTheDocument();
  });
});
