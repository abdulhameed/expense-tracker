import { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTransactionStore } from '@/store/transactionStore';
import { TransactionModal } from '@/components/TransactionModal';
import { MainLayout, Breadcrumb, Spinner } from '@/components';

export function TransactionEdit() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { selectedTransaction, categories, fetchTransaction, fetchCategories, updateTransaction, isLoading, error } =
    useTransactionStore();

  // Fetch transaction and categories on mount
  useEffect(() => {
    if (id) {
      fetchTransaction(parseInt(id));
    }
    if (categories.length === 0) {
      fetchCategories();
    }
  }, [id, fetchTransaction, fetchCategories, categories.length]);

  const handleSubmit = async (data: any) => {
    if (!id) return;
    try {
      await updateTransaction(parseInt(id), data);
      navigate('/transactions');
    } catch (err) {
      // Error is handled by the store and passed via error prop
      console.error('Failed to update transaction:', err);
    }
  };

  const handleClose = () => {
    navigate('/transactions');
  };

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
            { label: 'Edit Transaction' },
          ]}
        />
        <div className="mt-8">
          <p className="text-neutral-600">Transaction not found</p>
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
          { label: 'Transactions', href: '/transactions' },
          { label: `Edit - ${selectedTransaction.title}` },
        ]}
      />

      {/* Page Header */}
      <div className="mt-8 mb-8">
        <h1 className="text-3xl font-bold text-neutral-900">Edit Transaction</h1>
        <p className="text-neutral-600 mt-2">Update transaction details</p>
      </div>

      {/* Modal - shown directly on page */}
      <div className="max-w-2xl mx-auto">
        <TransactionModal
          isOpen={true}
          onClose={handleClose}
          onSubmit={handleSubmit}
          transaction={selectedTransaction}
          categories={categories}
          isLoading={isLoading}
          error={error || undefined}
        />
      </div>
    </MainLayout>
  );
}
