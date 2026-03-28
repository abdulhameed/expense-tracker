import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { Categories } from '../Categories';
import { useTransactionStore } from '@/store/transactionStore';

// Mock the store
vi.mock('@/store/transactionStore');

const mockCategories = [
  {
    id: 1,
    name: 'Food',
    type: 'expense' as const,
    color: '#ef4444',
    icon: '🍔',
    is_default: false,
  },
  {
    id: 2,
    name: 'Salary',
    type: 'income' as const,
    color: '#22c55e',
    icon: '💰',
    is_default: true,
  },
];

describe('Categories Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders categories page with header', () => {
    const mockFetchCategories = vi.fn();
    const mockCreateCategory = vi.fn();
    const mockUpdateCategory = vi.fn();
    const mockDeleteCategory = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      categories: mockCategories,
      fetchCategories: mockFetchCategories,
      createCategory: mockCreateCategory,
      updateCategory: mockUpdateCategory,
      deleteCategory: mockDeleteCategory,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Categories />
      </BrowserRouter>
    );

    expect(screen.getByRole('heading', { name: /Categories/ })).toBeInTheDocument();
    expect(screen.getByText('Manage your income and expense categories')).toBeInTheDocument();
  });

  it('displays category list', () => {
    const mockFetchCategories = vi.fn();
    const mockCreateCategory = vi.fn();
    const mockUpdateCategory = vi.fn();
    const mockDeleteCategory = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      categories: mockCategories,
      fetchCategories: mockFetchCategories,
      createCategory: mockCreateCategory,
      updateCategory: mockUpdateCategory,
      deleteCategory: mockDeleteCategory,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Categories />
      </BrowserRouter>
    );

    expect(screen.getByText('Food')).toBeInTheDocument();
    expect(screen.getByText('Salary')).toBeInTheDocument();
  });

  it('displays loading spinner when loading', () => {
    const mockFetchCategories = vi.fn();
    const mockCreateCategory = vi.fn();
    const mockUpdateCategory = vi.fn();
    const mockDeleteCategory = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      categories: [],
      fetchCategories: mockFetchCategories,
      createCategory: mockCreateCategory,
      updateCategory: mockUpdateCategory,
      deleteCategory: mockDeleteCategory,
      isLoading: true,
      error: null,
    });

    render(
      <BrowserRouter>
        <Categories />
      </BrowserRouter>
    );

    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('displays empty state when no categories', () => {
    const mockFetchCategories = vi.fn();
    const mockCreateCategory = vi.fn();
    const mockUpdateCategory = vi.fn();
    const mockDeleteCategory = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      categories: [],
      fetchCategories: mockFetchCategories,
      createCategory: mockCreateCategory,
      updateCategory: mockUpdateCategory,
      deleteCategory: mockDeleteCategory,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Categories />
      </BrowserRouter>
    );

    expect(screen.getByText('No categories found')).toBeInTheDocument();
  });

  it('filters categories by type', () => {
    const mockFetchCategories = vi.fn();
    const mockCreateCategory = vi.fn();
    const mockUpdateCategory = vi.fn();
    const mockDeleteCategory = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      categories: mockCategories,
      fetchCategories: mockFetchCategories,
      createCategory: mockCreateCategory,
      updateCategory: mockUpdateCategory,
      deleteCategory: mockDeleteCategory,
      isLoading: false,
      error: null,
    });

    const { container } = render(
      <BrowserRouter>
        <Categories />
      </BrowserRouter>
    );

    // Categories should be rendered
    expect(container.textContent).toContain('Food');
    expect(container.textContent).toContain('Salary');

    // Filter UI should exist
    expect(screen.getByLabelText('Filter by Type')).toBeInTheDocument();
  });

  it('displays category icons', () => {
    const mockFetchCategories = vi.fn();
    const mockCreateCategory = vi.fn();
    const mockUpdateCategory = vi.fn();
    const mockDeleteCategory = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      categories: mockCategories,
      fetchCategories: mockFetchCategories,
      createCategory: mockCreateCategory,
      updateCategory: mockUpdateCategory,
      deleteCategory: mockDeleteCategory,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Categories />
      </BrowserRouter>
    );

    expect(screen.getByText('🍔')).toBeInTheDocument();
    expect(screen.getByText('💰')).toBeInTheDocument();
  });

  it('displays category type badge', () => {
    const mockFetchCategories = vi.fn();
    const mockCreateCategory = vi.fn();
    const mockUpdateCategory = vi.fn();
    const mockDeleteCategory = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      categories: mockCategories,
      fetchCategories: mockFetchCategories,
      createCategory: mockCreateCategory,
      updateCategory: mockUpdateCategory,
      deleteCategory: mockDeleteCategory,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Categories />
      </BrowserRouter>
    );

    const expenseBadges = screen.getAllByText('Expense');
    const incomeBadges = screen.getAllByText('Income');

    expect(expenseBadges.length).toBeGreaterThan(0);
    expect(incomeBadges.length).toBeGreaterThan(0);
  });

  it('fetches categories on mount', () => {
    const mockFetchCategories = vi.fn();
    const mockCreateCategory = vi.fn();
    const mockUpdateCategory = vi.fn();
    const mockDeleteCategory = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      categories: [],
      fetchCategories: mockFetchCategories,
      createCategory: mockCreateCategory,
      updateCategory: mockUpdateCategory,
      deleteCategory: mockDeleteCategory,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Categories />
      </BrowserRouter>
    );

    expect(mockFetchCategories).toHaveBeenCalled();
  });

  it('displays Add Category button', () => {
    const mockFetchCategories = vi.fn();
    const mockCreateCategory = vi.fn();
    const mockUpdateCategory = vi.fn();
    const mockDeleteCategory = vi.fn();

    (useTransactionStore as any).mockReturnValue({
      categories: mockCategories,
      fetchCategories: mockFetchCategories,
      createCategory: mockCreateCategory,
      updateCategory: mockUpdateCategory,
      deleteCategory: mockDeleteCategory,
      isLoading: false,
      error: null,
    });

    render(
      <BrowserRouter>
        <Categories />
      </BrowserRouter>
    );

    const buttons = screen.getAllByText(/\+ Add Category/);
    expect(buttons.length).toBeGreaterThan(0);
  });
});
