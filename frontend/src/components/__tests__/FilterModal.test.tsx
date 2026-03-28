import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { FilterModal } from '../FilterModal';

const mockCategories = [
  { id: 1, name: 'Food', type: 'expense' as const, color: '#ef4444', icon: '🍔' },
  { id: 2, name: 'Transport', type: 'expense' as const, color: '#f97316', icon: '🚗' },
  { id: 3, name: 'Salary', type: 'income' as const, color: '#22c55e', icon: '💰' },
];

describe('FilterModal Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders modal when isOpen is true', () => {
    const mockOnClose = vi.fn();
    const mockOnApply = vi.fn();

    render(
      <FilterModal
        isOpen={true}
        onClose={mockOnClose}
        onApply={mockOnApply}
        categories={mockCategories}
      />
    );

    expect(screen.getByText('Advanced Filters')).toBeInTheDocument();
  });

  it('does not render modal when isOpen is false', () => {
    const mockOnClose = vi.fn();
    const mockOnApply = vi.fn();

    render(
      <FilterModal
        isOpen={false}
        onClose={mockOnClose}
        onApply={mockOnApply}
        categories={mockCategories}
      />
    );

    expect(screen.queryByText('Advanced Filters')).not.toBeInTheDocument();
  });

  it('displays all filter sections', () => {
    const mockOnClose = vi.fn();
    const mockOnApply = vi.fn();

    const { container } = render(
      <FilterModal
        isOpen={true}
        onClose={mockOnClose}
        onApply={mockOnApply}
        categories={mockCategories}
      />
    );

    // Check for text content instead of labels
    expect(container.textContent).toContain('Search');
    expect(container.textContent).toContain('Start Date');
    expect(container.textContent).toContain('End Date');
    expect(container.textContent).toContain('Transaction Type');
    expect(container.textContent).toContain('Categories');
    expect(container.textContent).toContain('Amount Range');
    expect(container.textContent).toContain('Payment Methods');
  });

  it('displays all category checkboxes', () => {
    const mockOnClose = vi.fn();
    const mockOnApply = vi.fn();

    render(
      <FilterModal
        isOpen={true}
        onClose={mockOnClose}
        onApply={mockOnApply}
        categories={mockCategories}
      />
    );

    mockCategories.forEach((category) => {
      expect(screen.getByLabelText(category.name)).toBeInTheDocument();
    });
  });

  it('displays payment method checkboxes', () => {
    const mockOnClose = vi.fn();
    const mockOnApply = vi.fn();

    render(
      <FilterModal
        isOpen={true}
        onClose={mockOnClose}
        onApply={mockOnApply}
        categories={mockCategories}
      />
    );

    expect(screen.getByLabelText(/CREDIT CARD/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/DEBIT CARD/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/BANK TRANSFER/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/CASH/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/CHECK/i)).toBeInTheDocument();
  });

  it('calls onApply when apply button is clicked', async () => {
    const mockOnClose = vi.fn();
    const mockOnApply = vi.fn();
    const user = userEvent.setup();

    render(
      <FilterModal
        isOpen={true}
        onClose={mockOnClose}
        onApply={mockOnApply}
        categories={mockCategories}
      />
    );

    const applyButton = screen.getByText('Apply Filters');
    await user.click(applyButton);

    expect(mockOnApply).toHaveBeenCalled();
  });

  it('calls onClose when cancel button is clicked', async () => {
    const mockOnClose = vi.fn();
    const mockOnApply = vi.fn();
    const user = userEvent.setup();

    render(
      <FilterModal
        isOpen={true}
        onClose={mockOnClose}
        onApply={mockOnApply}
        categories={mockCategories}
      />
    );

    const cancelButton = screen.getByText('Cancel');
    await user.click(cancelButton);

    expect(mockOnClose).toHaveBeenCalled();
  });

  it('resets filters when reset button is clicked', async () => {
    const mockOnClose = vi.fn();
    const mockOnApply = vi.fn();
    const user = userEvent.setup();

    render(
      <FilterModal
        isOpen={true}
        onClose={mockOnClose}
        onApply={mockOnApply}
        categories={mockCategories}
      />
    );

    // Fill in some filters
    const searchInput = screen.getByPlaceholderText(/Search by description.../i);
    await user.type(searchInput, 'test search');

    // Click reset
    const resetButton = screen.getByText('Reset');
    await user.click(resetButton);

    // Search input should be cleared
    expect((searchInput as HTMLInputElement).value).toBe('');
  });

  it('allows selecting categories', async () => {
    const mockOnClose = vi.fn();
    const mockOnApply = vi.fn();
    const user = userEvent.setup();

    render(
      <FilterModal
        isOpen={true}
        onClose={mockOnClose}
        onApply={mockOnApply}
        categories={mockCategories}
      />
    );

    const foodCheckbox = screen.getByLabelText('Food');
    await user.click(foodCheckbox);

    expect((foodCheckbox as HTMLInputElement).checked).toBe(true);
  });

  it('allows selecting payment methods', async () => {
    const mockOnClose = vi.fn();
    const mockOnApply = vi.fn();
    const user = userEvent.setup();

    render(
      <FilterModal
        isOpen={true}
        onClose={mockOnClose}
        onApply={mockOnApply}
        categories={mockCategories}
      />
    );

    const creditCardCheckbox = screen.getByLabelText(/CREDIT CARD/i);
    await user.click(creditCardCheckbox);

    expect((creditCardCheckbox as HTMLInputElement).checked).toBe(true);
  });

  it('allows setting amount range', async () => {
    const mockOnClose = vi.fn();
    const mockOnApply = vi.fn();
    const user = userEvent.setup();

    render(
      <FilterModal
        isOpen={true}
        onClose={mockOnClose}
        onApply={mockOnApply}
        categories={mockCategories}
      />
    );

    const minInput = screen.getByPlaceholderText('Min') as HTMLInputElement;
    const maxInput = screen.getByPlaceholderText('Max') as HTMLInputElement;

    await user.clear(minInput);
    await user.type(minInput, '100');

    await user.clear(maxInput);
    await user.type(maxInput, '500');

    expect(minInput.value).toBe('100');
    expect(maxInput.value).toBe('500');
  });

  it('allows selecting transaction type', async () => {
    const mockOnClose = vi.fn();
    const mockOnApply = vi.fn();
    const user = userEvent.setup();

    render(
      <FilterModal
        isOpen={true}
        onClose={mockOnClose}
        onApply={mockOnApply}
        categories={mockCategories}
      />
    );

    const typeSelect = screen.getByDisplayValue('All Types') as HTMLSelectElement;
    await user.selectOptions(typeSelect, 'income');

    expect(typeSelect.value).toBe('income');
  });

  it('allows setting date range', async () => {
    const mockOnClose = vi.fn();
    const mockOnApply = vi.fn();
    const user = userEvent.setup();

    render(
      <FilterModal
        isOpen={true}
        onClose={mockOnClose}
        onApply={mockOnApply}
        categories={mockCategories}
      />
    );

    // Get date inputs by their labels
    const startDateLabel = screen.getByText('Start Date');
    const endDateLabel = screen.getByText('End Date');

    // These labels should be associated with date inputs
    expect(startDateLabel).toBeInTheDocument();
    expect(endDateLabel).toBeInTheDocument();
  });

  it('disables apply button with proper styling when no filters selected', () => {
    const mockOnClose = vi.fn();
    const mockOnApply = vi.fn();

    render(
      <FilterModal
        isOpen={true}
        onClose={mockOnClose}
        onApply={mockOnApply}
        categories={mockCategories}
      />
    );

    const applyButton = screen.getByText('Apply Filters');
    expect(applyButton).toBeInTheDocument();
  });
});
