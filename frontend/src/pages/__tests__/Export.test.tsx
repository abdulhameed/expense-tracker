import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { Export } from '../Export';
import { useTransactionStore } from '@/store/transactionStore';

// Mock the store
vi.mock('@/store/transactionStore');

const mockExports = [
  {
    file_name: 'transactions_2024.pdf',
    file_url: 'https://example.com/exports/transactions_2024.pdf',
    format: 'pdf',
    created_at: '2024-03-20T10:00:00Z',
  },
  {
    file_name: 'transactions_2024.csv',
    file_url: 'https://example.com/exports/transactions_2024.csv',
    format: 'csv',
    created_at: '2024-03-19T10:00:00Z',
  },
];

describe('Export Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders export page with header', () => {
    const mockFetchExportHistory = vi.fn();
    const mockExportData = vi.fn();
    const mockDeleteExport = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      exports: [],
      fetchExportHistory: mockFetchExportHistory,
      exportData: mockExportData,
      deleteExport: mockDeleteExport,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Export />
      </BrowserRouter>
    );

    expect(screen.getByRole('heading', { name: /Export Data/ })).toBeInTheDocument();
    expect(screen.getByText('Download your financial data in multiple formats')).toBeInTheDocument();
  });

  it('displays export format selection buttons', () => {
    const mockFetchExportHistory = vi.fn();
    const mockExportData = vi.fn();
    const mockDeleteExport = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      exports: [],
      fetchExportHistory: mockFetchExportHistory,
      exportData: mockExportData,
      deleteExport: mockDeleteExport,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Export />
      </BrowserRouter>
    );

    expect(screen.getByText('PDF')).toBeInTheDocument();
    expect(screen.getByText('CSV')).toBeInTheDocument();
    expect(screen.getByText('XLSX')).toBeInTheDocument();
  });

  it('displays export history when exports exist', () => {
    const mockFetchExportHistory = vi.fn();
    const mockExportData = vi.fn();
    const mockDeleteExport = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      exports: mockExports,
      fetchExportHistory: mockFetchExportHistory,
      exportData: mockExportData,
      deleteExport: mockDeleteExport,
      isLoading: false,
      error: null,
    });

    const { container } = render(
      <BrowserRouter>
        <Export />
      </BrowserRouter>
    );

    expect(container.textContent).toContain('transactions_2024.pdf');
    expect(container.textContent).toContain('transactions_2024.csv');
  });

  it('shows empty state when no exports', () => {
    const mockFetchExportHistory = vi.fn();
    const mockExportData = vi.fn();
    const mockDeleteExport = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      exports: [],
      fetchExportHistory: mockFetchExportHistory,
      exportData: mockExportData,
      deleteExport: mockDeleteExport,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Export />
      </BrowserRouter>
    );

    expect(screen.getByText('No exports yet. Create your first export above!')).toBeInTheDocument();
  });

  it('calls exportData when export button is clicked', async () => {
    const mockFetchExportHistory = vi.fn();
    const mockExportData = vi.fn();
    const mockDeleteExport = vi.fn();
    const user = userEvent.setup();

    (useTransactionStore as any).mockReturnValue({
      exports: [],
      fetchExportHistory: mockFetchExportHistory,
      exportData: mockExportData,
      deleteExport: mockDeleteExport,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Export />
      </BrowserRouter>
    );

    const exportButton = screen.getByText('Export Now');
    await user.click(exportButton);

    expect(mockExportData).toHaveBeenCalled();
  });

  it('allows changing export format', async () => {
    const mockFetchExportHistory = vi.fn();
    const mockExportData = vi.fn();
    const mockDeleteExport = vi.fn();
    const user = userEvent.setup();

    (useTransactionStore as any).mockReturnValue({
      exports: [],
      fetchExportHistory: mockFetchExportHistory,
      exportData: mockExportData,
      deleteExport: mockDeleteExport,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Export />
      </BrowserRouter>
    );

    const csvButton = screen.getByText('CSV');
    await user.click(csvButton);

    expect(csvButton.closest('button')).toHaveClass('border-primary-500');
  });

  it('displays error alert when error occurs', () => {
    const mockFetchExportHistory = vi.fn();
    const mockExportData = vi.fn();
    const mockDeleteExport = vi.fn();
    const errorMessage = 'Failed to export data';

    (useTransactionStore as any).mockReturnValue({
      exports: [],
      fetchExportHistory: mockFetchExportHistory,
      exportData: mockExportData,
      deleteExport: mockDeleteExport,
      isLoading: false,
      error: errorMessage,
    });

    render(
      <BrowserRouter>
        <Export />
      </BrowserRouter>
    );

    expect(screen.getByText(errorMessage)).toBeInTheDocument();
  });

  it('fetches export history on mount', () => {
    const mockFetchExportHistory = vi.fn();
    const mockExportData = vi.fn();
    const mockDeleteExport = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      exports: [],
      fetchExportHistory: mockFetchExportHistory,
      exportData: mockExportData,
      deleteExport: mockDeleteExport,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Export />
      </BrowserRouter>
    );

    expect(mockFetchExportHistory).toHaveBeenCalled();
  });

  it('displays download buttons for each export', () => {
    const mockFetchExportHistory = vi.fn();
    const mockExportData = vi.fn();
    const mockDeleteExport = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      exports: mockExports,
      fetchExportHistory: mockFetchExportHistory,
      exportData: mockExportData,
      deleteExport: mockDeleteExport,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Export />
      </BrowserRouter>
    );

    const downloadButtons = screen.getAllByText('Download');
    expect(downloadButtons.length).toBe(mockExports.length);
  });

  it('displays delete buttons for each export', () => {
    const mockFetchExportHistory = vi.fn();
    const mockExportData = vi.fn();
    const mockDeleteExport = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      exports: mockExports,
      fetchExportHistory: mockFetchExportHistory,
      exportData: mockExportData,
      deleteExport: mockDeleteExport,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Export />
      </BrowserRouter>
    );

    const deleteButtons = screen.getAllByText('Delete');
    expect(deleteButtons.length).toBe(mockExports.length);
  });

  it('displays loading spinner while exporting', () => {
    const mockFetchExportHistory = vi.fn();
    const mockExportData = vi.fn();
    const mockDeleteExport = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      exports: [],
      fetchExportHistory: mockFetchExportHistory,
      exportData: mockExportData,
      deleteExport: mockDeleteExport,
      isLoading: true,
      error: null,
    });

    const { container } = render(
      <BrowserRouter>
        <Export />
      </BrowserRouter>
    );

    // The button contains a spinner and the text, look for the text in the button
    expect(container.textContent).toContain('Exporting');
  });
});
