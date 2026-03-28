import { create } from 'zustand';
import { User } from '@/types/api';
import { authService } from '@/services/auth';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (email: string, password: string) => Promise<void>;
  register: (
    email: string,
    first_name: string,
    last_name: string,
    password: string,
    password_confirm: string
  ) => Promise<void>;
  logout: () => Promise<void>;
  getCurrentUser: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  login: async (email: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await authService.login({ email, password });
      set({
        user: response.user,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error) {
      const message =
        error instanceof Error ? error.message : 'Login failed';
      set({
        error: message,
        isLoading: false,
      });
      throw error;
    }
  },

  register: async (
    email: string,
    first_name: string,
    last_name: string,
    password: string,
    password_confirm: string
  ) => {
    set({ isLoading: true, error: null });
    try {
      const response = await authService.register({
        email,
        first_name,
        last_name,
        password,
        password_confirm,
      });
      set({
        user: response.user,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error) {
      const message =
        error instanceof Error ? error.message : 'Registration failed';
      set({
        error: message,
        isLoading: false,
      });
      throw error;
    }
  },

  logout: async () => {
    set({ isLoading: true });
    try {
      await authService.logout();
      set({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      });
    } catch (error) {
      const message =
        error instanceof Error ? error.message : 'Logout failed';
      set({
        error: message,
        isLoading: false,
      });
      throw error;
    }
  },

  getCurrentUser: async () => {
    set({ isLoading: true });
    try {
      const user = await authService.getCurrentUser();
      set({
        user,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error) {
      set({
        isAuthenticated: false,
        isLoading: false,
      });
    }
  },

  clearError: () => {
    set({ error: null });
  },
}));
