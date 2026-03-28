import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Checkbox } from '../Checkbox';

describe('Checkbox Component', () => {
  it('renders checkbox', () => {
    render(<Checkbox id="test-checkbox" />);
    expect(screen.getByRole('checkbox')).toBeInTheDocument();
  });

  it('renders with label', () => {
    render(<Checkbox id="test-checkbox" label="Accept terms" />);
    expect(screen.getByLabelText('Accept terms')).toBeInTheDocument();
  });

  it('updates checked state on click', async () => {
    const user = userEvent.setup();
    const handleChange = vi.fn();
    render(
      <Checkbox
        id="test-checkbox"
        onChange={handleChange}
      />
    );

    const checkbox = screen.getByRole('checkbox');
    await user.click(checkbox);
    expect(handleChange).toHaveBeenCalled();
  });

  it('accepts checked prop', () => {
    render(<Checkbox id="test-checkbox" checked />);
    const checkbox = screen.getByRole('checkbox') as HTMLInputElement;
    expect(checkbox.checked).toBe(true);
  });

  it('disables checkbox when disabled prop is true', () => {
    render(<Checkbox id="test-checkbox" disabled />);
    expect(screen.getByRole('checkbox')).toBeDisabled();
  });

  it('renders error message', () => {
    render(<Checkbox id="test-checkbox" error="This field is required" />);
    expect(screen.getByText('This field is required')).toBeInTheDocument();
  });

  it('applies correct styling classes', () => {
    const { container } = render(<Checkbox id="test-checkbox" />);
    const checkbox = screen.getByRole('checkbox');
    expect(checkbox).toHaveClass('w-4');
    expect(checkbox).toHaveClass('h-4');
    expect(checkbox).toHaveClass('text-primary-600');
  });

  it('renders unchecked by default', () => {
    render(<Checkbox id="test-checkbox" />);
    const checkbox = screen.getByRole('checkbox') as HTMLInputElement;
    expect(checkbox.checked).toBe(false);
  });

  it('renders with custom className', () => {
    render(<Checkbox id="test-checkbox" className="custom-class" />);
    const checkbox = screen.getByRole('checkbox');
    expect(checkbox).toHaveClass('custom-class');
  });

  it('associates label with checkbox via htmlFor', () => {
    const { container } = render(
      <Checkbox id="my-checkbox" label="My checkbox" />
    );
    const label = screen.getByText('My checkbox');
    expect(label).toHaveAttribute('for', 'my-checkbox');
  });
});
