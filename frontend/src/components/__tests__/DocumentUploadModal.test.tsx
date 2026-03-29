import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DocumentUploadModal } from '../DocumentUploadModal';

describe('DocumentUploadModal Component', () => {
  const mockOnClose = vi.fn();
  const mockOnUpload = vi.fn();

  beforeEach(() => {
    mockOnClose.mockClear();
    mockOnUpload.mockClear();
  });

  it('does not render when isOpen is false', () => {
    render(
      <DocumentUploadModal
        isOpen={false}
        onClose={mockOnClose}
        onUpload={mockOnUpload}
      />
    );
    expect(screen.queryByText('Upload Document')).not.toBeInTheDocument();
  });

  it('renders when isOpen is true', () => {
    render(
      <DocumentUploadModal
        isOpen={true}
        onClose={mockOnClose}
        onUpload={mockOnUpload}
      />
    );
    expect(screen.getByText('Upload Document')).toBeInTheDocument();
  });

  it('renders upload area with instructions', () => {
    render(
      <DocumentUploadModal
        isOpen={true}
        onClose={mockOnClose}
        onUpload={mockOnUpload}
      />
    );
    expect(screen.getByText('Drag and drop your file here')).toBeInTheDocument();
    expect(screen.getByText(/browse files/i)).toBeInTheDocument();
  });

  it('renders description and tags input fields', () => {
    render(
      <DocumentUploadModal
        isOpen={true}
        onClose={mockOnClose}
        onUpload={mockOnUpload}
      />
    );
    expect(screen.getByPlaceholderText(/Invoice for office supplies/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/comma-separated/i)).toBeInTheDocument();
  });

  it('displays transaction ID when provided', () => {
    render(
      <DocumentUploadModal
        isOpen={true}
        onClose={mockOnClose}
        onUpload={mockOnUpload}
        transactionId={123}
      />
    );
    expect(screen.getByText(/transaction ID: 123/i)).toBeInTheDocument();
  });

  it('enables upload button only when a file is selected', async () => {
    const user = userEvent.setup();
    render(
      <DocumentUploadModal
        isOpen={true}
        onClose={mockOnClose}
        onUpload={mockOnUpload}
      />
    );

    const uploadButton = screen.getByRole('button', { name: /Upload Document/i });
    expect(uploadButton).toBeDisabled();
  });

  it('shows error for unsupported file type', async () => {
    const user = userEvent.setup();
    const file = new File(['test'], 'test.txt', { type: 'text/plain' });

    render(
      <DocumentUploadModal
        isOpen={true}
        onClose={mockOnClose}
        onUpload={mockOnUpload}
      />
    );

    const input = screen.getByRole('button', { name: /browse files/i })
      .closest('div')
      ?.querySelector('input[type="file"]') as HTMLInputElement;

    await user.upload(input, file);

    await waitFor(() => {
      expect(screen.getByText(/File type not supported/i)).toBeInTheDocument();
    });
  });

  it('shows error for file exceeding size limit', async () => {
    const user = userEvent.setup();

    // Create a file larger than 10MB (simulated)
    const largeContent = new Array(11 * 1024 * 1024 + 1).join('a');
    const file = new File([largeContent], 'large.pdf', { type: 'application/pdf' });

    render(
      <DocumentUploadModal
        isOpen={true}
        onClose={mockOnClose}
        onUpload={mockOnUpload}
      />
    );

    const input = screen.getByRole('button', { name: /browse files/i })
      .closest('div')
      ?.querySelector('input[type="file"]') as HTMLInputElement;

    await user.upload(input, file);

    await waitFor(() => {
      expect(screen.getByText(/exceeds 10 MB limit/i)).toBeInTheDocument();
    });
  });

  it('calls onClose when cancel button is clicked', async () => {
    const user = userEvent.setup();
    render(
      <DocumentUploadModal
        isOpen={true}
        onClose={mockOnClose}
        onUpload={mockOnUpload}
      />
    );

    const cancelButton = screen.getByRole('button', { name: /Cancel/i });
    await user.click(cancelButton);

    expect(mockOnClose).toHaveBeenCalled();
  });

  it('disables form when isLoading is true', () => {
    render(
      <DocumentUploadModal
        isOpen={true}
        onClose={mockOnClose}
        onUpload={mockOnUpload}
        isLoading={true}
      />
    );

    const cancelButton = screen.getByRole('button', { name: /Cancel/i });
    const uploadButton = screen.getByRole('button', { name: /Uploading/i });

    expect(cancelButton).toBeDisabled();
    expect(uploadButton).toBeDisabled();
  });

  it('renders footer with action buttons', () => {
    render(
      <DocumentUploadModal
        isOpen={true}
        onClose={mockOnClose}
        onUpload={mockOnUpload}
      />
    );

    expect(screen.getByRole('button', { name: /Cancel/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Upload Document/i })).toBeInTheDocument();
  });
});
