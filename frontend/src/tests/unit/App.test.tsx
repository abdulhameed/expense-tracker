import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from '../../App';

describe('App Component', () => {
  it('renders without crashing', () => {
    render(<App />);
    expect(screen.getByText(/Expense Tracker/i)).toBeInTheDocument();
  });

  it('displays the setup complete message', () => {
    render(<App />);
    expect(screen.getByText(/Setup Complete/i)).toBeInTheDocument();
  });

  it('shows Vite setup confirmation', () => {
    render(<App />);
    expect(screen.getByText(/Vite \+ React \+ TypeScript configured/i)).toBeInTheDocument();
  });

  it('shows Tailwind CSS setup confirmation', () => {
    render(<App />);
    expect(screen.getByText(/Tailwind CSS with custom theme/i)).toBeInTheDocument();
  });

  it('shows testing framework setup confirmation', () => {
    render(<App />);
    expect(screen.getByText(/Testing framework \(Vitest\) ready/i)).toBeInTheDocument();
  });
});
