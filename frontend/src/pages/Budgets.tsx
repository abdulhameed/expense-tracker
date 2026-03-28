import { useEffect, useState } from 'react';
import { useTransactionStore } from '@/store/transactionStore';
import { MainLayout, Card, Breadcrumb, Spinner, Alert, Button, Modal, Input, Select } from '@/components';
import { formatCurrency } from '@/utils/formatters';
import { Budget, BudgetProgress } from '@/types/api';

export function Budgets() {
  const {
    budgets,
    budgetProgress,
    fetchBudgets,
    fetchBudgetProgress,
    createBudget,
    updateBudget,
    deleteBudget,
    categories,
    fetchCategories,
    isLoading,
    error,
  } = useTransactionStore();

  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingBudget, setEditingBudget] = useState<Budget | null>(null);
  const [formData, setFormData] = useState({
    category_id: '',
    limit_amount: '',
    period: 'monthly' as const,
    alert_threshold: 80,
  });

  useEffect(() => {
    fetchBudgets();
    fetchBudgetProgress();
    fetchCategories();
  }, [fetchBudgets, fetchBudgetProgress, fetchCategories]);

  const handleOpenCreateModal = () => {
    setEditingBudget(null);
    setFormData({
      category_id: '',
      limit_amount: '',
      period: 'monthly',
      alert_threshold: 80,
    });
    setShowCreateModal(true);
  };

  const handleEditBudget = (budget: Budget) => {
    setEditingBudget(budget);
    setFormData({
      category_id: budget.category_id.toString(),
      limit_amount: budget.limit_amount.toString(),
      period: budget.period,
      alert_threshold: budget.alert_threshold,
    });
    setShowCreateModal(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const data = {
        category_id: parseInt(formData.category_id),
        limit_amount: parseFloat(formData.limit_amount),
        period: formData.period,
        alert_threshold: formData.alert_threshold,
        start_date: new Date().toISOString().split('T')[0],
        is_active: true,
      };

      if (editingBudget) {
        await updateBudget(editingBudget.id, data);
      } else {
        await createBudget(data);
      }

      setShowCreateModal(false);
      await fetchBudgets();
      await fetchBudgetProgress();
    } catch (err) {
      console.error('Failed to save budget:', err);
    }
  };

  const handleDeleteBudget = async (id: number) => {
    if (confirm('Are you sure you want to delete this budget?')) {
      try {
        await deleteBudget(id);
        await fetchBudgets();
        await fetchBudgetProgress();
      } catch (err) {
        console.error('Failed to delete budget:', err);
      }
    }
  };

  if (isLoading && budgets.length === 0) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center min-h-screen">
          <Spinner size="large" />
        </div>
      </MainLayout>
    );
  }

  const getProgressColor = (percentage: number) => {
    if (percentage >= 100) return 'bg-error-500';
    if (percentage >= 80) return 'bg-warning-500';
    return 'bg-success-500';
  };

  const getProgressTextColor = (percentage: number) => {
    if (percentage >= 100) return 'text-error-600';
    if (percentage >= 80) return 'text-warning-600';
    return 'text-success-600';
  };

  return (
    <MainLayout>
      {/* Breadcrumb */}
      <Breadcrumb
        items={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Budgets' },
        ]}
      />

      {/* Page Header */}
      <div className="flex items-center justify-between mt-8 mb-8">
        <div>
          <h1 className="text-3xl font-bold text-neutral-900">Budgets</h1>
          <p className="text-neutral-600 mt-2">Set and track spending limits by category</p>
        </div>
        <Button onClick={handleOpenCreateModal}>+ New Budget</Button>
      </div>

      {error && (
        <Alert variant="error" closeable className="mb-8">
          {error}
        </Alert>
      )}

      {/* Budget Overview */}
      {budgetProgress.length > 0 && (
        <Card className="mb-8">
          <div>
            <h2 className="text-xl font-bold text-neutral-900 mb-6">Budget Overview</h2>
            <div className="space-y-4">
              {budgetProgress.map((progress) => (
                <div key={progress.budget_id} className="border-b border-neutral-200 pb-4 last:border-b-0">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium text-neutral-900">{progress.category_name}</h3>
                    <span className={`text-sm font-bold ${getProgressTextColor(progress.percentage_used)}`}>
                      {progress.percentage_used.toFixed(1)}%
                    </span>
                  </div>

                  {/* Progress Bar */}
                  <div className="w-full bg-neutral-200 rounded-full h-2.5 mb-2">
                    <div
                      className={`h-2.5 rounded-full transition-all ${getProgressColor(progress.percentage_used)}`}
                      style={{ width: `${Math.min(progress.percentage_used, 100)}%` }}
                    />
                  </div>

                  {/* Budget Details */}
                  <div className="grid grid-cols-4 gap-4 text-sm">
                    <div>
                      <p className="text-neutral-600">Spent</p>
                      <p className="font-bold text-neutral-900">{formatCurrency(progress.spent_amount)}</p>
                    </div>
                    <div>
                      <p className="text-neutral-600">Limit</p>
                      <p className="font-bold text-neutral-900">{formatCurrency(progress.limit_amount)}</p>
                    </div>
                    <div>
                      <p className="text-neutral-600">Remaining</p>
                      <p className={`font-bold ${progress.remaining_amount >= 0 ? 'text-success-600' : 'text-error-600'}`}>
                        {formatCurrency(Math.abs(progress.remaining_amount))}
                      </p>
                    </div>
                    <div>
                      <p className="text-neutral-600">Status</p>
                      <p className={`font-bold ${progress.is_exceeded ? 'text-error-600' : 'text-success-600'}`}>
                        {progress.is_exceeded ? 'Exceeded' : 'On Track'}
                      </p>
                    </div>
                  </div>

                  {progress.alert_triggered && (
                    <div className="mt-2 p-2 bg-warning-50 border border-warning-200 rounded text-sm text-warning-800">
                      ⚠️ You've reached {progress.percentage_used.toFixed(1)}% of your budget for {progress.category_name}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </Card>
      )}

      {/* Budgets List */}
      {budgets.length === 0 ? (
        <Card>
          <div className="py-12 text-center">
            <p className="text-neutral-600 mb-4">No budgets created yet</p>
            <Button onClick={handleOpenCreateModal}>Create Your First Budget</Button>
          </div>
        </Card>
      ) : (
        <Card>
          <div>
            <h2 className="text-xl font-bold text-neutral-900 mb-6">Your Budgets</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {budgets.map((budget) => (
                <div
                  key={budget.id}
                  className="border border-neutral-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <p className="text-sm text-neutral-600">{budget.category.name}</p>
                      <p className="font-bold text-neutral-900">{formatCurrency(budget.limit_amount)}</p>
                    </div>
                    <span className="inline-block px-2 py-1 text-xs font-medium bg-primary-100 text-primary-800 rounded">
                      {budget.period}
                    </span>
                  </div>

                  <p className="text-xs text-neutral-500 mb-3">Alert at {budget.alert_threshold}%</p>

                  <div className="flex gap-2">
                    <button
                      onClick={() => handleEditBudget(budget)}
                      className="flex-1 px-3 py-2 text-sm font-medium text-primary-600 hover:bg-primary-50 rounded transition-colors"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDeleteBudget(budget.id)}
                      className="flex-1 px-3 py-2 text-sm font-medium text-error-600 hover:bg-error-50 rounded transition-colors"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </Card>
      )}

      {/* Create/Edit Budget Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        title={editingBudget ? 'Edit Budget' : 'Create New Budget'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <Select
            label="Category"
            required
            value={formData.category_id}
            onChange={(e) => setFormData((prev) => ({ ...prev, category_id: e.target.value }))}
            options={categories
              .filter((c) => c.type === 'expense')
              .map((c) => ({
                value: c.id.toString(),
                label: c.name,
              }))}
          />

          <Input
            label="Budget Limit"
            type="number"
            step="0.01"
            min="0"
            required
            value={formData.limit_amount}
            onChange={(e) => setFormData((prev) => ({ ...prev, limit_amount: e.target.value }))}
            placeholder="0.00"
          />

          <Select
            label="Period"
            value={formData.period}
            onChange={(e) => setFormData((prev) => ({ ...prev, period: e.target.value as any }))}
            options={[
              { value: 'monthly', label: 'Monthly' },
              { value: 'quarterly', label: 'Quarterly' },
              { value: 'yearly', label: 'Yearly' },
              { value: 'custom', label: 'Custom' },
            ]}
          />

          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-2">
              Alert Threshold: {formData.alert_threshold}%
            </label>
            <input
              type="range"
              min="1"
              max="100"
              value={formData.alert_threshold}
              onChange={(e) => setFormData((prev) => ({ ...prev, alert_threshold: parseInt(e.target.value) }))}
              className="w-full h-2 bg-neutral-200 rounded-lg appearance-none cursor-pointer"
            />
            <p className="text-xs text-neutral-500 mt-1">You'll be alerted when you reach this percentage</p>
          </div>

          <div className="flex gap-3 justify-end pt-4 border-t border-neutral-200">
            <Button
              type="button"
              onClick={() => setShowCreateModal(false)}
              className="px-4 py-2 text-neutral-700 bg-neutral-100 hover:bg-neutral-200 rounded-lg"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              className="px-4 py-2 bg-primary-600 text-white hover:bg-primary-700 rounded-lg"
            >
              {editingBudget ? 'Update Budget' : 'Create Budget'}
            </Button>
          </div>
        </form>
      </Modal>
    </MainLayout>
  );
}
