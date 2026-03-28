import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { Dashboard } from '../Dashboard';
import { useAuthStore } from '@/store/authStore';
import { useTransactionStore } from '@/store/transactionStore';

// Mock the stores
vi.mock('@/store/authStore');
vi.mock('@/store/transactionStore');

const mockStats = {
  total_income: 5000,
  total_expenses: 1500,
  net_balance: 3500,
  transactions_count: 10,
};

const mockTransactions = [
  {
    id: 1,
    title: 'Grocery Shopping',
    amount: 150,
    type: 'expense' as const,
    category_id: 1,
    category: { id: 1, name: 'Food', type: 'expense', color: '#ef4444', icon: '🍔' },
    date: '2024-03-20',
    description: 'Weekly groceries',
    payment_method: '',
    reference_number: '',
    is_recurring: false,
    recurring_frequency: '',
    tags: [],
  },
];

describe('Dashboard Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders dashboard page with welcome message', () => {
    const mockGetCurrentUser = vi.fn();
    const mockFetchStats = vi.fn();
    const mockFetchTransactions = vi.fn();

    (useAuthStore as any).mockReturnValue({
      user: { id: 1, first_name: 'John', email: 'john@example.com' },
      getCurrentUser: mockGetCurrentUser,
    });

    (useTransactionStore as any).mockReturnValue({
      stats: mockStats,
      transactions: mockTransactions,
      fetchStats: mockFetchStats,
      fetchTransactions: mockFetchTransactions,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    expect(screen.getByText(/Welcome, John/)).toBeInTheDocument();
    expect(screen.getByText("Here's your financial overview")).toBeInTheDocument();
  });

  it('displays loading spinner when loading', () => {
    const mockGetCurrentUser = vi.fn();
    const mockFetchStats = vi.fn();
    const mockFetchTransactions = vi.fn();

    (useAuthStore as any).mockReturnValue({
      user: null,
      getCurrentUser: mockGetCurrentUser,
    });

    (useTransactionStore as any).mockReturnValue({
      stats: null,
      transactions: [],
      fetchStats: mockFetchStats,
      fetchTransactions: mockFetchTransactions,
      isLoading: true,
      error: null,
    });

    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('displays all stat cards', () => {
    const mockGetCurrentUser = vi.fn();
    const mockFetchStats = vi.fn();
    const mockFetchTransactions = vi.fn();

    (useAuthStore as any).mockReturnValue({
      user: { id: 1, first_name: 'John', email: 'john@example.com' },
      getCurrentUser: mockGetCurrentUser,
    });

    (useTransactionStore as any).mockReturnValue({
      stats: mockStats,
      transactions: mockTransactions,
      fetchStats: mockFetchStats,
      fetchTransactions: mockFetchTransactions,
      isLoading: false,
      error: null,
    });

    const { container } = render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    expect(container.textContent).toContain('Total Income');
    expect(container.textContent).toContain('Total Expenses');
    expect(container.textContent).toContain('Net Balance');
    expect(container.textContent).toContain('$5,000.00');
    expect(container.textContent).toContain('$1,500.00');
    expect(container.textContent).toContain('$3,500.00');
  });

  it('displays correct currency values', () => {
    const mockGetCurrentUser = vi.fn();
    const mockFetchStats = vi.fn();
    const mockFetchTransactions = vi.fn();

    (useAuthStore as any).mockReturnValue({
      user: { id: 1, first_name: 'John', email: 'john@example.com' },
      getCurrentUser: mockGetCurrentUser,
    });

    (useTransactionStore as any).mockReturnValue({
      stats: mockStats,
      transactions: mockTransactions,
      fetchStats: mockFetchStats,
      fetchTransactions: mockFetchTransactions,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    expect(screen.getByText('$5,000.00')).toBeInTheDocument(); // Total Income
    expect(screen.getByText('$1,500.00')).toBeInTheDocument(); // Total Expenses
    expect(screen.getByText('$3,500.00')).toBeInTheDocument(); // Net Balance
  });

  it('displays transaction count', () => {
    const mockGetCurrentUser = vi.fn();
    const mockFetchStats = vi.fn();
    const mockFetchTransactions = vi.fn();

    (useAuthStore as any).mockReturnValue({
      user: { id: 1, first_name: 'John', email: 'john@example.com' },
      getCurrentUser: mockGetCurrentUser,
    });

    (useTransactionStore as any).mockReturnValue({
      stats: mockStats,
      transactions: mockTransactions,
      fetchStats: mockFetchStats,
      fetchTransactions: mockFetchTransactions,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    expect(screen.getByText('10')).toBeInTheDocument(); // transactions_count
  });

  it('displays chart sections', () => {
    const mockGetCurrentUser = vi.fn();
    const mockFetchStats = vi.fn();
    const mockFetchTransactions = vi.fn();

    (useAuthStore as any).mockReturnValue({
      user: { id: 1, first_name: 'John', email: 'john@example.com' },
      getCurrentUser: mockGetCurrentUser,
    });

    (useTransactionStore as any).mockReturnValue({
      stats: mockStats,
      transactions: mockTransactions,
      fetchStats: mockFetchStats,
      fetchTransactions: mockFetchTransactions,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    expect(screen.getByText('Income vs Expenses')).toBeInTheDocument();
    expect(screen.getByText('Spending by Category')).toBeInTheDocument();
  });

  it('displays recent transactions section', () => {
    const mockGetCurrentUser = vi.fn();
    const mockFetchStats = vi.fn();
    const mockFetchTransactions = vi.fn();

    (useAuthStore as any).mockReturnValue({
      user: { id: 1, first_name: 'John', email: 'john@example.com' },
      getCurrentUser: mockGetCurrentUser,
    });

    (useTransactionStore as any).mockReturnValue({
      stats: mockStats,
      transactions: mockTransactions,
      fetchStats: mockFetchStats,
      fetchTransactions: mockFetchTransactions,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    expect(screen.getByText('Recent Transactions')).toBeInTheDocument();
    expect(screen.getByText('Grocery Shopping')).toBeInTheDocument();
  });

  it('displays date range selector buttons', () => {
    const mockGetCurrentUser = vi.fn();
    const mockFetchStats = vi.fn();
    const mockFetchTransactions = vi.fn();

    (useAuthStore as any).mockReturnValue({
      user: { id: 1, first_name: 'John', email: 'john@example.com' },
      getCurrentUser: mockGetCurrentUser,
    });

    (useTransactionStore as any).mockReturnValue({
      stats: mockStats,
      transactions: mockTransactions,
      fetchStats: mockFetchStats,
      fetchTransactions: mockFetchTransactions,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    expect(screen.getByText('7 Days')).toBeInTheDocument();
    expect(screen.getByText('30 Days')).toBeInTheDocument();
    expect(screen.getByText('90 Days')).toBeInTheDocument();
    expect(screen.getByText('All Time')).toBeInTheDocument();
  });

  it('handles date range selection', async () => {
    const mockGetCurrentUser = vi.fn();
    const mockFetchStats = vi.fn();
    const mockFetchTransactions = vi.fn();
    const user = userEvent.setup();

    (useAuthStore as any).mockReturnValue({
      user: { id: 1, first_name: 'John', email: 'john@example.com' },
      getCurrentUser: mockGetCurrentUser,
    });

    (useTransactionStore as any).mockReturnValue({
      stats: mockStats,
      transactions: mockTransactions,
      fetchStats: mockFetchStats,
      fetchTransactions: mockFetchTransactions,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    const sevenDaysButton = screen.getByText('7 Days');
    await user.click(sevenDaysButton);

    expect(mockFetchStats).toHaveBeenCalled();
  });

  it('shows guest when user is not loaded', () => {
    const mockGetCurrentUser = vi.fn();
    const mockFetchStats = vi.fn();
    const mockFetchTransactions = vi.fn();

    (useAuthStore as any).mockReturnValue({
      user: null,
      getCurrentUser: mockGetCurrentUser,
    });

    (useTransactionStore as any).mockReturnValue({
      stats: null,
      transactions: [],
      fetchStats: mockFetchStats,
      fetchTransactions: mockFetchTransactions,
      isLoading: true,
      error: null,
    });

    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    expect(mockGetCurrentUser).toHaveBeenCalled();
  });
});
