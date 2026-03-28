import apiClient from './api';
import {
  Transaction,
  CreateTransactionRequest,
  UpdateTransactionRequest,
  TransactionListResponse,
  TransactionFilter,
  Category,
  CreateCategoryRequest,
  DashboardStats,
  ReportData,
  AnalyticsData,
} from '@/types/api';

/**
 * Transaction API Service
 */
export const transactionService = {
  /**
   * Get list of transactions with optional filtering and pagination
   */
  async getTransactions(filters?: TransactionFilter): Promise<TransactionListResponse> {
    const params = new URLSearchParams();

    if (filters) {
      if (filters.type) params.append('type', filters.type);
      if (filters.category_id) params.append('category_id', filters.category_id.toString());
      if (filters.start_date) params.append('start_date', filters.start_date);
      if (filters.end_date) params.append('end_date', filters.end_date);
      if (filters.min_amount) params.append('min_amount', filters.min_amount.toString());
      if (filters.max_amount) params.append('max_amount', filters.max_amount.toString());
      if (filters.search) params.append('search', filters.search);
      if (filters.page) params.append('page', filters.page.toString());
      if (filters.limit) params.append('limit', filters.limit.toString());
      if (filters.sort_by) params.append('sort_by', filters.sort_by);
      if (filters.sort_order) params.append('sort_order', filters.sort_order);
    }

    const response = await apiClient.get<TransactionListResponse>(
      `/transactions/?${params.toString()}`
    );
    return response.data;
  },

  /**
   * Get a single transaction by ID
   */
  async getTransaction(id: number): Promise<Transaction> {
    const response = await apiClient.get<Transaction>(`/transactions/${id}/`);
    return response.data;
  },

  /**
   * Create a new transaction
   */
  async createTransaction(data: CreateTransactionRequest): Promise<Transaction> {
    const response = await apiClient.post<Transaction>('/transactions/', data);
    return response.data;
  },

  /**
   * Update an existing transaction
   */
  async updateTransaction(id: number, data: UpdateTransactionRequest): Promise<Transaction> {
    const response = await apiClient.patch<Transaction>(`/transactions/${id}/`, data);
    return response.data;
  },

  /**
   * Delete a transaction
   */
  async deleteTransaction(id: number): Promise<void> {
    await apiClient.delete(`/transactions/${id}/`);
  },

  /**
   * Bulk delete transactions
   */
  async bulkDeleteTransactions(ids: number[]): Promise<void> {
    await apiClient.post('/transactions/bulk-delete/', { ids });
  },

  /**
   * Get dashboard statistics
   */
  async getDashboardStats(startDate?: string, endDate?: string): Promise<DashboardStats> {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);

    const response = await apiClient.get<DashboardStats>(
      `/dashboard/stats/?${params.toString()}`
    );
    return response.data;
  },

  /**
   * Get transactions by category for analysis
   */
  async getTransactionsByCategory(
    startDate?: string,
    endDate?: string
  ): Promise<Record<string, number>> {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);

    const response = await apiClient.get<Record<string, number>>(
      `/dashboard/by-category/?${params.toString()}`
    );
    return response.data;
  },

  /**
   * Get transactions grouped by date for chart data
   */
  async getTransactionsByDate(
    startDate?: string,
    endDate?: string
  ): Promise<Record<string, { income: number; expenses: number; net: number }>> {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);

    const response = await apiClient.get(
      `/dashboard/by-date/?${params.toString()}`
    );
    return response.data;
  },

  /**
   * Get comprehensive report data
   */
  async getReport(startDate?: string, endDate?: string): Promise<ReportData> {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);

    const response = await apiClient.get<ReportData>(
      `/reports/?${params.toString()}`
    );
    return response.data;
  },

  /**
   * Get analytics data with comparisons and trends
   */
  async getAnalytics(startDate?: string, endDate?: string): Promise<AnalyticsData> {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);

    const response = await apiClient.get<AnalyticsData>(
      `/analytics/?${params.toString()}`
    );
    return response.data;
  },
};

/**
 * Category API Service
 */
export const categoryService = {
  /**
   * Get all categories
   */
  async getCategories(type?: 'income' | 'expense'): Promise<Category[]> {
    const params = new URLSearchParams();
    if (type) params.append('type', type);

    const response = await apiClient.get<Category[]>(
      `/categories/?${params.toString()}`
    );
    return response.data;
  },

  /**
   * Get a single category by ID
   */
  async getCategory(id: number): Promise<Category> {
    const response = await apiClient.get<Category>(`/categories/${id}/`);
    return response.data;
  },

  /**
   * Create a new category
   */
  async createCategory(data: CreateCategoryRequest): Promise<Category> {
    const response = await apiClient.post<Category>('/categories/', data);
    return response.data;
  },

  /**
   * Update an existing category
   */
  async updateCategory(id: number, data: Partial<CreateCategoryRequest>): Promise<Category> {
    const response = await apiClient.patch<Category>(`/categories/${id}/`, data);
    return response.data;
  },

  /**
   * Delete a category
   */
  async deleteCategory(id: number): Promise<void> {
    await apiClient.delete(`/categories/${id}/`);
  },
};
