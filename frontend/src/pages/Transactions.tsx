import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useTransactionStore } from '@/store/transactionStore';
import { MainLayout, Card, Breadcrumb, Input, Select, Button, Spinner, Modal } from '@/components';
import { formatCurrency, formatDate } from '@/utils/formatters';

export function Transactions() {
  const { transactions, categories, fetchTransactions, fetchCategories, deleteTransaction, isLoading, error } =
    useTransactionStore();

  // Filters
  const [type, setType] = useState<'all' | 'income' | 'expense'>('all');
  const [categoryId, setCategoryId] = useState<string>('');
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState<'date' | 'amount'>('date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [page, setPage] = useState(1);

  // UI State
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const [deleteConfirm, setDeleteConfirm] = useState<number | null>(null);

  // Load data
  useEffect(() => {
    if (categories.length === 0) {
      fetchCategories();
    }
    loadTransactions();
  }, []);

  useEffect(() => {
    loadTransactions();
  }, [type, categoryId, search, sortBy, sortOrder, page]);

  const loadTransactions = () => {
    const filter: any = {
      page,
      limit: 20,
      sort_by: sortBy,
      sort_order: sortOrder,
    };

    if (type !== 'all') filter.type = type;
    if (categoryId) filter.category_id = parseInt(categoryId);
    if (search) filter.search = search;

    fetchTransactions(filter);
  };

  const handleSelectAll = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.checked) {
      setSelectedIds(new Set(transactions.map((t) => t.id)));
    } else {
      setSelectedIds(new Set());
    }
  };

  const handleSelectTransaction = (id: number) => {
    const newSelected = new Set(selectedIds);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedIds(newSelected);
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteTransaction(id);
      setDeleteConfirm(null);
    } catch (err) {
      console.error('Failed to delete transaction:', err);
    }
  };

  const categoryMap = categories.reduce(
    (acc, cat) => {
      acc[cat.id] = cat.name;
      return acc;
    },
    {} as Record<number, string>
  );

  return (
    <MainLayout>
      {/* Breadcrumb */}
      <Breadcrumb
        items={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Transactions' },
        ]}
      />

      {/* Page Header */}
      <div className="mt-8 mb-8 flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-neutral-900">Transactions</h1>
          <p className="text-neutral-600 mt-2">Manage your income and expenses</p>
        </div>
        <Link to="/transactions/new">
          <Button>+ Add Transaction</Button>
        </Link>
      </div>

      {/* Filters */}
      <Card className="mb-8">
        <div>
          <h3 className="text-lg font-bold text-neutral-900 mb-6">Filters</h3>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Type Filter */}
            <Select
              id="type-filter"
              label="Type"
              value={type}
              onChange={(e) => setType(e.target.value as any)}
              options={[
                { value: 'all', label: 'All Types' },
                { value: 'income', label: 'Income' },
                { value: 'expense', label: 'Expense' },
              ]}
            />

            {/* Category Filter */}
            <Select
              id="category-filter"
              label="Category"
              value={categoryId}
              onChange={(e) => setCategoryId(e.target.value)}
              options={[
                { value: '', label: 'All Categories' },
                ...categories.map((cat) => ({
                  value: cat.id.toString(),
                  label: cat.name,
                })),
              ]}
            />

            {/* Sort By */}
            <Select
              id="sort-by"
              label="Sort By"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              options={[
                { value: 'date', label: 'Date' },
                { value: 'amount', label: 'Amount' },
              ]}
            />

            {/* Sort Order */}
            <Select
              id="sort-order"
              label="Order"
              value={sortOrder}
              onChange={(e) => setSortOrder(e.target.value as any)}
              options={[
                { value: 'desc', label: 'Descending' },
                { value: 'asc', label: 'Ascending' },
              ]}
            />
          </div>

          {/* Search */}
          <div className="mt-4">
            <Input
              id="search"
              label="Search Transactions"
              placeholder="Search by title, description..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          {/* Bulk Actions */}
          {selectedIds.size > 0 && (
            <div className="mt-4 pt-4 border-t border-neutral-200 flex gap-3">
              <Button
                variant="danger"
                onClick={() =>
                  selectedIds.forEach((id) => {
                    deleteTransaction(id);
                  })
                }
              >
                Delete Selected ({selectedIds.size})
              </Button>
              <Button
                variant="secondary"
                onClick={() => setSelectedIds(new Set())}
              >
                Clear Selection
              </Button>
            </div>
          )}
        </div>
      </Card>

      {/* Transactions Table */}
      <Card>
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Spinner size="large" />
          </div>
        ) : transactions.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-neutral-600 mb-4">No transactions found</p>
            <Link to="/transactions/new">
              <Button>Create Your First Transaction</Button>
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-neutral-200">
                  <th className="text-left py-3 px-4 font-semibold text-neutral-700">
                    <input
                      type="checkbox"
                      checked={selectedIds.size === transactions.length && transactions.length > 0}
                      onChange={handleSelectAll}
                      className="w-4 h-4 text-primary-600 rounded border-neutral-300"
                    />
                  </th>
                  <th className="text-left py-3 px-4 font-semibold text-neutral-700">Date</th>
                  <th className="text-left py-3 px-4 font-semibold text-neutral-700">Title</th>
                  <th className="text-left py-3 px-4 font-semibold text-neutral-700">Category</th>
                  <th className="text-right py-3 px-4 font-semibold text-neutral-700">Amount</th>
                  <th className="text-center py-3 px-4 font-semibold text-neutral-700">Actions</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map((transaction) => (
                  <tr
                    key={transaction.id}
                    className="border-b border-neutral-200 hover:bg-neutral-50 transition-colors"
                  >
                    <td className="py-3 px-4">
                      <input
                        type="checkbox"
                        checked={selectedIds.has(transaction.id)}
                        onChange={() => handleSelectTransaction(transaction.id)}
                        className="w-4 h-4 text-primary-600 rounded border-neutral-300"
                      />
                    </td>
                    <td className="py-3 px-4 text-neutral-900">
                      {formatDate(transaction.date)}
                    </td>
                    <td className="py-3 px-4 text-neutral-900 font-medium">
                      <Link to={`/transactions/${transaction.id}`} className="text-primary-600 hover:text-primary-700">
                        {transaction.title}
                      </Link>
                    </td>
                    <td className="py-3 px-4 text-neutral-600">
                      {categoryMap[transaction.category_id] || 'Uncategorized'}
                    </td>
                    <td
                      className={`py-3 px-4 text-right font-bold ${
                        transaction.type === 'income'
                          ? 'text-success-600'
                          : 'text-error-600'
                      }`}
                    >
                      {transaction.type === 'income' ? '+' : '-'}
                      {formatCurrency(transaction.amount)}
                    </td>
                    <td className="py-3 px-4 text-center">
                      <div className="flex gap-2 justify-center">
                        <Link to={`/transactions/${transaction.id}/edit`}>
                          <Button variant="secondary" size="small">
                            Edit
                          </Button>
                        </Link>
                        <Button
                          variant="danger"
                          size="small"
                          onClick={() => setDeleteConfirm(transaction.id)}
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
        )}
      </Card>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={deleteConfirm !== null}
        onClose={() => setDeleteConfirm(null)}
        title="Delete Transaction"
        footer={
          <>
            <Button
              variant="secondary"
              onClick={() => setDeleteConfirm(null)}
            >
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
          Are you sure you want to delete this transaction? This action cannot be undone.
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
