// API Response types
export interface APIResponse<T> {
  data: T;
  message?: string;
  statusCode: number;
}

// Authentication types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  first_name: string;
  last_name: string;
  password: string;
  password_confirm: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  created_at: string;
  updated_at: string;
}

export interface AuthResponse {
  user: User;
  tokens: AuthTokens;
}

// API Error types
export interface APIError {
  statusCode: number;
  message: string;
  errors?: Record<string, string[]>;
}

// Category types
export interface Category {
  id: number;
  user_id: number;
  name: string;
  type: 'income' | 'expense';
  color?: string;
  icon?: string;
  is_default: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateCategoryRequest {
  name: string;
  type: 'income' | 'expense';
  color?: string;
  icon?: string;
}

// Transaction types
export interface Transaction {
  id: number;
  user_id: number;
  title: string;
  description?: string;
  amount: number;
  type: 'income' | 'expense';
  category_id: number;
  category?: Category;
  date: string;
  payment_method?: string;
  reference_number?: string;
  is_recurring: boolean;
  recurring_frequency?: 'daily' | 'weekly' | 'monthly' | 'yearly';
  attachments?: string[];
  tags?: string[];
  created_at: string;
  updated_at: string;
}

export interface CreateTransactionRequest {
  title: string;
  description?: string;
  amount: number;
  type: 'income' | 'expense';
  category_id: number;
  date: string;
  payment_method?: string;
  reference_number?: string;
  is_recurring?: boolean;
  recurring_frequency?: string;
  tags?: string[];
}

export interface UpdateTransactionRequest extends Partial<CreateTransactionRequest> {}

// Transaction filter/query types
export interface TransactionFilter {
  type?: 'income' | 'expense';
  category_id?: number;
  start_date?: string;
  end_date?: string;
  min_amount?: number;
  max_amount?: number;
  search?: string;
  page?: number;
  limit?: number;
  sort_by?: 'date' | 'amount' | 'title';
  sort_order?: 'asc' | 'desc';
}

export interface TransactionListResponse {
  items: Transaction[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

// Dashboard statistics types
export interface DashboardStats {
  total_income: number;
  total_expenses: number;
  net_balance: number;
  transactions_count: number;
  categories_count: number;
  period: {
    start_date: string;
    end_date: string;
  };
}

export interface TransactionsByCategory {
  [categoryName: string]: number;
}

export interface TransactionsByDate {
  [date: string]: {
    income: number;
    expenses: number;
    net: number;
  };
}

// Reports & Analytics types
export interface CategoryBreakdown {
  category_id: number;
  category_name: string;
  amount: number;
  percentage: number;
  transaction_count: number;
}

export interface MonthlyTrend {
  month: string; // YYYY-MM
  income: number;
  expenses: number;
  net: number;
}

export interface CategoryTrend {
  category_name: string;
  current_month: number;
  previous_month: number;
  change_percentage: number;
}

export interface TopCategory {
  category_id: number;
  category_name: string;
  total_amount: number;
  transaction_count: number;
}

export interface RecurringTransactionSummary {
  transaction_id: number;
  title: string;
  amount: number;
  frequency: string;
  category_name: string;
  next_occurrence?: string;
}

export interface ReportData {
  period: {
    start_date: string;
    end_date: string;
  };
  summary: {
    total_income: number;
    total_expenses: number;
    net_balance: number;
    transaction_count: number;
  };
  by_category: CategoryBreakdown[];
  by_date: TransactionsByDate;
  monthly_trends: MonthlyTrend[];
  top_categories: TopCategory[];
  recurring_summary: RecurringTransactionSummary[];
}

export interface AnalyticsData {
  comparison: {
    current_period: {
      income: number;
      expenses: number;
      net: number;
    };
    previous_period: {
      income: number;
      expenses: number;
      net: number;
    };
    change_percentage: {
      income: number;
      expenses: number;
      net: number;
    };
  };
  category_trends: CategoryTrend[];
  spending_velocity: {
    average_daily_spend: number;
    average_daily_income: number;
  };
}

// Budget types
export interface Budget {
  id: number;
  category_id: number;
  category: Category;
  limit_amount: number;
  period: 'monthly' | 'quarterly' | 'yearly' | 'custom';
  start_date: string;
  end_date?: string;
  alert_threshold: number; // percentage (e.g., 80 for 80%)
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface BudgetProgress {
  budget_id: number;
  category_name: string;
  limit_amount: number;
  spent_amount: number;
  remaining_amount: number;
  percentage_used: number;
  is_exceeded: boolean;
  alert_triggered: boolean;
}

// Export types
export interface ExportRequest {
  format: 'pdf' | 'csv' | 'xlsx';
  data_type: 'transactions' | 'report' | 'analytics';
  start_date?: string;
  end_date?: string;
  filters?: Record<string, any>;
}

export interface ExportResponse {
  file_url: string;
  file_name: string;
  format: string;
  created_at: string;
}

// Search and filter types
export interface FilterPreset {
  id: number;
  name: string;
  filters: FilterCriteria;
  is_default: boolean;
  created_at: string;
}

export interface FilterCriteria {
  dateRange?: {
    start_date: string;
    end_date: string;
  };
  categories?: number[];
  transactionType?: 'income' | 'expense';
  amountRange?: {
    min: number;
    max: number;
  };
  searchQuery?: string;
  tags?: string[];
  paymentMethods?: string[];
}

export interface SearchResult {
  id: number;
  title: string;
  description: string;
  amount: number;
  type: 'income' | 'expense';
  date: string;
  category_name: string;
  relevance_score: number;
}

// Enhanced recurrence types
export type RecurrenceFrequency =
  | 'daily'
  | 'weekly'
  | 'bi_weekly'
  | 'monthly'
  | 'bi_monthly'
  | 'quarterly'
  | 'semi_annual'
  | 'yearly';

export interface RecurrencePattern {
  frequency: RecurrenceFrequency;
  interval: number; // every N periods
  end_date?: string;
  max_occurrences?: number;
  on_day?: number; // for monthly/yearly (1-31)
  on_month?: number; // for yearly (1-12)
}

export interface RecurringTransactionPrediction {
  transaction_id: number;
  next_occurrence_date: string;
  estimated_amount: number;
  frequency: RecurrenceFrequency;
  last_occurrence: string;
}

export interface RecurringTransactionFull extends Transaction {
  recurrence_pattern: RecurrencePattern;
  next_auto_occurrence: string;
  total_occurrences: number;
}

// Project and Team Collaboration types
export type ProjectType = 'personal' | 'business' | 'team';
export type MemberRole = 'owner' | 'admin' | 'member' | 'viewer';
export type InvitationStatus = 'pending' | 'accepted' | 'declined' | 'expired';

export interface Project {
  id: string;
  name: string;
  description: string;
  project_type: ProjectType;
  owner: string;
  currency: string;
  budget?: number;
  start_date?: string;
  end_date?: string;
  is_active: boolean;
  is_archived: boolean;
  member_count: number;
  created_at: string;
  updated_at: string;
}

export interface ProjectMember {
  id: string;
  user: string;
  email: string;
  first_name: string;
  last_name: string;
  role: MemberRole;
  can_create_transactions: boolean;
  can_edit_transactions: boolean;
  can_delete_transactions: boolean;
  can_view_reports: boolean;
  can_invite_members: boolean;
  joined_at: string;
}

export interface CreateProjectMemberRequest {
  email: string;
  role: MemberRole;
}

export interface UpdateProjectMemberRequest {
  role?: MemberRole;
  can_create_transactions?: boolean;
  can_edit_transactions?: boolean;
  can_delete_transactions?: boolean;
  can_view_reports?: boolean;
  can_invite_members?: boolean;
}

export interface Invitation {
  id: string;
  project: string;
  project_name: string;
  email: string;
  role: MemberRole;
  invited_by: string;
  invited_by_email: string;
  status: InvitationStatus;
  created_at: string;
  expires_at: string;
}

export interface ProjectListResponse {
  count: number;
  next?: string;
  previous?: string;
  results: Project[];
}

export interface MemberListResponse {
  items: ProjectMember[];
  total: number;
}

// Document Management types
export interface Document {
  id: number;
  user_id: number;
  transaction_id?: number;
  file_name: string;
  file_path: string;
  file_size: number; // in bytes
  file_type: string; // MIME type
  file_extension: string;
  uploaded_by: string;
  description?: string;
  tags?: string[];
  is_public: boolean;
  created_at: string;
  updated_at: string;
}

export interface UploadDocumentRequest {
  file: File;
  transaction_id?: number;
  description?: string;
  tags?: string[];
  is_public?: boolean;
}

export interface DocumentListResponse {
  items: Document[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface DocumentFilter {
  transaction_id?: number;
  file_type?: string;
  search?: string;
  start_date?: string;
  end_date?: string;
  tags?: string[];
  page?: number;
  limit?: number;
  sort_by?: 'date' | 'name' | 'size';
  sort_order?: 'asc' | 'desc';
}
