import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { Transactions } from '../Transactions';
import { useTransactionStore } from '@/store/transactionStore';

// Mock the store
vi.mock('@/store/transactionStore');

const mockTransactions = [
  {
    id: 1,
    title: 'Grocery Shopping',
    description: 'Weekly groceries',
    amount: 150,
    type: 'expense' as const,
    category_id: 1,
    category: { id: 1, name: 'Food', type: 'expense', color: '#ef4444', icon: '🍔' },
    date: '2024-03-20',
    payment_method: 'credit_card',
    reference_number: '',
    is_recurring: false,
    recurring_frequency: '',
    tags: ['groceries'],
  },
  {
    id: 2,
    title: 'Salary',
    description: 'Monthly salary',
    amount: 5000,
    type: 'income' as const,
    category_id: 2,
    category: { id: 2, name: 'Salary', type: 'income', color: '#22c55e', icon: '💰' },
    date: '2024-03-15',
    payment_method: 'bank_transfer',
    reference_number: '',
    is_recurring: true,
    recurring_frequency: 'monthly',
    tags: [],
  },
];

const mockCategories = [
  { id: 1, name: 'Food', type: 'expense' as const, color: '#ef4444', icon: '🍔' },
  { id: 2, name: 'Salary', type: 'income' as const, color: '#22c55e', icon: '💰' },
];

