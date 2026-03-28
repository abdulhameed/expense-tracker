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
