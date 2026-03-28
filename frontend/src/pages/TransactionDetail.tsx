import { useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useTransactionStore } from '@/store/transactionStore';
import { MainLayout, Card, Breadcrumb, Button, Spinner } from '@/components';
import { formatCurrency, formatDate } from '@/utils/formatters';

export function TransactionDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { selectedTransaction, fetchTransaction, isLoading } = useTransactionStore();

  useEffect(() => {
    if (id) {
      fetchTransaction(parseInt(id));
    }
  }, [id, fetchTransaction]);

  if (isLoading && !selectedTransaction) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center min-h-screen">
          <Spinner size="large" />
        </div>
      </MainLayout>
    );
  }

  if (!selectedTransaction) {
    return (
      <MainLayout>
        <Breadcrumb
          items={[
            { label: 'Dashboard', href: '/dashboard' },
            { label: 'Transactions', href: '/transactions' },
            { label: 'Transaction Details' },
          ]}
        />
        <div className="mt-8">
          <p className="text-neutral-600 mb-4">Transaction not found</p>
          <Link to="/transactions">
            <Button>Back to Transactions</Button>
          </Link>
        </div>
      </MainLayout>
    );
  }

  const amountColor =
    selectedTransaction.type === 'income' ? 'text-success-600' : 'text-error-600';

  return (
    <MainLayout>
      {/* Breadcrumb */}
      <Breadcrumb
        items={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Transactions', href: '/transactions' },
          { label: selectedTransaction.title },
        ]}
      />

      {/* Page Header */}
      <div className="mt-8 mb-8 flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-neutral-900">{selectedTransaction.title}</h1>
          <p className="text-neutral-600 mt-2">{selectedTransaction.description}</p>
        </div>
        <div className="flex gap-2">
          <Link to={`/transactions/${selectedTransaction.id}/edit`}>
            <Button variant="secondary">Edit</Button>
          </Link>
          <Link to="/transactions">
            <Button variant="secondary">Back</Button>
          </Link>
        </div>
      </div>

      {/* Amount Card */}
      <Card className="mb-8 bg-gradient-to-br from-neutral-50 to-neutral-100">
        <div className="text-center py-8">
          <p className="text-neutral-600 text-sm font-medium mb-2">Transaction Amount</p>
          <p className={`text-5xl font-bold ${amountColor}`}>
            {selectedTransaction.type === 'income' ? '+' : '-'}
            {formatCurrency(selectedTransaction.amount)}
          </p>
          <p className="text-neutral-500 text-sm mt-4">
            {selectedTransaction.type === 'income' ? 'Income' : 'Expense'}
          </p>
        </div>
      </Card>

      {/* Transaction Details */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
        {/* Basic Details */}
        <Card>
          <div>
            <h2 className="text-lg font-bold text-neutral-900 mb-6">Basic Information</h2>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-neutral-500">Date</p>
                <p className="text-neutral-900 font-medium">{formatDate(selectedTransaction.date)}</p>
              </div>
              <div>
                <p className="text-sm text-neutral-500">Type</p>
                <p className="text-neutral-900 font-medium">
                  {selectedTransaction.type === 'income' ? 'Income' : 'Expense'}
                </p>
              </div>
              <div>
                <p className="text-sm text-neutral-500">Category</p>
                <p className="text-neutral-900 font-medium">
                  {selectedTransaction.category?.name || 'Uncategorized'}
                </p>
              </div>
            </div>
          </div>
        </Card>

        {/* Additional Details */}
        <Card>
          <div>
            <h2 className="text-lg font-bold text-neutral-900 mb-6">Additional Information</h2>
            <div className="space-y-4">
              {selectedTransaction.payment_method && (
                <div>
                  <p className="text-sm text-neutral-500">Payment Method</p>
                  <p className="text-neutral-900 font-medium">
                    {selectedTransaction.payment_method.replace('_', ' ').toUpperCase()}
                  </p>
                </div>
              )}

              {selectedTransaction.reference_number && (
                <div>
                  <p className="text-sm text-neutral-500">Reference Number</p>
                  <p className="text-neutral-900 font-medium">{selectedTransaction.reference_number}</p>
                </div>
              )}

              {selectedTransaction.is_recurring && (
                <div>
                  <p className="text-sm text-neutral-500">Recurring</p>
                  <p className="text-neutral-900 font-medium">
                    {selectedTransaction.recurring_frequency?.replace('_', ' ').toUpperCase() || 'Yes'}
                  </p>
                </div>
              )}
            </div>
          </div>
        </Card>
      </div>

      {/* Tags */}
      {selectedTransaction.tags && selectedTransaction.tags.length > 0 && (
        <Card>
          <div>
            <h2 className="text-lg font-bold text-neutral-900 mb-4">Tags</h2>
            <div className="flex flex-wrap gap-2">
              {selectedTransaction.tags.map((tag) => (
                <span
                  key={tag}
                  className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm font-medium"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        </Card>
      )}
    </MainLayout>
  );
}
