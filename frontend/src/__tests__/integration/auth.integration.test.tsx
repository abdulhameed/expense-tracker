import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useAuthStore } from '@/store/authStore';
import { Login } from '@/pages/Login';
import { Register } from '@/pages/Register';
import * as api from '@/services/api';

// Mock the API
vi.mock('@/services/api', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
  },
  setTokens: vi.fn(),
  clearTokens: vi.fn(),
  getTokens: vi.fn(() => null),
}));

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => vi.fn(),
  };
});

describe('Authentication Integration Tests', () => {
  beforeEach(() => {
    // Reset auth store and mocks before each test
    useAuthStore.setState({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
    });
    vi.clearAllMocks();
  });

  describe('Login Flow', () => {
    it('validates email format on login', async () => {
      const user = userEvent.setup();
      render(<Login />);

      const submitButton = screen.getByRole('button', { name: /sign in/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Email is required')).toBeInTheDocument();
      });
    });

    it('validates password length on login', async () => {
      const user = userEvent.setup();
      render(<Login />);

      const emailInput = screen.getByPlaceholderText('you@example.com');
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      await user.type(emailInput, 'user@example.com');
      await user.click(submitButton);

      await waitFor(() => {
        expect(
          screen.getByText('Password must be at least 6 characters')
        ).toBeInTheDocument();
      });
    });

    it('submits login form with valid credentials', async () => {
      const user = userEvent.setup();
      const mockApiPost = vi.fn().mockResolvedValue({
        data: {
          tokens: { access: 'test-token', refresh: 'refresh-token' },
          user: { id: 1, email: 'test@example.com', first_name: 'Test' },
        },
      });
      (api.default.post as any) = mockApiPost;

      render(<Login />);

      const emailInput = screen.getByPlaceholderText('you@example.com');
      const passwordInput = screen.getByPlaceholderText('Enter your password');
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      await user.type(emailInput, 'test@example.com');
      await user.type(passwordInput, 'password123');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockApiPost).toHaveBeenCalledWith('/auth/login/', {
          email: 'test@example.com',
          password: 'password123',
        });
      });
    });

    it('displays error on failed login', async () => {
      const user = userEvent.setup();
      const mockApiPost = vi.fn().mockRejectedValue({
        response: {
          data: { detail: 'Invalid credentials' },
        },
      });
      (api.default.post as any) = mockApiPost;

      render(<Login />);

      const emailInput = screen.getByPlaceholderText('you@example.com');
      const passwordInput = screen.getByPlaceholderText('Enter your password');
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      await user.type(emailInput, 'test@example.com');
      await user.type(passwordInput, 'wrongpassword');
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
      });
    });
  });

  describe('Registration Flow', () => {
    it('validates all required fields on register', async () => {
      const user = userEvent.setup();
      render(<Register />);

      const submitButton = screen.getByRole('button', {
        name: /create account/i,
      });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Email is required')).toBeInTheDocument();
        expect(screen.getByText('First name is required')).toBeInTheDocument();
        expect(screen.getByText('Last name is required')).toBeInTheDocument();
      });
    });

    it('validates password match on register', async () => {
      const user = userEvent.setup();
      render(<Register />);

      const emailInput = screen.getByPlaceholderText('you@example.com');
      const firstNameInput = screen.getByPlaceholderText('John');
      const lastNameInput = screen.getByPlaceholderText('Doe');
      const passwordInputs = screen.getAllByPlaceholderText(/password/i);
      const submitButton = screen.getByRole('button', {
        name: /create account/i,
      });

      await user.type(emailInput, 'test@example.com');
      await user.type(firstNameInput, 'John');
      await user.type(lastNameInput, 'Doe');
      await user.type(passwordInputs[0], 'password123');
      await user.type(passwordInputs[1], 'password456');
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Passwords do not match')).toBeInTheDocument();
      });
    });

    it('validates terms agreement on register', async () => {
      const user = userEvent.setup();
      render(<Register />);

      const emailInput = screen.getByPlaceholderText('you@example.com');
      const firstNameInput = screen.getByPlaceholderText('John');
      const lastNameInput = screen.getByPlaceholderText('Doe');
      const passwordInputs = screen.getAllByPlaceholderText(/password/i);
      const submitButton = screen.getByRole('button', {
        name: /create account/i,
      });

      await user.type(emailInput, 'test@example.com');
      await user.type(firstNameInput, 'John');
      await user.type(lastNameInput, 'Doe');
      await user.type(passwordInputs[0], 'password123');
      await user.type(passwordInputs[1], 'password123');
      await user.click(submitButton);

      await waitFor(() => {
        expect(
          screen.getByText('You must agree to the Terms of Service')
        ).toBeInTheDocument();
      });
    });

    it('submits registration with valid data', async () => {
      const user = userEvent.setup();
      const mockApiPost = vi.fn().mockResolvedValue({
        data: {
          tokens: { access: 'test-token', refresh: 'refresh-token' },
          user: {
            id: 1,
            email: 'test@example.com',
            first_name: 'John',
            last_name: 'Doe',
          },
        },
      });
      (api.default.post as any) = mockApiPost;

      render(<Register />);

      const emailInput = screen.getByPlaceholderText('you@example.com');
      const firstNameInput = screen.getByPlaceholderText('John');
      const lastNameInput = screen.getByPlaceholderText('Doe');
      const passwordInputs = screen.getAllByPlaceholderText(/password/i);
      const termsCheckbox = screen.getByRole('checkbox', {
        name: /i agree to the/i,
      });
      const submitButton = screen.getByRole('button', {
        name: /create account/i,
      });

      await user.type(emailInput, 'test@example.com');
      await user.type(firstNameInput, 'John');
      await user.type(lastNameInput, 'Doe');
      await user.type(passwordInputs[0], 'password123');
      await user.type(passwordInputs[1], 'password123');
      await user.click(termsCheckbox);
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockApiPost).toHaveBeenCalledWith(
          '/auth/register/',
          expect.objectContaining({
            email: 'test@example.com',
            first_name: 'John',
            last_name: 'Doe',
          })
        );
      });
    });
  });

  describe('Auth State Management', () => {
    it('clears error messages on input change', async () => {
      const user = userEvent.setup();
      render(<Login />);

      // Trigger validation error
      const submitButton = screen.getByRole('button', { name: /sign in/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Email is required')).toBeInTheDocument();
      });

      // Type email - error should clear
      const emailInput = screen.getByPlaceholderText('you@example.com');
      await user.type(emailInput, 't');

      await waitFor(() => {
        expect(screen.queryByText('Email is required')).not.toBeInTheDocument();
      });
    });
  });
});
