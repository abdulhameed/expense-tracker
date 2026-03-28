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
  Budget,
  BudgetProgress,
  ExportRequest,
  ExportResponse,
  FilterPreset,
  FilterCriteria,
  SearchResult,
  RecurringTransactionPrediction,
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

  // ========== Budget Management ==========

  /**
   * Get all budgets for the user
   */
  async getBudgets(): Promise<Budget[]> {
    const response = await apiClient.get<Budget[]>('/budgets/');
    return response.data;
  },

  /**
   * Get budget progress for all active budgets
   */
  async getBudgetProgress(): Promise<BudgetProgress[]> {
    const response = await apiClient.get<BudgetProgress[]>('/budgets/progress/');
    return response.data;
  },

  /**
   * Create a new budget
   */
  async createBudget(data: Omit<Budget, 'id' | 'created_at' | 'updated_at'>): Promise<Budget> {
    const response = await apiClient.post<Budget>('/budgets/', data);
    return response.data;
  },

  /**
   * Update an existing budget
   */
  async updateBudget(id: number, data: Partial<Omit<Budget, 'id' | 'created_at' | 'updated_at'>>): Promise<Budget> {
    const response = await apiClient.patch<Budget>(`/budgets/${id}/`, data);
    return response.data;
  },

  /**
   * Delete a budget
   */
  async deleteBudget(id: number): Promise<void> {
    await apiClient.delete(`/budgets/${id}/`);
  },

  // ========== Data Export ==========

  /**
   * Export data to PDF, CSV, or XLSX format
   */
  async exportData(request: ExportRequest): Promise<ExportResponse> {
    const response = await apiClient.post<ExportResponse>('/export/', request);
    return response.data;
  },

  /**
   * Get list of previously generated exports
   */
  async getExports(): Promise<ExportResponse[]> {
    const response = await apiClient.get<ExportResponse[]>('/export/history/');
    return response.data;
  },

  /**
   * Delete an export file
   */
  async deleteExport(fileUrl: string): Promise<void> {
    await apiClient.delete(`/export/${encodeURIComponent(fileUrl)}/`);
  },

  // ========== Advanced Filtering & Search ==========

  /**
   * Search transactions with full-text search
   */
  async searchTransactions(query: string): Promise<SearchResult[]> {
    const response = await apiClient.get<SearchResult[]>(`/search/transactions/?q=${encodeURIComponent(query)}`);
    return response.data;
  },

  /**
   * Get all saved filter presets
   */
  async getFilterPresets(): Promise<FilterPreset[]> {
    const response = await apiClient.get<FilterPreset[]>('/filters/presets/');
    return response.data;
  },

  /**
   * Save a new filter preset
   */
  async saveFilterPreset(name: string, filters: FilterCriteria): Promise<FilterPreset> {
    const response = await apiClient.post<FilterPreset>('/filters/presets/', {
      name,
      filters,
    });
    return response.data;
  },

  /**
   * Update a filter preset
   */
  async updateFilterPreset(id: number, data: Partial<FilterPreset>): Promise<FilterPreset> {
    const response = await apiClient.patch<FilterPreset>(`/filters/presets/${id}/`, data);
    return response.data;
  },

  /**
   * Delete a filter preset
   */
  async deleteFilterPreset(id: number): Promise<void> {
    await apiClient.delete(`/filters/presets/${id}/`);
  },

  /**
   * Apply advanced filters to transactions
   */
  async applyFilters(filters: FilterCriteria): Promise<TransactionListResponse> {
    const response = await apiClient.post<TransactionListResponse>('/transactions/filter/', filters);
    return response.data;
  },

  // ========== Recurring Transactions Enhancement ==========

  /**
   * Get recurring transaction predictions
   */
  async getRecurringPredictions(): Promise<RecurringTransactionPrediction[]> {
    const response = await apiClient.get<RecurringTransactionPrediction[]>('/transactions/recurring/predictions/');
    return response.data;
  },

  /**
   * Auto-create upcoming recurring transactions
   */
  async autoCreateRecurringTransactions(): Promise<Transaction[]> {
    const response = await apiClient.post<Transaction[]>('/transactions/recurring/auto-create/', {});
    return response.data;
  },

  /**
   * Get recurring transactions with enhanced details
   */
  async getRecurringTransactions(): Promise<Transaction[]> {
    const response = await apiClient.get<Transaction[]>('/transactions/recurring/');
    return response.data;
  },

  /**
   * Update recurrence pattern for a transaction
   */
  async updateRecurrencePattern(
    transactionId: number,
    pattern: any
  ): Promise<Transaction> {
    const response = await apiClient.patch<Transaction>(
      `/transactions/${transactionId}/recurrence/`,
      { recurrence_pattern: pattern }
    );
    return response.data;
  },
};
