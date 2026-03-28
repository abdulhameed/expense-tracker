import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { Budgets } from '../Budgets';
import { useTransactionStore } from '@/store/transactionStore';

// Mock the store
vi.mock('@/store/transactionStore');

const mockCategories = [
  { id: 1, name: 'Food', type: 'expense' as const, color: '#ef4444', icon: '🍔' },
  { id: 2, name: 'Transport', type: 'expense' as const, color: '#f97316', icon: '🚗' },
];

const mockBudgets = [
  {
    id: 1,
    category_id: 1,
    category: mockCategories[0],
    limit_amount: 500,
    period: 'monthly' as const,
    start_date: '2024-03-01',
    alert_threshold: 80,
    is_active: true,
    created_at: '2024-03-01T00:00:00Z',
    updated_at: '2024-03-01T00:00:00Z',
  },
  {
    id: 2,
    category_id: 2,
    category: mockCategories[1],
    limit_amount: 300,
    period: 'monthly' as const,
    start_date: '2024-03-01',
    alert_threshold: 80,
    is_active: true,
    created_at: '2024-03-01T00:00:00Z',
    updated_at: '2024-03-01T00:00:00Z',
  },
];

const mockBudgetProgress = [
  {
    budget_id: 1,
    category_name: 'Food',
    limit_amount: 500,
    spent_amount: 350,
    remaining_amount: 150,
    percentage_used: 70,
    is_exceeded: false,
    alert_triggered: false,
  },
  {
    budget_id: 2,
    category_name: 'Transport',
    limit_amount: 300,
    spent_amount: 280,
    remaining_amount: 20,
    percentage_used: 93.3,
    is_exceeded: false,
    alert_triggered: true,
  },
];

