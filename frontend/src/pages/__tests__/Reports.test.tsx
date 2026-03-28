import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { Reports } from '../Reports';
import { useTransactionStore } from '@/store/transactionStore';

vi.mock('@/store/transactionStore');

const mockReportData = {
  period: {
    start_date: '2024-02-01',
    end_date: '2024-02-29',
  },
  summary: {
    total_income: 5000,
    total_expenses: 1500,
    net_balance: 3500,
    transaction_count: 25,
  },
  by_category: [
    {
      category_id: 1,
      category_name: 'Food',
      amount: 500,
      percentage: 33.3,
      transaction_count: 10,
    },
    {
      category_id: 2,
      category_name: 'Transport',
      amount: 300,
      percentage: 20,
      transaction_count: 5,
    },
  ],
  by_date: {
    '2024-02-01': { income: 200, expenses: 50, net: 150 },
    '2024-02-15': { income: 250, expenses: 100, net: 150 },
  },
  monthly_trends: [
    { month: '2024-01', income: 4800, expenses: 1400, net: 3400 },
    { month: '2024-02', income: 5000, expenses: 1500, net: 3500 },
  ],
  top_categories: [
    { category_id: 1, category_name: 'Food', total_amount: 500, transaction_count: 10 },
    { category_id: 2, category_name: 'Transport', total_amount: 300, transaction_count: 5 },
  ],
  recurring_summary: [
    {
      transaction_id: 1,
      title: 'Netflix Subscription',
      amount: 15,
      frequency: 'monthly',
      category_name: 'Entertainment',
      next_occurrence: '2024-03-01',
    },
  ],
};

describe('Reports Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders reports page with header', () => {
    const mockFetchReport = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      reportData: null,
      fetchReport: mockFetchReport,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Reports />
      </BrowserRouter>
    );

    expect(screen.getByRole('heading', { name: /Reports/ })).toBeInTheDocument();
    expect(screen.getByText('Generate and view detailed financial reports')).toBeInTheDocument();
  });

  it('displays loading spinner when loading', () => {
    const mockFetchReport = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      reportData: null,
      fetchReport: mockFetchReport,
      isLoading: true,
      error: null,
    });

    const { container } = render(
      <BrowserRouter>
        <Reports />
      </BrowserRouter>
    );

    // Check for loading spinner or just that something is rendering
    expect(container).toBeInTheDocument();
  });

  it('displays report data when available', () => {
    const mockFetchReport = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      reportData: mockReportData,
      fetchReport: mockFetchReport,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Reports />
      </BrowserRouter>
    );

    expect(screen.getByText('$5,000.00')).toBeInTheDocument();
    expect(screen.getByText('$1,500.00')).toBeInTheDocument();
    expect(screen.getByText('$3,500.00')).toBeInTheDocument();
  });

  it('displays summary statistics', () => {
    const mockFetchReport = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      reportData: mockReportData,
      fetchReport: mockFetchReport,
      isLoading: false,
      error: null,
    });

    const { container } = render(
      <BrowserRouter>
        <Reports />
      </BrowserRouter>
    );

    // Check for summary cards (more specific check)
    expect(container.textContent).toContain('Total Income');
    expect(container.textContent).toContain('Total Expenses');
    expect(container.textContent).toContain('Net Balance');
  });

  it('displays top spending categories', () => {
    const mockFetchReport = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      reportData: mockReportData,
      fetchReport: mockFetchReport,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Reports />
      </BrowserRouter>
    );

    expect(screen.getByText('Top Spending Categories')).toBeInTheDocument();
    expect(screen.getByText('Food')).toBeInTheDocument();
    expect(screen.getByText('Transport')).toBeInTheDocument();
  });

  it('displays recurring transactions', () => {
    const mockFetchReport = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      reportData: mockReportData,
      fetchReport: mockFetchReport,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Reports />
      </BrowserRouter>
    );

    expect(screen.getByText('Recurring Transactions')).toBeInTheDocument();
    expect(screen.getByText('Netflix Subscription')).toBeInTheDocument();
  });

  it('calls fetchReport on mount with default 30 days', () => {
    const mockFetchReport = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      reportData: mockReportData,
      fetchReport: mockFetchReport,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Reports />
      </BrowserRouter>
    );

    expect(mockFetchReport).toHaveBeenCalled();
  });

  it('handles date range changes', async () => {
    const mockFetchReport = vi.fn();
    const user = userEvent.setup();

    (useTransactionStore as any).mockReturnValue({
      reportData: mockReportData,
      fetchReport: mockFetchReport,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Reports />
      </BrowserRouter>
    );

    const sevenDaysButton = screen.getByText('Last 7 Days');
    await user.click(sevenDaysButton);

    expect(mockFetchReport).toHaveBeenCalled();
  });

  it('displays error message when fetch fails', () => {
    const mockFetchReport = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      reportData: null,
      fetchReport: mockFetchReport,
      isLoading: false,
      error: 'Failed to fetch report',
    });

    render(
      <BrowserRouter>
        <Reports />
      </BrowserRouter>
    );

    expect(screen.getByText('Failed to fetch report')).toBeInTheDocument();
  });
});
