import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Input } from '../Input';

describe('Input Component', () => {
  it('renders input field', () => {
    render(<Input id="test-input" />);
    expect(screen.getByRole('textbox')).toBeInTheDocument();
  });

  it('renders with label', () => {
    render(<Input id="test-input" label="Email" />);
    expect(screen.getByLabelText('Email')).toBeInTheDocument();
  });

  it('renders required indicator', () => {
    render(<Input id="test-input" label="Email" required />);
    expect(screen.getByText('*')).toBeInTheDocument();
  });

  it('renders placeholder text', () => {
    render(<Input id="test-input" placeholder="Enter email" />);
    const input = screen.getByRole('textbox') as HTMLInputElement;
    expect(input.placeholder).toBe('Enter email');
  });

  it('updates value on input change', async () => {
    const user = userEvent.setup();
    const handleChange = vi.fn();
    render(
      <Input
        id="test-input"
        value="test"
        onChange={handleChange}
      />
    );

    const input = screen.getByRole('textbox');
    await user.type(input, 'test');
    expect(handleChange).toHaveBeenCalled();
  });

  it('renders error message', () => {
    render(<Input id="test-input" error="This field is required" />);
    expect(screen.getByText('This field is required')).toBeInTheDocument();
  });

  it('renders helper text when no error', () => {
    render(<Input id="test-input" helperText="Use a strong password" />);
    expect(screen.getByText('Use a strong password')).toBeInTheDocument();
  });

  it('does not show helper text when error is present', () => {
    render(
      <Input
        id="test-input"
        error="Required"
        helperText="Use a strong password"
      />
    );
    expect(screen.getByText('Required')).toBeInTheDocument();
    expect(screen.queryByText('Use a strong password')).not.toBeInTheDocument();
  });

  it('disables input when disabled prop is true', () => {
    render(<Input id="test-input" disabled />);
    expect(screen.getByRole('textbox')).toBeDisabled();
  });

  it('renders password variant with show/hide button', () => {
    render(<Input id="test-input" variant="password" />);
    const input = document.querySelector('#test-input') as HTMLInputElement;
    expect(input).toHaveAttribute('type', 'password');
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('toggles password visibility', async () => {
    const user = userEvent.setup();
    render(<Input id="test-input" variant="password" />);

    const input = document.querySelector('#test-input') as HTMLInputElement;
    const button = screen.getByRole('button');

    expect(input.type).toBe('password');

    await user.click(button);
    expect(input.type).toBe('text');

    await user.click(button);
    expect(input.type).toBe('password');
  });

  it('renders email type input', () => {
    render(<Input id="test-input" type="email" />);
    expect(screen.getByRole('textbox')).toHaveAttribute('type', 'email');
  });

  it('renders number type input', () => {
    render(<Input id="test-input" type="number" />);
    const input = screen.getByRole('spinbutton');
    expect(input).toHaveAttribute('type', 'number');
  });

  it('applies error styling to border', () => {
    render(<Input id="test-input" error="Error" />);
    const input = screen.getByRole('textbox');
    expect(input).toHaveClass('border-error-300');
  });

  it('applies normal border styling without error', () => {
    render(<Input id="test-input" />);
    const input = screen.getByRole('textbox');
    expect(input).toHaveClass('border-neutral-300');
  });

  it('renders with custom className', () => {
    render(<Input id="test-input" className="custom-class" />);
    const input = screen.getByRole('textbox');
    expect(input).toHaveClass('custom-class');
  });
});