describe('Budgets Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders budgets page with header', () => {
    const mockFetchBudgets = vi.fn();
    const mockFetchBudgetProgress = vi.fn();
    const mockFetchCategories = vi.fn();
    const mockCreateBudget = vi.fn();
    const mockUpdateBudget = vi.fn();
    const mockDeleteBudget = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      budgets: [],
      budgetProgress: [],
      categories: mockCategories,
      fetchBudgets: mockFetchBudgets,
      fetchBudgetProgress: mockFetchBudgetProgress,
      fetchCategories: mockFetchCategories,
      createBudget: mockCreateBudget,
      updateBudget: mockUpdateBudget,
      deleteBudget: mockDeleteBudget,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Budgets />
      </BrowserRouter>
    );

    expect(screen.getByRole('heading', { name: /Budgets/ })).toBeInTheDocument();
    expect(screen.getByText('Set and track spending limits by category')).toBeInTheDocument();
  });

  it('displays budget list when budgets exist', () => {
    const mockFetchBudgets = vi.fn();
    const mockFetchBudgetProgress = vi.fn();
    const mockFetchCategories = vi.fn();
    const mockCreateBudget = vi.fn();
    const mockUpdateBudget = vi.fn();
    const mockDeleteBudget = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      budgets: mockBudgets,
      budgetProgress: mockBudgetProgress,
      categories: mockCategories,
      fetchBudgets: mockFetchBudgets,
      fetchBudgetProgress: mockFetchBudgetProgress,
      fetchCategories: mockFetchCategories,
      createBudget: mockCreateBudget,
      updateBudget: mockUpdateBudget,
      deleteBudget: mockDeleteBudget,
      isLoading: false,
      error: null,
    });

    const { container } = render(
      <BrowserRouter>
        <Budgets />
      </BrowserRouter>
    );

    expect(container.textContent).toContain('Food');
    expect(container.textContent).toContain('Transport');
    expect(container.textContent).toContain('$500.00');
    expect(container.textContent).toContain('$300.00');
  });

  it('shows empty state when no budgets exist', () => {
    const mockFetchBudgets = vi.fn();
    const mockFetchBudgetProgress = vi.fn();
    const mockFetchCategories = vi.fn();
    const mockCreateBudget = vi.fn();
    const mockUpdateBudget = vi.fn();
    const mockDeleteBudget = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      budgets: [],
      budgetProgress: [],
      categories: mockCategories,
      fetchBudgets: mockFetchBudgets,
      fetchBudgetProgress: mockFetchBudgetProgress,
      fetchCategories: mockFetchCategories,
      createBudget: mockCreateBudget,
      updateBudget: mockUpdateBudget,
      deleteBudget: mockDeleteBudget,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Budgets />
      </BrowserRouter>
    );

    expect(screen.getByText('No budgets created yet')).toBeInTheDocument();
  });

  it('displays budget progress overview', () => {
    const mockFetchBudgets = vi.fn();
    const mockFetchBudgetProgress = vi.fn();
    const mockFetchCategories = vi.fn();
    const mockCreateBudget = vi.fn();
    const mockUpdateBudget = vi.fn();
    const mockDeleteBudget = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      budgets: mockBudgets,
      budgetProgress: mockBudgetProgress,
      categories: mockCategories,
      fetchBudgets: mockFetchBudgets,
      fetchBudgetProgress: mockFetchBudgetProgress,
      fetchCategories: mockFetchCategories,
      createBudget: mockCreateBudget,
      updateBudget: mockUpdateBudget,
      deleteBudget: mockDeleteBudget,
      isLoading: false,
      error: null,
    });

    const { container } = render(
      <BrowserRouter>
        <Budgets />
      </BrowserRouter>
    );

    expect(container.textContent).toContain('70%');
    expect(container.textContent).toContain('93.3%');
  });

  it('shows alert trigger for budgets exceeding threshold', () => {
    const mockFetchBudgets = vi.fn();
    const mockFetchBudgetProgress = vi.fn();
    const mockFetchCategories = vi.fn();
    const mockCreateBudget = vi.fn();
    const mockUpdateBudget = vi.fn();
    const mockDeleteBudget = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      budgets: mockBudgets,
      budgetProgress: mockBudgetProgress,
      categories: mockCategories,
      fetchBudgets: mockFetchBudgets,
      fetchBudgetProgress: mockFetchBudgetProgress,
      fetchCategories: mockFetchCategories,
      createBudget: mockCreateBudget,
      updateBudget: mockUpdateBudget,
      deleteBudget: mockDeleteBudget,
      isLoading: false,
      error: null,
    });

    const { container } = render(
      <BrowserRouter>
        <Budgets />
      </BrowserRouter>
    );

    expect(container.textContent).toContain('You\'ve reached 93.3% of your budget for Transport');
  });

  it('opens create budget modal when new budget button clicked', async () => {
    const mockFetchBudgets = vi.fn();
    const mockFetchBudgetProgress = vi.fn();
    const mockFetchCategories = vi.fn();
    const mockCreateBudget = vi.fn();
    const mockUpdateBudget = vi.fn();
    const mockDeleteBudget = vi.fn();
    const user = userEvent.setup();

    (useTransactionStore as any).mockReturnValue({
      budgets: [],
      budgetProgress: [],
      categories: mockCategories,
      fetchBudgets: mockFetchBudgets,
      fetchBudgetProgress: mockFetchBudgetProgress,
      fetchCategories: mockFetchCategories,
      createBudget: mockCreateBudget,
      updateBudget: mockUpdateBudget,
      deleteBudget: mockDeleteBudget,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Budgets />
      </BrowserRouter>
    );

    const createButton = screen.getByText('Create Your First Budget');
    await user.click(createButton);

    await waitFor(() => {
      expect(screen.getByText('Create New Budget')).toBeInTheDocument();
    });
  });

  it('displays loading spinner when loading', () => {
    const mockFetchBudgets = vi.fn();
    const mockFetchBudgetProgress = vi.fn();
    const mockFetchCategories = vi.fn();
    const mockCreateBudget = vi.fn();
    const mockUpdateBudget = vi.fn();
    const mockDeleteBudget = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      budgets: [],
      budgetProgress: [],
      categories: mockCategories,
      fetchBudgets: mockFetchBudgets,
      fetchBudgetProgress: mockFetchBudgetProgress,
      fetchCategories: mockFetchCategories,
      createBudget: mockCreateBudget,
      updateBudget: mockUpdateBudget,
      deleteBudget: mockDeleteBudget,
      isLoading: true,
      error: null,
    });

    render(
      <BrowserRouter>
        <Budgets />
      </BrowserRouter>
    );

    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('displays error alert when error occurs', () => {
    const mockFetchBudgets = vi.fn();
    const mockFetchBudgetProgress = vi.fn();
    const mockFetchCategories = vi.fn();
    const mockCreateBudget = vi.fn();
    const mockUpdateBudget = vi.fn();
    const mockDeleteBudget = vi.fn();
    const errorMessage = 'Failed to load budgets';

    (useTransactionStore as any).mockReturnValue({
      budgets: [],
      budgetProgress: [],
      categories: mockCategories,
      fetchBudgets: mockFetchBudgets,
      fetchBudgetProgress: mockFetchBudgetProgress,
      fetchCategories: mockFetchCategories,
      createBudget: mockCreateBudget,
      updateBudget: mockUpdateBudget,
      deleteBudget: mockDeleteBudget,
      isLoading: false,
      error: errorMessage,
    });

    render(
      <BrowserRouter>
        <Budgets />
      </BrowserRouter>
    );

    expect(screen.getByText(errorMessage)).toBeInTheDocument();
  });

  it('shows progress status colors correctly', () => {
    const mockFetchBudgets = vi.fn();
    const mockFetchBudgetProgress = vi.fn();
    const mockFetchCategories = vi.fn();
    const mockCreateBudget = vi.fn();
    const mockUpdateBudget = vi.fn();
    const mockDeleteBudget = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      budgets: mockBudgets,
      budgetProgress: mockBudgetProgress,
      categories: mockCategories,
      fetchBudgets: mockFetchBudgets,
      fetchBudgetProgress: mockFetchBudgetProgress,
      fetchCategories: mockFetchCategories,
      createBudget: mockCreateBudget,
      updateBudget: mockUpdateBudget,
      deleteBudget: mockDeleteBudget,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Budgets />
      </BrowserRouter>
    );

    // Both budgets should show their spent amounts
    expect(screen.getByText('$350.00')).toBeInTheDocument(); // Food spent
    expect(screen.getByText('$280.00')).toBeInTheDocument(); // Transport spent
  });

  it('displays edit and delete buttons for each budget', () => {
    const mockFetchBudgets = vi.fn();
    const mockFetchBudgetProgress = vi.fn();
    const mockFetchCategories = vi.fn();
    const mockCreateBudget = vi.fn();
    const mockUpdateBudget = vi.fn();
    const mockDeleteBudget = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      budgets: mockBudgets,
      budgetProgress: mockBudgetProgress,
      categories: mockCategories,
      fetchBudgets: mockFetchBudgets,
      fetchBudgetProgress: mockFetchBudgetProgress,
      fetchCategories: mockFetchCategories,
      createBudget: mockCreateBudget,
      updateBudget: mockUpdateBudget,
      deleteBudget: mockDeleteBudget,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Budgets />
      </BrowserRouter>
    );

    const editButtons = screen.getAllByText('Edit');
    const deleteButtons = screen.getAllByText('Delete');

    expect(editButtons.length).toBe(mockBudgets.length);
    expect(deleteButtons.length).toBe(mockBudgets.length);
  });

  it('fetches data on mount', () => {
    const mockFetchBudgets = vi.fn();
    const mockFetchBudgetProgress = vi.fn();
    const mockFetchCategories = vi.fn();
    const mockCreateBudget = vi.fn();
    const mockUpdateBudget = vi.fn();
    const mockDeleteBudget = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      budgets: [],
      budgetProgress: [],
      categories: mockCategories,
      fetchBudgets: mockFetchBudgets,
      fetchBudgetProgress: mockFetchBudgetProgress,
      fetchCategories: mockFetchCategories,
      createBudget: mockCreateBudget,
      updateBudget: mockUpdateBudget,
      deleteBudget: mockDeleteBudget,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Budgets />
      </BrowserRouter>
    );

    expect(mockFetchBudgets).toHaveBeenCalled();
    expect(mockFetchBudgetProgress).toHaveBeenCalled();
    expect(mockFetchCategories).toHaveBeenCalled();
  });
});
