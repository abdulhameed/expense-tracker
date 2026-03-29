import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { RecurringTransactions } from '../RecurringTransactions';
import { useTransactionStore } from '@/store/transactionStore';

// Mock the store
vi.mock('@/store/transactionStore');

const mockRecurringTransactions = [
  {
    id: 1,
    title: 'Monthly Rent',
    description: 'Apartment rent',
    amount: 1200,
    type: 'expense' as const,
    category_id: 1,
    category: { id: 1, name: 'Housing', type: 'expense', color: '#ef4444', icon: '🏠' },
    date: '2024-03-01',
    payment_method: 'bank_transfer',
    reference_number: '',
    is_recurring: true,
    recurring_frequency: 'monthly',
    tags: [],
  },
  {
    id: 2,
    title: 'Bi-weekly Salary',
    description: 'Work salary',
    amount: 2000,
    type: 'income' as const,
    category_id: 2,
    category: { id: 2, name: 'Salary', type: 'income', color: '#22c55e', icon: '💰' },
    date: '2024-03-01',
    payment_method: 'bank_transfer',
    reference_number: '',
    is_recurring: true,
    recurring_frequency: 'bi_weekly',
    tags: [],
  },
];

const mockPredictions = [
  {
    transaction_id: 1,
    next_occurrence_date: '2024-04-01',
    estimated_amount: 1200,
    frequency: 'monthly' as const,
    last_occurrence: '2024-03-01',
  },
  {
    transaction_id: 2,
    next_occurrence_date: '2024-03-29',
    estimated_amount: 2000,
    frequency: 'bi_weekly' as const,
    last_occurrence: '2024-03-15',
  },
];

