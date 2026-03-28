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
