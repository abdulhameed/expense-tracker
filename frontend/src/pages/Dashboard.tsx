import { useEffect } from 'react';
import { useAuthStore } from '@/store/authStore';

export function Dashboard() {
  const { user, getCurrentUser } = useAuthStore();

  useEffect(() => {
    if (!user) {
      getCurrentUser();
    }
  }, [user, getCurrentUser]);

  return (
    <div className="min-h-screen bg-neutral-50">
      <nav className="bg-white border-b border-neutral-200">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-primary-900">
              Expense Tracker
            </h1>
            <button className="text-neutral-600 hover:text-neutral-900">
              {user?.first_name} {user?.last_name}
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-neutral-600 text-sm font-medium">
              Total Expenses
            </p>
            <p className="text-3xl font-bold text-primary-900 mt-2">$0.00</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-neutral-600 text-sm font-medium">This Month</p>
            <p className="text-3xl font-bold text-primary-900 mt-2">$0.00</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-neutral-600 text-sm font-medium">Budget Left</p>
            <p className="text-3xl font-bold text-success-600 mt-2">$0.00</p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-neutral-900 mb-4">
            Recent Expenses
          </h2>
          <p className="text-neutral-600">
            No expenses yet. Start tracking your expenses!
          </p>
        </div>
      </main>
    </div>
  );
}
