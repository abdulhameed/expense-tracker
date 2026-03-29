import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DocumentList } from '../DocumentList';
import { Document } from '@/types/api';

describe('DocumentList Component', () => {
  const mockOnDownload = vi.fn();
  const mockOnPreview = vi.fn();
  const mockOnDelete = vi.fn();
  const mockOnSearch = vi.fn();
  const mockOnSort = vi.fn();

  const mockDocuments: Document[] = [
    {
      id: 1,
      user_id: 1,
      file_name: 'invoice.pdf',
      file_path: '/documents/invoice.pdf',
      file_size: 1024000,
      file_type: 'application/pdf',
      file_extension: 'pdf',
      uploaded_by: 'John Doe',
      description: 'Monthly invoice',
      tags: ['invoice', '2024'],
      is_public: false,
      created_at: '2024-01-15T10:00:00Z',
      updated_at: '2024-01-15T10:00:00Z',
    },
    {
      id: 2,
      user_id: 1,
      file_name: 'receipt.jpg',
      file_path: '/documents/receipt.jpg',
      file_size: 512000,
      file_type: 'image/jpeg',
      file_extension: 'jpg',
      uploaded_by: 'John Doe',
      description: 'Store receipt',
      tags: ['receipt'],
      is_public: false,
      created_at: '2024-01-14T10:00:00Z',
      updated_at: '2024-01-14T10:00:00Z',
    },
  ];

  beforeEach(() => {
    mockOnDownload.mockClear();
    mockOnPreview.mockClear();
    mockOnDelete.mockClear();
    mockOnSearch.mockClear();
    mockOnSort.mockClear();
  });

  it('renders document list with all documents', () => {
    render(
      <DocumentList
        documents={mockDocuments}
        onDownload={mockOnDownload}
        onPreview={mockOnPreview}
        onDelete={mockOnDelete}
      />
    );

    expect(screen.getByText('invoice.pdf')).toBeInTheDocument();
    expect(screen.getByText('receipt.jpg')).toBeInTheDocument();
  });

  it('shows empty state when no documents', () => {
    render(
      <DocumentList
        documents={[]}
        onDownload={mockOnDownload}
        onPreview={mockOnPreview}
        onDelete={mockOnDelete}
      />
    );

    expect(screen.getByText('No documents found')).toBeInTheDocument();
    expect(screen.getByText('Upload your first document to get started')).toBeInTheDocument();
  });

  it('displays loading spinner when isLoading is true', () => {
    render(
      <DocumentList
        documents={[]}
        isLoading={true}
        onDownload={mockOnDownload}
        onPreview={mockOnPreview}
        onDelete={mockOnDelete}
      />
    );

    // The Spinner component should be rendered
    expect(screen.queryByText('No documents found')).not.toBeInTheDocument();
  });

  it('displays file size formatted correctly', () => {
    render(
      <DocumentList
        documents={mockDocuments}
        onDownload={mockOnDownload}
        onPreview={mockOnPreview}
        onDelete={mockOnDelete}
      />
    );

    // 1024000 bytes = ~1 MB, 512000 bytes = ~0.5 MB
    expect(screen.getByText(/1\.00 MB|0\.98 MB/)).toBeInTheDocument();
  });

  it('displays document tags', () => {
    render(
      <DocumentList
        documents={mockDocuments}
        onDownload={mockOnDownload}
        onPreview={mockOnPreview}
        onDelete={mockOnDelete}
      />
    );

    expect(screen.getByText('invoice')).toBeInTheDocument();
    expect(screen.getByText('2024')).toBeInTheDocument();
    expect(screen.getByText('receipt')).toBeInTheDocument();
  });

  it('calls onSearch when search input changes', async () => {
    const user = userEvent.setup();
    render(
      <DocumentList
        documents={mockDocuments}
        onSearch={mockOnSearch}
        onDownload={mockOnDownload}
        onPreview={mockOnPreview}
        onDelete={mockOnDelete}
      />
    );

    const searchInput = screen.getByPlaceholderText(/Search documents/i);
    await user.type(searchInput, 'invoice');

    expect(mockOnSearch).toHaveBeenCalledWith('invoice');
  });

  it('calls onSort when sort header is clicked', async () => {
    const user = userEvent.setup();
    render(
      <DocumentList
        documents={mockDocuments}
        onSort={mockOnSort}
        onDownload={mockOnDownload}
        onPreview={mockOnPreview}
        onDelete={mockOnDelete}
      />
    );

    const nameButton = screen.getByRole('button', { name: /File Name/i });
    await user.click(nameButton);

    expect(mockOnSort).toHaveBeenCalledWith('name', 'desc');
  });

  it('calls onPreview when preview button is clicked', async () => {
    const user = userEvent.setup();
    render(
      <DocumentList
        documents={mockDocuments}
        onDownload={mockOnDownload}
        onPreview={mockOnPreview}
        onDelete={mockOnDelete}
      />
    );

    const previewButtons = screen.getAllByTitle('Preview');
    await user.click(previewButtons[0]);

    expect(mockOnPreview).toHaveBeenCalledWith(1);
  });

  it('calls onDownload when download button is clicked', async () => {
    const user = userEvent.setup();
    mockOnDownload.mockResolvedValue(undefined);

    render(
      <DocumentList
        documents={mockDocuments}
        onDownload={mockOnDownload}
        onPreview={mockOnPreview}
        onDelete={mockOnDelete}
      />
    );

    const downloadButtons = screen.getAllByTitle('Download');
    await user.click(downloadButtons[0]);

    expect(mockOnDownload).toHaveBeenCalledWith(1);
  });

  it('calls onDelete after confirmation when delete button is clicked', async () => {
    const user = userEvent.setup();
    mockOnDelete.mockResolvedValue(undefined);

    // Mock window.confirm
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true);

    render(
      <DocumentList
        documents={mockDocuments}
        onDownload={mockOnDownload}
        onPreview={mockOnPreview}
        onDelete={mockOnDelete}
      />
    );

    const deleteButtons = screen.getAllByTitle('Delete');
    await user.click(deleteButtons[0]);

    expect(confirmSpy).toHaveBeenCalled();
    expect(mockOnDelete).toHaveBeenCalledWith(1);

    confirmSpy.mockRestore();
  });

  it('does not call onDelete if confirmation is cancelled', async () => {
    const user = userEvent.setup();
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(false);

    render(
      <DocumentList
        documents={mockDocuments}
        onDownload={mockOnDownload}
        onPreview={mockOnPreview}
        onDelete={mockOnDelete}
      />
    );

    const deleteButtons = screen.getAllByTitle('Delete');
    await user.click(deleteButtons[0]);

    expect(mockOnDelete).not.toHaveBeenCalled();

    confirmSpy.mockRestore();
  });

  it('displays document summary', () => {
    render(
      <DocumentList
        documents={mockDocuments}
        onDownload={mockOnDownload}
        onPreview={mockOnPreview}
        onDelete={mockOnDelete}
      />
    );

    expect(screen.getByText(/Showing 2 documents/i)).toBeInTheDocument();
  });

  it('displays description when available', () => {
    render(
      <DocumentList
        documents={mockDocuments}
        onDownload={mockOnDownload}
        onPreview={mockOnPreview}
        onDelete={mockOnDelete}
      />
    );

    expect(screen.getByText('Monthly invoice')).toBeInTheDocument();
    expect(screen.getByText('Store receipt')).toBeInTheDocument();
  });

  it('shows dash for missing description', () => {
    const docWithoutDescription: Document[] = [
      {
        ...mockDocuments[0],
        description: undefined,
      },
    ];

    render(
      <DocumentList
        documents={docWithoutDescription}
        onDownload={mockOnDownload}
        onPreview={mockOnPreview}
        onDelete={mockOnDelete}
      />
    );

    // Check that we have at least one dash in the table
    const cells = screen.getAllByText('-');
    expect(cells.length).toBeGreaterThan(0);
  });
});