describe('Recurring Transactions Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders recurring transactions page with header', () => {
    const mockGetRecurringPredictions = vi.fn();
    const mockGetRecurringTransactions = vi.fn();
    const mockAutoCreateRecurringTransactions = vi.fn();
    const mockUpdateRecurrencePattern = vi.fn();
    const mockDeleteTransaction = vi.fn();
    const mockFetchTransactions = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      transactions: mockRecurringTransactions,
      recurringPredictions: mockPredictions,
      fetchTransactions: mockFetchTransactions,
      getRecurringPredictions: mockGetRecurringPredictions,
      getRecurringTransactions: mockGetRecurringTransactions,
      autoCreateRecurringTransactions: mockAutoCreateRecurringTransactions,
      updateRecurrencePattern: mockUpdateRecurrencePattern,
      deleteTransaction: mockDeleteTransaction,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <RecurringTransactions />
      </BrowserRouter>
    );

    expect(screen.getByRole('heading', { level: 1, name: /Recurring Transactions/ })).toBeInTheDocument();
    expect(
      screen.getByText('Manage automatic recurring payments and income')
    ).toBeInTheDocument();
  });

  it('displays recurring transactions table', () => {
    const mockGetRecurringPredictions = vi.fn();
    const mockGetRecurringTransactions = vi.fn();
    const mockAutoCreateRecurringTransactions = vi.fn();
    const mockUpdateRecurrencePattern = vi.fn();
    const mockDeleteTransaction = vi.fn();
    const mockFetchTransactions = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      transactions: mockRecurringTransactions,
      recurringPredictions: mockPredictions,
      fetchTransactions: mockFetchTransactions,
      getRecurringPredictions: mockGetRecurringPredictions,
      getRecurringTransactions: mockGetRecurringTransactions,
      autoCreateRecurringTransactions: mockAutoCreateRecurringTransactions,
      updateRecurrencePattern: mockUpdateRecurrencePattern,
      deleteTransaction: mockDeleteTransaction,
      isLoading: false,
      error: null,
    });

    const { container } = render(
      <BrowserRouter>
        <RecurringTransactions />
      </BrowserRouter>
    );

    expect(container.textContent).toContain('Monthly Rent');
    expect(container.textContent).toContain('Bi-weekly Salary');
    expect(container.textContent).toContain('monthly');
    expect(container.textContent).toContain('bi_weekly');
  });

  it('displays upcoming predictions', () => {
    const mockGetRecurringPredictions = vi.fn();
    const mockGetRecurringTransactions = vi.fn();
    const mockAutoCreateRecurringTransactions = vi.fn();
    const mockUpdateRecurrencePattern = vi.fn();
    const mockDeleteTransaction = vi.fn();
    const mockFetchTransactions = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      transactions: mockRecurringTransactions,
      recurringPredictions: mockPredictions,
      fetchTransactions: mockFetchTransactions,
      getRecurringPredictions: mockGetRecurringPredictions,
      getRecurringTransactions: mockGetRecurringTransactions,
      autoCreateRecurringTransactions: mockAutoCreateRecurringTransactions,
      updateRecurrencePattern: mockUpdateRecurrencePattern,
      deleteTransaction: mockDeleteTransaction,
      isLoading: false,
      error: null,
    });

    const { container } = render(
      <BrowserRouter>
        <RecurringTransactions />
      </BrowserRouter>
    );

    expect(container.textContent).toContain('Upcoming Auto-Generated Transactions');
  });

  it('shows empty state when no recurring transactions', () => {
    const mockGetRecurringPredictions = vi.fn();
    const mockGetRecurringTransactions = vi.fn();
    const mockAutoCreateRecurringTransactions = vi.fn();
    const mockUpdateRecurrencePattern = vi.fn();
    const mockDeleteTransaction = vi.fn();
    const mockFetchTransactions = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      transactions: [],
      recurringPredictions: [],
      fetchTransactions: mockFetchTransactions,
      getRecurringPredictions: mockGetRecurringPredictions,
      getRecurringTransactions: mockGetRecurringTransactions,
      autoCreateRecurringTransactions: mockAutoCreateRecurringTransactions,
      updateRecurrencePattern: mockUpdateRecurrencePattern,
      deleteTransaction: mockDeleteTransaction,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <RecurringTransactions />
      </BrowserRouter>
    );

    expect(screen.getByText('No recurring transactions set up yet')).toBeInTheDocument();
  });

  it('displays loading spinner when loading', () => {
    const mockGetRecurringPredictions = vi.fn();
    const mockGetRecurringTransactions = vi.fn();
    const mockAutoCreateRecurringTransactions = vi.fn();
    const mockUpdateRecurrencePattern = vi.fn();
    const mockDeleteTransaction = vi.fn();
    const mockFetchTransactions = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      transactions: [],
      recurringPredictions: [],
      fetchTransactions: mockFetchTransactions,
      getRecurringPredictions: mockGetRecurringPredictions,
      getRecurringTransactions: mockGetRecurringTransactions,
      autoCreateRecurringTransactions: mockAutoCreateRecurringTransactions,
      updateRecurrencePattern: mockUpdateRecurrencePattern,
      deleteTransaction: mockDeleteTransaction,
      isLoading: true,
      error: null,
    });

    render(
      <BrowserRouter>
        <RecurringTransactions />
      </BrowserRouter>
    );

    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('displays error alert when error occurs', () => {
    const mockGetRecurringPredictions = vi.fn();
    const mockGetRecurringTransactions = vi.fn();
    const mockAutoCreateRecurringTransactions = vi.fn();
    const mockUpdateRecurrencePattern = vi.fn();
    const mockDeleteTransaction = vi.fn();
    const mockFetchTransactions = vi.fn();
    const errorMessage = 'Failed to load recurring transactions';

    (useTransactionStore as any).mockReturnValue({
      transactions: [],
      recurringPredictions: [],
      fetchTransactions: mockFetchTransactions,
      getRecurringPredictions: mockGetRecurringPredictions,
      getRecurringTransactions: mockGetRecurringTransactions,
      autoCreateRecurringTransactions: mockAutoCreateRecurringTransactions,
      updateRecurrencePattern: mockUpdateRecurrencePattern,
      deleteTransaction: mockDeleteTransaction,
      isLoading: false,
      error: errorMessage,
    });

    render(
      <BrowserRouter>
        <RecurringTransactions />
      </BrowserRouter>
    );

    expect(screen.getByText(errorMessage)).toBeInTheDocument();
  });

  it('fetches recurring data on mount', () => {
    const mockGetRecurringPredictions = vi.fn();
    const mockGetRecurringTransactions = vi.fn();
    const mockAutoCreateRecurringTransactions = vi.fn();
    const mockUpdateRecurrencePattern = vi.fn();
    const mockDeleteTransaction = vi.fn();
    const mockFetchTransactions = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      transactions: mockRecurringTransactions,
      recurringPredictions: mockPredictions,
      fetchTransactions: mockFetchTransactions,
      getRecurringPredictions: mockGetRecurringPredictions,
      getRecurringTransactions: mockGetRecurringTransactions,
      autoCreateRecurringTransactions: mockAutoCreateRecurringTransactions,
      updateRecurrencePattern: mockUpdateRecurrencePattern,
      deleteTransaction: mockDeleteTransaction,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <RecurringTransactions />
      </BrowserRouter>
    );

    expect(mockGetRecurringPredictions).toHaveBeenCalled();
    expect(mockGetRecurringTransactions).toHaveBeenCalled();
  });

  it('displays income and expense amounts with correct colors', () => {
    const mockGetRecurringPredictions = vi.fn();
    const mockGetRecurringTransactions = vi.fn();
    const mockAutoCreateRecurringTransactions = vi.fn();
    const mockUpdateRecurrencePattern = vi.fn();
    const mockDeleteTransaction = vi.fn();
    const mockFetchTransactions = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      transactions: mockRecurringTransactions,
      recurringPredictions: mockPredictions,
      fetchTransactions: mockFetchTransactions,
      getRecurringPredictions: mockGetRecurringPredictions,
      getRecurringTransactions: mockGetRecurringTransactions,
      autoCreateRecurringTransactions: mockAutoCreateRecurringTransactions,
      updateRecurrencePattern: mockUpdateRecurrencePattern,
      deleteTransaction: mockDeleteTransaction,
      isLoading: false,
      error: null,
    });

    const { container } = render(
      <BrowserRouter>
        <RecurringTransactions />
      </BrowserRouter>
    );

    expect(container.textContent).toContain('+$2,000.00');
    expect(container.textContent).toContain('-$1,200.00');
  });

  it('displays auto-create button', () => {
    const mockGetRecurringPredictions = vi.fn();
    const mockGetRecurringTransactions = vi.fn();
    const mockAutoCreateRecurringTransactions = vi.fn();
    const mockUpdateRecurrencePattern = vi.fn();
    const mockDeleteTransaction = vi.fn();
    const mockFetchTransactions = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      transactions: mockRecurringTransactions,
      recurringPredictions: mockPredictions,
      fetchTransactions: mockFetchTransactions,
      getRecurringPredictions: mockGetRecurringPredictions,
      getRecurringTransactions: mockGetRecurringTransactions,
      autoCreateRecurringTransactions: mockAutoCreateRecurringTransactions,
      updateRecurrencePattern: mockUpdateRecurrencePattern,
      deleteTransaction: mockDeleteTransaction,
      isLoading: false,
      error: null,
    });

    const { container } = render(
      <BrowserRouter>
        <RecurringTransactions />
      </BrowserRouter>
    );

    expect(container.textContent).toContain('Auto-Create Now');
  });
});
