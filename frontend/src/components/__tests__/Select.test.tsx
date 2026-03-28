import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Select } from '../Select';

describe('Select Component', () => {
  const options = [
    { value: '1', label: 'Option 1' },
    { value: '2', label: 'Option 2' },
    { value: '3', label: 'Option 3' },
  ];

  it('renders select element', () => {
    render(<Select id="test-select" options={options} />);
    expect(screen.getByRole('combobox')).toBeInTheDocument();
  });

  it('renders with label', () => {
    render(
      <Select
        id="test-select"
        label="Choose option"
        options={options}
      />
    );
    expect(screen.getByLabelText('Choose option')).toBeInTheDocument();
  });

  it('renders required indicator', () => {
    render(
      <Select
        id="test-select"
        label="Choose"
        options={options}
        required
      />
    );
    expect(screen.getByText('*')).toBeInTheDocument();
  });

  it('renders all options', () => {
    render(<Select id="test-select" options={options} />);
    options.forEach((option) => {
      expect(screen.getByRole('option', { name: option.label })).toBeInTheDocument();
    });
  });

  it('renders placeholder option', () => {
    render(
      <Select
        id="test-select"
        options={options}
        placeholder="Select an option"
      />
    );
    expect(
      screen.getByRole('option', { name: 'Select an option' })
    ).toBeInTheDocument();
  });

  it('updates value on selection', async () => {
    const user = userEvent.setup();
    const handleChange = vi.fn();
    render(
      <Select
        id="test-select"
        options={options}
        onChange={handleChange}
      />
    );

    const select = screen.getByRole('combobox');
    await user.selectOptions(select, '2');
    expect(handleChange).toHaveBeenCalled();
  });

  it('disables select when disabled prop is true', () => {
    render(
      <Select id="test-select" options={options} disabled />
    );
    expect(screen.getByRole('combobox')).toBeDisabled();
  });

  it('renders error message', () => {
    render(
      <Select
        id="test-select"
        options={options}
        error="This field is required"
      />
    );
    expect(screen.getByText('This field is required')).toBeInTheDocument();
  });

  it('renders helper text when no error', () => {
    render(
      <Select
        id="test-select"
        options={options}
        helperText="Select one option"
      />
    );
    expect(screen.getByText('Select one option')).toBeInTheDocument();
  });

  it('does not show helper text when error is present', () => {
    render(
      <Select
        id="test-select"
        options={options}
        error="Error"
        helperText="Helper text"
      />
    );
    expect(screen.getByText('Error')).toBeInTheDocument();
    expect(screen.queryByText('Helper text')).not.toBeInTheDocument();
  });

  it('applies error styling when error is present', () => {
    const { container } = render(
      <Select
        id="test-select"
        options={options}
        error="Error"
      />
    );
    const select = screen.getByRole('combobox');
    expect(select).toHaveClass('border-error-300');
  });

  it('applies custom className', () => {
    render(
      <Select
        id="test-select"
        options={options}
        className="custom-class"
      />
    );
    const select = screen.getByRole('combobox');
    expect(select).toHaveClass('custom-class');
  });
});
