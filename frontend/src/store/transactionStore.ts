import { create } from 'zustand';
import { Transaction, Category, DashboardStats, TransactionFilter, ReportData, AnalyticsData } from '@/types/api';
import { transactionService, categoryService } from '@/services/transaction';

interface TransactionState {
  // State
  transactions: Transaction[];
  categories: Category[];
  stats: DashboardStats | null;
  reportData: ReportData | null;
  analyticsData: AnalyticsData | null;
  isLoading: boolean;
  error: string | null;
  selectedTransaction: Transaction | null;

  // Transaction Actions
  fetchTransactions: (filters?: TransactionFilter) => Promise<void>;
  fetchTransaction: (id: number) => Promise<void>;
  createTransaction: (data: any) => Promise<Transaction>;
  updateTransaction: (id: number, data: any) => Promise<Transaction>;
  deleteTransaction: (id: number) => Promise<void>;
  deleteTransactions: (ids: number[]) => Promise<void>;
  selectTransaction: (transaction: Transaction | null) => void;

  // Category Actions
  fetchCategories: (type?: 'income' | 'expense') => Promise<void>;
  createCategory: (data: any) => Promise<Category>;
  updateCategory: (id: number, data: any) => Promise<Category>;
  deleteCategory: (id: number) => Promise<void>;

  // Stats Actions
  fetchStats: (startDate?: string, endDate?: string) => Promise<void>;

  // Report & Analytics Actions
  fetchReport: (startDate?: string, endDate?: string) => Promise<void>;
  fetchAnalytics: (startDate?: string, endDate?: string) => Promise<void>;

  // Utility
  clearError: () => void;
  reset: () => void;
}

export const useTransactionStore = create<TransactionState>((set, get) => ({
  // Initial State
  transactions: [],
  categories: [],
  stats: null,
  reportData: null,
  analyticsData: null,
  isLoading: false,
  error: null,
  selectedTransaction: null,

  // Transaction Actions
  fetchTransactions: async (filters?: TransactionFilter) => {
    set({ isLoading: true, error: null });
    try {
      const response = await transactionService.getTransactions(filters);
      set({ transactions: response.items, isLoading: false });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch transactions';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  fetchTransaction: async (id: number) => {
    set({ isLoading: true, error: null });
    try {
      const transaction = await transactionService.getTransaction(id);
      set({ selectedTransaction: transaction, isLoading: false });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch transaction';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  createTransaction: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const transaction = await transactionService.createTransaction(data);
      set((state) => ({
        transactions: [transaction, ...state.transactions],
        isLoading: false,
      }));
      await get().fetchStats();
      return transaction;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to create transaction';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  updateTransaction: async (id, data) => {
    set({ isLoading: true, error: null });
    try {
      const updated = await transactionService.updateTransaction(id, data);
      set((state) => ({
        transactions: state.transactions.map((t) => (t.id === id ? updated : t)),
        selectedTransaction:
          state.selectedTransaction?.id === id ? updated : state.selectedTransaction,
        isLoading: false,
      }));
      await get().fetchStats();
      return updated;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to update transaction';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  deleteTransaction: async (id) => {
    set({ isLoading: true, error: null });
    try {
      await transactionService.deleteTransaction(id);
      set((state) => ({
        transactions: state.transactions.filter((t) => t.id !== id),
        selectedTransaction:
          state.selectedTransaction?.id === id ? null : state.selectedTransaction,
        isLoading: false,
      }));
      await get().fetchStats();
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to delete transaction';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  deleteTransactions: async (ids) => {
    set({ isLoading: true, error: null });
    try {
      await transactionService.bulkDeleteTransactions(ids);
      set((state) => ({
        transactions: state.transactions.filter((t) => !ids.includes(t.id)),
        isLoading: false,
      }));
      await get().fetchStats();
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to delete transactions';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  selectTransaction: (transaction) => {
    set({ selectedTransaction: transaction });
  },

  // Category Actions
  fetchCategories: async (type?: 'income' | 'expense') => {
    set({ isLoading: true, error: null });
    try {
      const categories = await categoryService.getCategories(type);
      set({ categories, isLoading: false });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch categories';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  createCategory: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const category = await categoryService.createCategory(data);
      set((state) => ({
        categories: [...state.categories, category],
        isLoading: false,
      }));
      return category;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to create category';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  updateCategory: async (id, data) => {
    set({ isLoading: true, error: null });
    try {
      const updated = await categoryService.updateCategory(id, data);
      set((state) => ({
        categories: state.categories.map((c) => (c.id === id ? updated : c)),
        isLoading: false,
      }));
      return updated;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to update category';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  deleteCategory: async (id) => {
    set({ isLoading: true, error: null });
    try {
      await categoryService.deleteCategory(id);
      set((state) => ({
        categories: state.categories.filter((c) => c.id !== id),
        isLoading: false,
      }));
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to delete category';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  // Stats Actions
  fetchStats: async (startDate?: string, endDate?: string) => {
    set({ isLoading: true, error: null });
    try {
      const stats = await transactionService.getDashboardStats(startDate, endDate);
      set({ stats, isLoading: false });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch stats';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  // Report & Analytics Actions
  fetchReport: async (startDate?: string, endDate?: string) => {
    set({ isLoading: true, error: null });
    try {
      const reportData = await transactionService.getReport(startDate, endDate);
      set({ reportData, isLoading: false });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch report';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  fetchAnalytics: async (startDate?: string, endDate?: string) => {
    set({ isLoading: true, error: null });
    try {
      const analyticsData = await transactionService.getAnalytics(startDate, endDate);
      set({ analyticsData, isLoading: false });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch analytics';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  // Utility
  clearError: () => {
    set({ error: null });
  },

  reset: () => {
    set({
      transactions: [],
      categories: [],
      stats: null,
      reportData: null,
      analyticsData: null,
      isLoading: false,
      error: null,
      selectedTransaction: null,
    });
  },
}));
