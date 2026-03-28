import { useState, useEffect } from 'react';
import { Modal, Input, Select, Button, Spinner, Alert } from '@/components';
import { Transaction, Category } from '@/types/api';
import { isValidAmount } from '@/utils/validation';

interface TransactionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: any) => Promise<void>;
  transaction?: Transaction;
  categories: Category[];
  isLoading?: boolean;
  error?: string;
}

export function TransactionModal({
  isOpen,
  onClose,
  onSubmit,
  transaction,
  categories,
  isLoading = false,
  error,
}: TransactionModalProps) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    amount: '',
    type: 'expense' as 'income' | 'expense',
    category_id: '',
    date: new Date().toISOString().split('T')[0],
    payment_method: '',
    reference_number: '',
    is_recurring: false,
    recurring_frequency: '',
    tags: '',
  });

  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  // Initialize form with transaction data
  useEffect(() => {
    if (transaction) {
      setFormData({
        title: transaction.title,
        description: transaction.description || '',
        amount: transaction.amount.toString(),
        type: transaction.type,
        category_id: transaction.category_id.toString(),
        date: transaction.date.split('T')[0],
        payment_method: transaction.payment_method || '',
        reference_number: transaction.reference_number || '',
        is_recurring: transaction.is_recurring,
        recurring_frequency: transaction.recurring_frequency || '',
        tags: transaction.tags?.join(', ') || '',
      });
    }
  }, [transaction, isOpen]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value, type } = e.target as any;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value,
    }));

    // Clear error for this field
    if (validationErrors[name]) {
      setValidationErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!formData.title.trim()) {
      errors.title = 'Title is required';
    }

    if (!formData.amount) {
      errors.amount = 'Amount is required';
    } else if (!isValidAmount(formData.amount)) {
      errors.amount = 'Please enter a valid amount (e.g., 100.50)';
    }

    if (!formData.category_id) {
      errors.category_id = 'Category is required';
    }

    if (!formData.date) {
      errors.date = 'Date is required';
    }

    if (formData.is_recurring && !formData.recurring_frequency) {
      errors.recurring_frequency = 'Recurring frequency is required';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    const submitData = {
      title: formData.title.trim(),
      description: formData.description.trim() || undefined,
      amount: parseFloat(formData.amount),
      type: formData.type,
      category_id: parseInt(formData.category_id),
      date: formData.date,
      payment_method: formData.payment_method || undefined,
      reference_number: formData.reference_number || undefined,
      is_recurring: formData.is_recurring,
      recurring_frequency: formData.is_recurring ? formData.recurring_frequency : undefined,
      tags: formData.tags
        ? formData.tags.split(',').map((tag) => tag.trim())
        : undefined,
    };

    try {
      await onSubmit(submitData);
      onClose();
    } catch (err) {
      console.error('Failed to save transaction:', err);
    }
  };

  const expenseCategories = categories.filter((c) => c.type === formData.type);

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={transaction ? 'Edit Transaction' : 'Add New Transaction'}
      size="large"
      footer={
        <>
          <Button variant="secondary" onClick={onClose} disabled={isLoading}>
            Cancel
          </Button>
          <Button onClick={handleSubmit} isLoading={isLoading} disabled={isLoading}>
            {transaction ? 'Update Transaction' : 'Add Transaction'}
          </Button>
        </>
      }
    >
      <form onSubmit={handleSubmit} className="space-y-5">
        {error && (
          <Alert variant="error" closeable>
            {error}
          </Alert>
        )}

        {/* Transaction Type */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-2">
              Type *
            </label>
            <div className="flex gap-2">
              {(['income', 'expense'] as const).map((type) => (
                <button
                  key={type}
                  type="button"
                  onClick={() =>
                    setFormData((prev) => ({
                      ...prev,
                      type,
                      category_id: '', // Reset category when type changes
                    }))
                  }
                  className={`flex-1 py-2 px-4 rounded-lg font-medium transition-colors ${
                    formData.type === type
                      ? type === 'income'
                        ? 'bg-success-100 text-success-700 border border-success-300'
                        : 'bg-error-100 text-error-700 border border-error-300'
                      : 'bg-neutral-100 text-neutral-700 border border-neutral-300 hover:bg-neutral-200'
                  }`}
                >
                  {type === 'income' ? 'Income' : 'Expense'}
                </button>
              ))}
            </div>
          </div>

          {/* Amount */}
          <Input
            id="amount"
            name="amount"
            label="Amount *"
            type="number"
            value={formData.amount}
            onChange={handleChange}
            placeholder="0.00"
            step="0.01"
            min="0"
            error={validationErrors.amount}
            required
          />
        </div>

        {/* Title */}
        <Input
          id="title"
          name="title"
          label="Title *"
          value={formData.title}
          onChange={handleChange}
          placeholder="e.g., Grocery Shopping"
          error={validationErrors.title}
          required
        />

        {/* Description */}
        <div>
          <label htmlFor="description" className="block text-sm font-medium text-neutral-700 mb-2">
            Description
          </label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            placeholder="Add notes or details about this transaction..."
            className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            rows={3}
          />
        </div>

        {/* Category */}
        <Select
          id="category_id"
          name="category_id"
          label="Category *"
          value={formData.category_id}
          onChange={handleChange}
          options={expenseCategories.map((cat) => ({
            value: cat.id.toString(),
            label: cat.name,
          }))}
          error={validationErrors.category_id}
          required
        />

        {/* Date */}
        <Input
          id="date"
          name="date"
          label="Date *"
          type="date"
          value={formData.date}
          onChange={handleChange}
          error={validationErrors.date}
          required
        />

        {/* Payment Method */}
        <Select
          id="payment_method"
          name="payment_method"
          label="Payment Method"
          value={formData.payment_method}
          onChange={handleChange}
          options={[
            { value: '', label: 'Select payment method' },
            { value: 'cash', label: 'Cash' },
            { value: 'credit_card', label: 'Credit Card' },
            { value: 'debit_card', label: 'Debit Card' },
            { value: 'bank_transfer', label: 'Bank Transfer' },
            { value: 'check', label: 'Check' },
            { value: 'other', label: 'Other' },
          ]}
        />

        {/* Reference Number */}
        <Input
          id="reference_number"
          name="reference_number"
          label="Reference Number"
          value={formData.reference_number}
          onChange={handleChange}
          placeholder="e.g., Invoice, Check number, Transaction ID"
        />

        {/* Tags */}
        <Input
          id="tags"
          name="tags"
          label="Tags (comma-separated)"
          value={formData.tags}
          onChange={handleChange}
          placeholder="e.g., shopping, groceries, important"
        />

        {/* Recurring */}
        <div>
          <label className="flex items-center">
            <input
              type="checkbox"
              name="is_recurring"
              checked={formData.is_recurring}
              onChange={handleChange}
              className="w-4 h-4 text-primary-600 rounded border-neutral-300"
            />
            <span className="ml-3 text-sm font-medium text-neutral-700">
              This is a recurring transaction
            </span>
          </label>
        </div>

        {/* Recurring Frequency */}
        {formData.is_recurring && (
          <Select
            id="recurring_frequency"
            name="recurring_frequency"
            label="Recurring Frequency *"
            value={formData.recurring_frequency}
            onChange={handleChange}
            options={[
              { value: '', label: 'Select frequency' },
              { value: 'daily', label: 'Daily' },
              { value: 'weekly', label: 'Weekly' },
              { value: 'monthly', label: 'Monthly' },
              { value: 'yearly', label: 'Yearly' },
            ]}
            error={validationErrors.recurring_frequency}
            required
          />
        )}
      </form>
    </Modal>
  );
}
