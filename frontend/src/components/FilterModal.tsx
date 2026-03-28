import { useState } from 'react';
import { Modal, Button, Input, Select, Checkbox } from '@/components';
import { FilterCriteria, Category } from '@/types/api';

interface FilterModalProps {
  isOpen: boolean;
  onClose: () => void;
  onApply: (filters: FilterCriteria) => void;
  categories: Category[];
}

export function FilterModal({ isOpen, onClose, onApply, categories }: FilterModalProps) {
  const [filters, setFilters] = useState<FilterCriteria>({
    dateRange: {
      start_date: '',
      end_date: '',
    },
    categories: [],
    transactionType: undefined,
    amountRange: {
      min: 0,
      max: 1000000,
    },
    searchQuery: '',
    tags: [],
    paymentMethods: [],
  });

  const [selectedCategories, setSelectedCategories] = useState<number[]>([]);
  const [selectedPaymentMethods, setSelectedPaymentMethods] = useState<string[]>([]);

  const handleCategoryToggle = (categoryId: number) => {
    setSelectedCategories((prev) =>
      prev.includes(categoryId) ? prev.filter((id) => id !== categoryId) : [...prev, categoryId]
    );
  };

  const handlePaymentMethodToggle = (method: string) => {
    setSelectedPaymentMethods((prev) =>
      prev.includes(method) ? prev.filter((m) => m !== method) : [...prev, method]
    );
  };

  const handleApply = () => {
    const appliedFilters: FilterCriteria = {
      ...filters,
      categories: selectedCategories.length > 0 ? selectedCategories : undefined,
      paymentMethods: selectedPaymentMethods.length > 0 ? selectedPaymentMethods : undefined,
      dateRange:
        filters.dateRange?.start_date || filters.dateRange?.end_date
          ? filters.dateRange
          : undefined,
    };

    onApply(appliedFilters);
    onClose();
  };

  const handleReset = () => {
    setFilters({
      dateRange: { start_date: '', end_date: '' },
      categories: [],
      transactionType: undefined,
      amountRange: { min: 0, max: 1000000 },
      searchQuery: '',
      tags: [],
      paymentMethods: [],
    });
    setSelectedCategories([]);
    setSelectedPaymentMethods([]);
  };

  const paymentMethods = ['credit_card', 'debit_card', 'bank_transfer', 'cash', 'check'];

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Advanced Filters">
      <div className="space-y-6">
        {/* Search Query */}
        <div>
          <label className="block text-sm font-medium text-neutral-700 mb-2">Search</label>
          <Input
            placeholder="Search by description..."
            value={filters.searchQuery || ''}
            onChange={(e) => setFilters((prev) => ({ ...prev, searchQuery: e.target.value }))}
          />
        </div>

        {/* Date Range */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-2">Start Date</label>
            <input
              type="date"
              value={filters.dateRange?.start_date || ''}
              onChange={(e) =>
                setFilters((prev) => ({
                  ...prev,
                  dateRange: { ...prev.dateRange, start_date: e.target.value },
                }))
              }
              className="w-full px-3 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-2">End Date</label>
            <input
              type="date"
              value={filters.dateRange?.end_date || ''}
              onChange={(e) =>
                setFilters((prev) => ({
                  ...prev,
                  dateRange: { ...prev.dateRange, end_date: e.target.value },
                }))
              }
              className="w-full px-3 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>

        {/* Transaction Type */}
        <Select
          label="Transaction Type"
          value={filters.transactionType || ''}
          onChange={(e) =>
            setFilters((prev) => ({
              ...prev,
              transactionType: (e.target.value as 'income' | 'expense') || undefined,
            }))
          }
          options={[
            { value: '', label: 'All Types' },
            { value: 'income', label: 'Income' },
            { value: 'expense', label: 'Expense' },
          ]}
        />

        {/* Categories */}
        <div>
          <label className="block text-sm font-medium text-neutral-700 mb-3">Categories</label>
          <div className="space-y-2 max-h-40 overflow-y-auto">
            {categories.map((category) => (
              <div key={category.id} className="flex items-center">
                <Checkbox
                  label={category.name}
                  checked={selectedCategories.includes(category.id)}
                  onChange={() => handleCategoryToggle(category.id)}
                />
              </div>
            ))}
          </div>
        </div>

        {/* Amount Range */}
        <div>
          <label className="block text-sm font-medium text-neutral-700 mb-3">Amount Range</label>
          <div className="grid grid-cols-2 gap-4">
            <Input
              type="number"
              placeholder="Min"
              value={filters.amountRange?.min || 0}
              onChange={(e) =>
                setFilters((prev) => ({
                  ...prev,
                  amountRange: {
                    ...prev.amountRange,
                    min: parseFloat(e.target.value) || 0,
                  },
                }))
              }
            />
            <Input
              type="number"
              placeholder="Max"
              value={filters.amountRange?.max || 1000000}
              onChange={(e) =>
                setFilters((prev) => ({
                  ...prev,
                  amountRange: {
                    ...prev.amountRange,
                    max: parseFloat(e.target.value) || 1000000,
                  },
                }))
              }
            />
          </div>
        </div>

        {/* Payment Methods */}
        <div>
          <label className="block text-sm font-medium text-neutral-700 mb-3">Payment Methods</label>
          <div className="space-y-2">
            {paymentMethods.map((method) => (
              <div key={method} className="flex items-center">
                <Checkbox
                  label={method.replace(/_/g, ' ').toUpperCase()}
                  checked={selectedPaymentMethods.includes(method)}
                  onChange={() => handlePaymentMethodToggle(method)}
                />
              </div>
            ))}
          </div>
        </div>

        {/* Buttons */}
        <div className="flex gap-3 justify-end pt-4 border-t border-neutral-200">
          <Button
            type="button"
            onClick={handleReset}
            className="px-4 py-2 text-neutral-700 bg-neutral-100 hover:bg-neutral-200 rounded-lg"
          >
            Reset
          </Button>
          <Button
            type="button"
            onClick={() => onClose()}
            className="px-4 py-2 text-neutral-700 bg-neutral-100 hover:bg-neutral-200 rounded-lg"
          >
            Cancel
          </Button>
          <Button
            type="button"
            onClick={handleApply}
            className="px-4 py-2 bg-primary-600 text-white hover:bg-primary-700 rounded-lg"
          >
            Apply Filters
          </Button>
        </div>
      </div>
    </Modal>
  );
}
