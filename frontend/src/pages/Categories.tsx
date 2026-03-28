import { useEffect, useState } from 'react';
import { useTransactionStore } from '@/store/transactionStore';
import { MainLayout, Card, Breadcrumb, Button, Input, Select, Modal, Spinner, Alert } from '@/components';
import { Category } from '@/types/api';

interface CategoryFormData {
  name: string;
  type: 'income' | 'expense';
  color?: string;
  icon?: string;
}

const COLORS = [
  '#ef4444', // red
  '#f97316', // orange
  '#eab308', // yellow
  '#22c55e', // green
  '#3b82f6', // blue
  '#8b5cf6', // purple
  '#ec4899', // pink
  '#06b6d4', // cyan
];

const ICONS = ['💰', '🎯', '🛒', '🍔', '🚗', '🎬', '📱', '⚡', '🏠', '🎓'];

export function Categories() {
  const { categories, fetchCategories, createCategory, updateCategory, deleteCategory, isLoading, error } =
    useTransactionStore();

  // Form state
  const [formData, setFormData] = useState<CategoryFormData>({
    name: '',
    type: 'expense',
    color: COLORS[0],
    icon: ICONS[0],
  });

  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  const [editingId, setEditingId] = useState<number | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState<number | null>(null);
  const [typeFilter, setTypeFilter] = useState<'all' | 'income' | 'expense'>('all');

  // Load categories on mount
  useEffect(() => {
    fetchCategories();
  }, [fetchCategories]);

  const filteredCategories = categories.filter((cat) => {
    if (typeFilter === 'all') return true;
    return cat.type === typeFilter;
  });

  const handleOpenModal = (category?: Category) => {
    if (category) {
      setFormData({
        name: category.name,
        type: category.type,
        color: category.color || COLORS[0],
        icon: category.icon || ICONS[0],
      });
      setEditingId(category.id);
    } else {
      setFormData({
        name: '',
        type: 'expense',
        color: COLORS[0],
        icon: ICONS[0],
      });
      setEditingId(null);
    }
    setValidationErrors({});
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingId(null);
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!formData.name.trim()) {
      errors.name = 'Category name is required';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    try {
      if (editingId) {
        await updateCategory(editingId, {
          name: formData.name.trim(),
          type: formData.type,
          color: formData.color,
          icon: formData.icon,
        });
      } else {
        await createCategory({
          name: formData.name.trim(),
          type: formData.type,
          color: formData.color,
          icon: formData.icon,
        });
      }
      handleCloseModal();
    } catch (err) {
      console.error('Failed to save category:', err);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteCategory(id);
      setDeleteConfirm(null);
    } catch (err) {
      console.error('Failed to delete category:', err);
    }
  };

  return (
    <MainLayout>
      {/* Breadcrumb */}
      <Breadcrumb
        items={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Categories' },
        ]}
      />

      {/* Page Header */}
      <div className="mt-8 mb-8 flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-neutral-900">Categories</h1>
          <p className="text-neutral-600 mt-2">Manage your income and expense categories</p>
        </div>
        <Button onClick={() => handleOpenModal()}>+ Add Category</Button>
      </div>

      {/* Filter */}
      <Card className="mb-8">
        <div>
          <Select
            id="type-filter"
            label="Filter by Type"
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value as any)}
            options={[
              { value: 'all', label: 'All Types' },
              { value: 'income', label: 'Income' },
              { value: 'expense', label: 'Expense' },
            ]}
          />
        </div>
      </Card>

      {/* Categories Grid */}
      <Card>
        {isLoading && filteredCategories.length === 0 ? (
          <div className="flex items-center justify-center py-12">
            <Spinner size="large" />
          </div>
        ) : filteredCategories.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-neutral-600 mb-4">No categories found</p>
            <Button onClick={() => handleOpenModal()}>Create Your First Category</Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredCategories.map((category) => (
              <div
                key={category.id}
                className="p-4 border border-neutral-200 rounded-lg hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <span className="text-3xl">{category.icon || '📁'}</span>
                    <div>
                      <h3 className="font-semibold text-neutral-900">{category.name}</h3>
                      <p className="text-xs text-neutral-500">
                        {category.type === 'income' ? 'Income' : 'Expense'}
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleOpenModal(category)}
                      className="text-primary-600 hover:text-primary-700 text-sm font-medium"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => setDeleteConfirm(category.id)}
                      className="text-error-600 hover:text-error-700 text-sm font-medium"
                    >
                      Delete
                    </button>
                  </div>
                </div>

                {category.color && (
                  <div
                    className="h-2 rounded-full"
                    style={{ backgroundColor: category.color }}
                  />
                )}
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Category Form Modal */}
      <Modal
        isOpen={showModal}
        onClose={handleCloseModal}
        title={editingId ? 'Edit Category' : 'Add New Category'}
        size="large"
        footer={
          <>
            <Button variant="secondary" onClick={handleCloseModal} disabled={isLoading}>
              Cancel
            </Button>
            <Button onClick={handleSubmit} isLoading={isLoading} disabled={isLoading}>
              {editingId ? 'Update Category' : 'Add Category'}
            </Button>
          </>
        }
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <Alert variant="error" closeable>
              {error}
            </Alert>
          )}

          {/* Name */}
          <Input
            id="name"
            name="name"
            label="Category Name *"
            value={formData.name}
            onChange={(e) =>
              setFormData((prev) => ({ ...prev, name: e.target.value }))
            }
            placeholder="e.g., Groceries, Salary"
            error={validationErrors.name}
            required
          />

          {/* Type */}
          <Select
            id="type"
            label="Type *"
            value={formData.type}
            onChange={(e) =>
              setFormData((prev) => ({ ...prev, type: e.target.value as 'income' | 'expense' }))
            }
            options={[
              { value: 'expense', label: 'Expense' },
              { value: 'income', label: 'Income' },
            ]}
            required
          />

          {/* Color */}
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-2">Color</label>
            <div className="flex gap-2 flex-wrap">
              {COLORS.map((color) => (
                <button
                  key={color}
                  type="button"
                  onClick={() => setFormData((prev) => ({ ...prev, color }))}
                  className={`w-8 h-8 rounded-full border-2 transition-all ${
                    formData.color === color ? 'border-neutral-900 scale-110' : 'border-neutral-300'
                  }`}
                  style={{ backgroundColor: color }}
                />
              ))}
            </div>
          </div>

          {/* Icon */}
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-2">Icon</label>
            <div className="flex gap-2 flex-wrap">
              {ICONS.map((icon) => (
                <button
                  key={icon}
                  type="button"
                  onClick={() => setFormData((prev) => ({ ...prev, icon }))}
                  className={`w-10 h-10 rounded-lg border-2 text-xl transition-all flex items-center justify-center ${
                    formData.icon === icon
                      ? 'border-neutral-900 bg-neutral-100 scale-110'
                      : 'border-neutral-300 hover:border-neutral-400'
                  }`}
                >
                  {icon}
                </button>
              ))}
            </div>
          </div>
        </form>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={deleteConfirm !== null}
        onClose={() => setDeleteConfirm(null)}
        title="Delete Category"
        footer={
          <>
            <Button variant="secondary" onClick={() => setDeleteConfirm(null)}>
              Cancel
            </Button>
            <Button
              variant="danger"
              onClick={() => deleteConfirm !== null && handleDelete(deleteConfirm)}
            >
              Delete
            </Button>
          </>
        }
      >
        <p className="text-neutral-700">
          Are you sure you want to delete this category? Transactions with this category will not be affected.
        </p>
      </Modal>

      {error && (
        <div className="mt-8 p-4 bg-error-50 border border-error-200 rounded-lg">
          <p className="text-error-800">{error}</p>
        </div>
      )}
    </MainLayout>
  );
}
