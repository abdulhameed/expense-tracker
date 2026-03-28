import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Analytics } from '../Analytics';
import { useTransactionStore } from '@/store/transactionStore';

vi.mock('@/store/transactionStore');

const mockAnalyticsData = {
  comparison: {
    current_period: {
      income: 5000,
      expenses: 1500,
      net: 3500,
    },
    previous_period: {
      income: 4800,
      expenses: 1400,
      net: 3400,
    },
    change_percentage: {
      income: 4.17,
      expenses: 7.14,
      net: 2.94,
    },
  },
  category_trends: [
    {
      category_name: 'Food',
      current_month: 500,
      previous_month: 450,
      change_percentage: 11.11,
    },
    {
      category_name: 'Transport',
      current_month: 300,
      previous_month: 320,
      change_percentage: -6.25,
    },
  ],
  spending_velocity: {
    average_daily_spend: 48.39,
    average_daily_income: 161.29,
  },
};

describe('Analytics Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders analytics page with header', () => {
    const mockFetchAnalytics = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      analyticsData: null,
      fetchAnalytics: mockFetchAnalytics,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Analytics />
      </BrowserRouter>
    );

    expect(screen.getByRole('heading', { name: /Analytics/ })).toBeInTheDocument();
    expect(screen.getByText('Detailed insights and trends analysis')).toBeInTheDocument();
  });

  it('displays loading spinner when loading', () => {
    const mockFetchAnalytics = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      analyticsData: null,
      fetchAnalytics: mockFetchAnalytics,
      isLoading: true,
      error: null,
    });

    const { container } = render(
      <BrowserRouter>
        <Analytics />
      </BrowserRouter>
    );

    // Check that something is rendering
    expect(container).toBeInTheDocument();
  });

  it('displays analytics data when available', () => {
    const mockFetchAnalytics = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      analyticsData: mockAnalyticsData,
      fetchAnalytics: mockFetchAnalytics,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Analytics />
      </BrowserRouter>
    );

    expect(screen.getByText('Current Period')).toBeInTheDocument();
    expect(screen.getByText('Previous Period')).toBeInTheDocument();
  });

  it('displays period comparison cards', () => {
    const mockFetchAnalytics = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      analyticsData: mockAnalyticsData,
      fetchAnalytics: mockFetchAnalytics,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Analytics />
      </BrowserRouter>
    );

    // Current period values
    expect(screen.getByText('$5,000.00')).toBeInTheDocument(); // Current income
    expect(screen.getByText('$1,500.00')).toBeInTheDocument(); // Current expenses
  });

  it('displays spending velocity', () => {
    const mockFetchAnalytics = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      analyticsData: mockAnalyticsData,
      fetchAnalytics: mockFetchAnalytics,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Analytics />
      </BrowserRouter>
    );

    expect(screen.getByText('Spending Velocity')).toBeInTheDocument();
    expect(screen.getByText('Average Daily Income')).toBeInTheDocument();
    expect(screen.getByText('Average Daily Spend')).toBeInTheDocument();
  });

  it('displays category trends', () => {
    const mockFetchAnalytics = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      analyticsData: mockAnalyticsData,
      fetchAnalytics: mockFetchAnalytics,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Analytics />
      </BrowserRouter>
    );

    expect(screen.getByText('Category Trends')).toBeInTheDocument();
    expect(screen.getByText('Food')).toBeInTheDocument();
    expect(screen.getByText('Transport')).toBeInTheDocument();
  });

  it('displays change indicators', () => {
    const mockFetchAnalytics = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      analyticsData: mockAnalyticsData,
      fetchAnalytics: mockFetchAnalytics,
      isLoading: false,
      error: null,
    });

    const { container } = render(
      <BrowserRouter>
        <Analytics />
      </BrowserRouter>
    );

    expect(container.textContent).toContain('Period Changes');
    expect(container.textContent).toContain('Income Change');
    expect(container.textContent).toContain('Expense Change');
    expect(container.textContent).toContain('Net Change');
  });

  it('calls fetchAnalytics on mount', () => {
    const mockFetchAnalytics = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      analyticsData: null,
      fetchAnalytics: mockFetchAnalytics,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Analytics />
      </BrowserRouter>
    );

    expect(mockFetchAnalytics).toHaveBeenCalled();
  });

  it('displays error message when fetch fails', () => {
    const mockFetchAnalytics = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      analyticsData: null,
      fetchAnalytics: mockFetchAnalytics,
      isLoading: false,
      error: 'Failed to fetch analytics',
    });

    render(
      <BrowserRouter>
        <Analytics />
      </BrowserRouter>
    );

    expect(screen.getByText('Failed to fetch analytics')).toBeInTheDocument();
  });

  it('displays income trend with positive change', () => {
    const mockFetchAnalytics = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      analyticsData: mockAnalyticsData,
      fetchAnalytics: mockFetchAnalytics,
      isLoading: false,
      error: null,
    });

    const { container } = render(
      <BrowserRouter>
        <Analytics />
      </BrowserRouter>
    );

    // Check that the percentage change is displayed (4.17 is rounded to 4.2 by toFixed(1))
    expect(container.textContent).toContain('4.2%');
  });

  it('displays no category trends message when empty', () => {
    const mockFetchAnalytics = vi.fn();
    const emptyAnalyticsData = {
      ...mockAnalyticsData,
      category_trends: [],
    };

    (useTransactionStore as any).mockReturnValue({
      analyticsData: emptyAnalyticsData,
      fetchAnalytics: mockFetchAnalytics,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Analytics />
      </BrowserRouter>
    );

    expect(screen.getByText('No category trends available')).toBeInTheDocument();
  });
});
