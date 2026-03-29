import { useEffect, useState } from 'react';
import { useTransactionStore } from '@/store/transactionStore';
import { MainLayout, Card, Breadcrumb, Button, Modal, Input, Select, Spinner, Alert } from '@/components';
import { formatCurrency, formatDate } from '@/utils/formatters';
import { RecurrencePattern, RecurrenceFrequency } from '@/types/api';

export function RecurringTransactions() {
  const {
    transactions,
    recurringPredictions,
    fetchTransactions,
    getRecurringPredictions,
    getRecurringTransactions,
    autoCreateRecurringTransactions,
    updateRecurrencePattern,
    deleteTransaction,
    isLoading,
    error,
  } = useTransactionStore();

  // UI State
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedTransaction, setSelectedTransaction] = useState<any>(null);
  const [deleteConfirmation, setDeleteConfirmation] = useState<{
    isOpen: boolean;
    transactionId?: number;
  }>({ isOpen: false });
  const [formData, setFormData] = useState<Partial<RecurrencePattern>>({
    frequency: 'monthly',
    interval: 1,
  });

  // Load data
  useEffect(() => {
    loadRecurringData();
  }, []);

  const loadRecurringData = async () => {
    try {
      await Promise.all([getRecurringPredictions(), getRecurringTransactions()]);
    } catch (err) {
      console.error('Failed to load recurring data:', err);
    }
  };

  const handleEditRecurrence = (transaction: any) => {
    setSelectedTransaction(transaction);
    if (transaction.recurrence_pattern) {
      setFormData(transaction.recurrence_pattern);
    }
    setShowEditModal(true);
  };

  const handleSaveRecurrence = async () => {
    if (!selectedTransaction) return;

    try {
      await updateRecurrencePattern(selectedTransaction.id, formData as RecurrencePattern);
      setShowEditModal(false);
      setSelectedTransaction(null);
      await loadRecurringData();
    } catch (err) {
      console.error('Failed to update recurrence pattern:', err);
    }
  };

  const handleAutoCreate = async () => {
    try {
      await autoCreateRecurringTransactions();
      await loadRecurringData();
    } catch (err) {
      console.error('Failed to auto-create recurring transactions:', err);
    }
  };

  const handleDeleteConfirm = async () => {
    if (!deleteConfirmation.transactionId) return;

    try {
      await deleteTransaction(deleteConfirmation.transactionId);
      await loadRecurringData();
      setDeleteConfirmation({ isOpen: false });
    } catch (err) {
      console.error('Failed to delete recurring transaction:', err);
    }
  };

  // Filter recurring transactions
  const recurringTransactions = transactions.filter(t => t.is_recurring);

  if (isLoading && recurringTransactions.length === 0) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center min-h-screen">
          <Spinner size="large" />
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      {/* Breadcrumb */}
      <Breadcrumb
        items={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Recurring Transactions' },
        ]}
      />

      {/* Page Header */}
      <div className="flex items-center justify-between mt-8 mb-8">
        <div>
          <h1 className="text-3xl font-bold text-neutral-900">Recurring Transactions</h1>
          <p className="text-neutral-600 mt-2">Manage automatic recurring payments and income</p>
        </div>
        <Button onClick={handleAutoCreate} className="bg-secondary-600 hover:bg-secondary-700 text-white">
          🔄 Auto-Create Now
        </Button>
      </div>

      {error && (
        <Alert variant="error" closeable className="mb-8">
          {error}
        </Alert>
      )}

      {/* Upcoming Predictions */}
      {recurringPredictions.length > 0 && (
        <Card className="mb-8 bg-gradient-to-r from-primary-50 to-secondary-50">
          <div>
            <h2 className="text-xl font-bold text-neutral-900 mb-6">📅 Upcoming Auto-Generated Transactions</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {recurringPredictions.map((prediction) => (
                <div key={prediction.transaction_id} className="bg-white rounded-lg p-4 border border-primary-200">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <p className="font-bold text-neutral-900">{prediction.transaction_id}</p>
                      <p className="text-sm text-neutral-600">{prediction.frequency}</p>
                    </div>
                    <div className="flex items-baseline gap-2">
                      <span
                        className={`text-lg font-bold ${
                          prediction.estimated_amount > 0 ? 'text-success-600' : 'text-error-600'
                        }`}
                      >
                        {prediction.estimated_amount > 0 ? '+' : '-'}
                        {formatCurrency(Math.abs(prediction.estimated_amount))}
                      </span>
                      <span className="text-xs text-neutral-600">
                        {prediction.estimated_amount > 0 ? '(Income)' : '(Expense)'}
                      </span>
                    </div>
                  </div>
                  <div className="pt-2 border-t border-neutral-200 text-xs text-neutral-500">
                    <p>Next: {formatDate(prediction.next_occurrence_date)}</p>
                    <p>Last: {formatDate(prediction.last_occurrence)}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </Card>
      )}

      {/* Recurring Transactions List */}
      {recurringTransactions.length === 0 ? (
        <Card>
          <div className="py-12 text-center">
            <p className="text-neutral-600 mb-4">No recurring transactions set up yet</p>
            <p className="text-sm text-neutral-500">Enable recurring transactions on individual expense or income items to see them here</p>
          </div>
        </Card>
      ) : (
        <Card>
          <div>
            <h2 className="text-xl font-bold text-neutral-900 mb-6">Your Recurring Transactions</h2>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-neutral-200">
                    <th className="text-left py-3 px-4 font-semibold text-neutral-700">Title</th>
                    <th className="text-left py-3 px-4 font-semibold text-neutral-700">Amount</th>
                    <th className="text-left py-3 px-4 font-semibold text-neutral-700">Frequency</th>
                    <th className="text-left py-3 px-4 font-semibold text-neutral-700">Type</th>
                    <th className="text-center py-3 px-4 font-semibold text-neutral-700">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {recurringTransactions.map((transaction) => (
                    <tr
                      key={transaction.id}
                      className="border-b border-neutral-200 hover:bg-neutral-50 transition-colors"
                    >
                      <td className="py-3 px-4 font-medium text-neutral-900">{transaction.title}</td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <span className={`font-bold ${
                            transaction.type === 'income' ? 'text-success-600' : 'text-error-600'
                          }`}
                          >
                            {transaction.type === 'income' ? '+' : '-'}
                            {formatCurrency(transaction.amount)}
                          </span>
                          <span className="sr-only">
                            {transaction.type === 'income' ? 'income' : 'expense'}
                          </span>
                        </div>
                      </td>
                      <td className="py-3 px-4 text-neutral-600">
                        <span className="inline-block px-2 py-1 text-xs font-medium bg-primary-100 text-primary-800 rounded">
                          {transaction.recurring_frequency}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-neutral-600 capitalize">{transaction.type}</td>
                      <td className="py-3 px-4 text-center">
                        <div className="flex gap-2 justify-center">
                          <Button
                            onClick={() => handleEditRecurrence(transaction)}
                            className="px-3 py-2 text-sm font-medium text-primary-600 hover:bg-primary-50 rounded"
                          >
                            Edit
                          </Button>
                          <Button
                            onClick={() => setDeleteConfirmation({ isOpen: true, transactionId: transaction.id })}
                            className="px-3 py-2 text-sm font-medium text-error-600 hover:bg-error-50 rounded"
                          >
                            Delete
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </Card>
      )}

      {/* Edit Recurrence Modal */}
      <Modal
        isOpen={showEditModal}
        onClose={() => setShowEditModal(false)}
        title="Edit Recurrence Pattern"
      >
        <form className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-2">Frequency</label>
            <Select
              value={formData.frequency || 'monthly'}
              onChange={(e) =>
                setFormData((prev) => ({
                  ...prev,
                  frequency: e.target.value as RecurrenceFrequency,
                }))
              }
              options={[
                { value: 'daily', label: 'Daily' },
                { value: 'weekly', label: 'Weekly' },
                { value: 'bi_weekly', label: 'Bi-Weekly' },
                { value: 'monthly', label: 'Monthly' },
                { value: 'bi_monthly', label: 'Bi-Monthly' },
                { value: 'quarterly', label: 'Quarterly' },
                { value: 'semi_annual', label: 'Semi-Annual' },
                { value: 'yearly', label: 'Yearly' },
              ]}
            />
          </div>

          <Input
            label="Every N Periods"
            type="number"
            min="1"
            value={formData.interval || 1}
            onChange={(e) =>
              setFormData((prev) => ({
                ...prev,
                interval: parseInt(e.target.value) || 1,
              }))
            }
          />

          {['monthly', 'yearly'].includes(formData.frequency || '') && (
            <Input
              label="Day of Month (1-31)"
              type="number"
              min="1"
              max="31"
              value={formData.on_day || 1}
              onChange={(e) =>
                setFormData((prev) => ({
                  ...prev,
                  on_day: parseInt(e.target.value) || 1,
                }))
              }
            />
          )}

          {formData.frequency === 'yearly' && (
            <Input
              label="Month (1-12)"
              type="number"
              min="1"
              max="12"
              value={formData.on_month || 1}
              onChange={(e) =>
                setFormData((prev) => ({
                  ...prev,
                  on_month: parseInt(e.target.value) || 1,
                }))
              }
            />
          )}

          <Input
            label="End Date (Optional)"
            type="date"
            value={formData.end_date || ''}
            onChange={(e) =>
              setFormData((prev) => ({
                ...prev,
                end_date: e.target.value || undefined,
              }))
            }
          />

          <Input
            label="Max Occurrences (Optional)"
            type="number"
            min="1"
            value={formData.max_occurrences || ''}
            onChange={(e) =>
              setFormData((prev) => ({
                ...prev,
                max_occurrences: e.target.value ? parseInt(e.target.value) : undefined,
              }))
            }
          />

          <div className="flex gap-3 justify-end pt-4 border-t border-neutral-200">
            <Button
              type="button"
              onClick={() => setShowEditModal(false)}
              className="px-4 py-2 text-neutral-700 bg-neutral-100 hover:bg-neutral-200 rounded-lg"
            >
              Cancel
            </Button>
            <Button
              type="button"
              onClick={handleSaveRecurrence}
              className="px-4 py-2 bg-primary-600 text-white hover:bg-primary-700 rounded-lg"
            >
              Save Pattern
            </Button>
          </div>
        </form>
      </Modal>

      {/* Delete Recurring Transaction Confirmation Modal */}
      <Modal
        isOpen={deleteConfirmation.isOpen}
        onClose={() => setDeleteConfirmation({ isOpen: false })}
        title="Delete Recurring Transaction"
        size="small"
      >
        <div className="space-y-4">
          <p className="text-neutral-700">
            Are you sure you want to delete this recurring transaction? This action cannot be undone.
          </p>
          <div className="flex justify-end gap-3">
            <Button
              onClick={() => setDeleteConfirmation({ isOpen: false })}
              className="px-4 py-2 text-neutral-700 bg-neutral-100 hover:bg-neutral-200 rounded-lg"
            >
              Cancel
            </Button>
            <Button
              onClick={handleDeleteConfirm}
              className="px-4 py-2 bg-error-600 text-white hover:bg-error-700 rounded-lg"
            >
              Delete
            </Button>
          </div>
        </div>
      </Modal>
    </MainLayout>
  );
}