describe('Transactions Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders transactions page with header', () => {
    const mockFetchTransactions = vi.fn();
    const mockFetchCategories = vi.fn();
    const mockDeleteTransaction = vi.fn();
    const mockApplyFilters = vi.fn();
    const mockSaveFilterPreset = vi.fn();
    const mockDeleteFilterPreset = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      transactions: mockTransactions,
      categories: mockCategories,
      filterPresets: [],
      fetchTransactions: mockFetchTransactions,
      fetchCategories: mockFetchCategories,
      deleteTransaction: mockDeleteTransaction,
      applyFilters: mockApplyFilters,
      saveFilterPreset: mockSaveFilterPreset,
      deleteFilterPreset: mockDeleteFilterPreset,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Transactions />
      </BrowserRouter>
    );

    expect(screen.getByRole('heading', { name: /Transactions/ })).toBeInTheDocument();
    expect(screen.getByText('Manage your income and expenses')).toBeInTheDocument();
  });

  it('displays transaction list', () => {
    const mockFetchTransactions = vi.fn();
    const mockFetchCategories = vi.fn();
    const mockDeleteTransaction = vi.fn();
    const mockApplyFilters = vi.fn();
    const mockSaveFilterPreset = vi.fn();
    const mockDeleteFilterPreset = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      transactions: mockTransactions,
      categories: mockCategories,
      filterPresets: [],
      fetchTransactions: mockFetchTransactions,
      fetchCategories: mockFetchCategories,
      deleteTransaction: mockDeleteTransaction,
      applyFilters: mockApplyFilters,
      saveFilterPreset: mockSaveFilterPreset,
      deleteFilterPreset: mockDeleteFilterPreset,
      isLoading: false,
      error: null,
    });

    const { container } = render(
      <BrowserRouter>
        <Transactions />
      </BrowserRouter>
    );

    // Check for transaction titles and amounts displayed in the table
    expect(container.textContent).toContain('Grocery Shopping');
    expect(container.textContent).toContain('$5,000.00');
    expect(container.textContent).toContain('$150.00');
  });

  it('displays loading spinner when loading', () => {
    const mockFetchTransactions = vi.fn();
    const mockFetchCategories = vi.fn();
    const mockDeleteTransaction = vi.fn();
    const mockApplyFilters = vi.fn();
    const mockSaveFilterPreset = vi.fn();
    const mockDeleteFilterPreset = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      transactions: [],
      categories: mockCategories,
      filterPresets: [],
      fetchTransactions: mockFetchTransactions,
      fetchCategories: mockFetchCategories,
      deleteTransaction: mockDeleteTransaction,
      applyFilters: mockApplyFilters,
      saveFilterPreset: mockSaveFilterPreset,
      deleteFilterPreset: mockDeleteFilterPreset,
      isLoading: true,
      error: null,
    });

    render(
      <BrowserRouter>
        <Transactions />
      </BrowserRouter>
    );

    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('displays empty state when no transactions', () => {
    const mockFetchTransactions = vi.fn();
    const mockFetchCategories = vi.fn();
    const mockDeleteTransaction = vi.fn();
    const mockApplyFilters = vi.fn();
    const mockSaveFilterPreset = vi.fn();
    const mockDeleteFilterPreset = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      transactions: [],
      categories: mockCategories,
      filterPresets: [],
      fetchTransactions: mockFetchTransactions,
      fetchCategories: mockFetchCategories,
      deleteTransaction: mockDeleteTransaction,
      applyFilters: mockApplyFilters,
      saveFilterPreset: mockSaveFilterPreset,
      deleteFilterPreset: mockDeleteFilterPreset,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Transactions />
      </BrowserRouter>
    );

    expect(screen.getByText('No transactions found')).toBeInTheDocument();
  });

  it('handles transaction selection', async () => {
    const mockFetchTransactions = vi.fn();
    const mockFetchCategories = vi.fn();
    const mockDeleteTransaction = vi.fn();
    const mockApplyFilters = vi.fn();
    const mockSaveFilterPreset = vi.fn();
    const mockDeleteFilterPreset = vi.fn();
    const user = userEvent.setup();

    (useTransactionStore as any).mockReturnValue({
      transactions: mockTransactions,
      categories: mockCategories,
      filterPresets: [],
      fetchTransactions: mockFetchTransactions,
      fetchCategories: mockFetchCategories,
      deleteTransaction: mockDeleteTransaction,
      applyFilters: mockApplyFilters,
      saveFilterPreset: mockSaveFilterPreset,
      deleteFilterPreset: mockDeleteFilterPreset,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Transactions />
      </BrowserRouter>
    );

    const checkboxes = screen.getAllByRole('checkbox');
    const firstTransactionCheckbox = checkboxes[1]; // Skip the select-all checkbox

    await user.click(firstTransactionCheckbox);

    expect(firstTransactionCheckbox).toBeChecked();
  });

  it('shows currency correctly for income and expense', () => {
    const mockFetchTransactions = vi.fn();
    const mockFetchCategories = vi.fn();
    const mockDeleteTransaction = vi.fn();
    const mockApplyFilters = vi.fn();
    const mockSaveFilterPreset = vi.fn();
    const mockDeleteFilterPreset = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      transactions: mockTransactions,
      categories: mockCategories,
      filterPresets: [],
      fetchTransactions: mockFetchTransactions,
      fetchCategories: mockFetchCategories,
      deleteTransaction: mockDeleteTransaction,
      applyFilters: mockApplyFilters,
      saveFilterPreset: mockSaveFilterPreset,
      deleteFilterPreset: mockDeleteFilterPreset,
      isLoading: false,
      error: null,
    });

    const { container } = render(
      <BrowserRouter>
        <Transactions />
      </BrowserRouter>
    );

    // Check that income and expense amounts are displayed with currency formatting
    expect(container.textContent).toContain('+$5,000.00');
    expect(container.textContent).toContain('-$150.00');
  });

  it('displays categories correctly in table', () => {
    const mockFetchTransactions = vi.fn();
    const mockFetchCategories = vi.fn();
    const mockDeleteTransaction = vi.fn();
    const mockApplyFilters = vi.fn();
    const mockSaveFilterPreset = vi.fn();
    const mockDeleteFilterPreset = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      transactions: mockTransactions,
      categories: mockCategories,
      filterPresets: [],
      fetchTransactions: mockFetchTransactions,
      fetchCategories: mockFetchCategories,
      deleteTransaction: mockDeleteTransaction,
      applyFilters: mockApplyFilters,
      saveFilterPreset: mockSaveFilterPreset,
      deleteFilterPreset: mockDeleteFilterPreset,
      isLoading: false,
      error: null,
    });

    const { container } = render(
      <BrowserRouter>
        <Transactions />
      </BrowserRouter>
    );

    // Check that categories are displayed in the table
    expect(container.textContent).toContain('Food');
    expect(container.textContent).toContain('Grocery Shopping');
  });

  it('fetches categories on mount if empty', () => {
    const mockFetchTransactions = vi.fn();
    const mockFetchCategories = vi.fn();
    const mockDeleteTransaction = vi.fn();
    const mockApplyFilters = vi.fn();
    const mockSaveFilterPreset = vi.fn();
    const mockDeleteFilterPreset = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      transactions: [],
      categories: [],
      filterPresets: [],
      fetchTransactions: mockFetchTransactions,
      fetchCategories: mockFetchCategories,
      deleteTransaction: mockDeleteTransaction,
      applyFilters: mockApplyFilters,
      saveFilterPreset: mockSaveFilterPreset,
      deleteFilterPreset: mockDeleteFilterPreset,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Transactions />
      </BrowserRouter>
    );

    expect(mockFetchCategories).toHaveBeenCalled();
  });

  it('does not fetch categories if already loaded', () => {
    const mockFetchTransactions = vi.fn();
    const mockFetchCategories = vi.fn();
    const mockDeleteTransaction = vi.fn();
    const mockApplyFilters = vi.fn();
    const mockSaveFilterPreset = vi.fn();
    const mockDeleteFilterPreset = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      transactions: mockTransactions,
      categories: mockCategories,
      filterPresets: [],
      fetchTransactions: mockFetchTransactions,
      fetchCategories: mockFetchCategories,
      deleteTransaction: mockDeleteTransaction,
      applyFilters: mockApplyFilters,
      saveFilterPreset: mockSaveFilterPreset,
      deleteFilterPreset: mockDeleteFilterPreset,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Transactions />
      </BrowserRouter>
    );

    expect(mockFetchCategories).not.toHaveBeenCalled();
  });
});
