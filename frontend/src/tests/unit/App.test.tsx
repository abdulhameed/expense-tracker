import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import App from '../../App';
import { useAuthStore } from '@/store/authStore';

describe('App Router', () => {
  it('renders without crashing', () => {
    const { container } = render(<App />);
    expect(container).toBeDefined();
  });

  it('initializes auth store correctly', () => {
    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.isAuthenticated).toBe(false);
  });

  it('provides auth methods in store', () => {
    const state = useAuthStore.getState();
    expect(typeof state.login).toBe('function');
    expect(typeof state.register).toBe('function');
    expect(typeof state.logout).toBe('function');
  });

  it('provides error clearing method', () => {
    const state = useAuthStore.getState();
    expect(typeof state.clearError).toBe('function');
  });

  it('initializes with loading state as false', () => {
    const state = useAuthStore.getState();
    expect(state.isLoading).toBe(false);
  });
});
