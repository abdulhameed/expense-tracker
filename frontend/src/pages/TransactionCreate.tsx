import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTransactionStore } from '@/store/transactionStore';
import { TransactionModal } from '@/components/TransactionModal';
import { MainLayout, Breadcrumb } from '@/components';

export function TransactionCreate() {
  const navigate = useNavigate();
  const { categories, fetchCategories, createTransaction, isLoading, error } = useTransactionStore();

  // Load categories on mount
  useEffect(() => {
    if (categories.length === 0) {
      fetchCategories();
    }
  }, []);

  const handleSubmit = async (data: any) => {
    try {
      await createTransaction(data);
      navigate('/transactions');
    } catch (err) {
      // Error is handled by the store and passed via error prop
      console.error('Failed to create transaction:', err);
    }
  };

  const handleClose = () => {
    navigate('/transactions');
  };

  return (
    <MainLayout>
      {/* Breadcrumb */}
      <Breadcrumb
        items={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Transactions', href: '/transactions' },
          { label: 'Create Transaction' },
        ]}
      />

      {/* Page Header */}
      <div className="mt-8 mb-8">
        <h1 className="text-3xl font-bold text-neutral-900">Create New Transaction</h1>
        <p className="text-neutral-600 mt-2">Add a new income or expense to your account</p>
      </div>

      {/* Modal - shown directly on page */}
      <div className="max-w-2xl mx-auto">
        <TransactionModal
          isOpen={true}
          onClose={handleClose}
          onSubmit={handleSubmit}
          categories={categories}
          isLoading={isLoading}
          error={error || undefined}
        />
      </div>
    </MainLayout>
  );
}
