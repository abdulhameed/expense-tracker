import apiClient, { setTokens, clearTokens } from './api';
import {
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  User,
} from '@/types/api';

export const authService = {
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/login/', credentials);
    setTokens(response.data.tokens);
    return response.data;
  },

  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/register/', data);
    setTokens(response.data.tokens);
    return response.data;
  },

  async logout(): Promise<void> {
    try {
      await apiClient.post('/auth/logout/');
    } finally {
      clearTokens();
    }
  },

  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/auth/me/');
    return response.data;
  },

  async refreshToken(): Promise<string> {
    const response = await apiClient.post<{ access: string }>(
      '/auth/refresh/',
      {}
    );
    return response.data.access;
  },
};
