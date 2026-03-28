import { useEffect } from 'react';
import { useAuthStore } from '@/store/authStore';
import { MainLayout, Card, Breadcrumb } from '@/components';

export function Dashboard() {
  const { user, getCurrentUser } = useAuthStore();

  useEffect(() => {
    if (!user) {
      getCurrentUser();
    }
  }, [user, getCurrentUser]);

  return (
    <MainLayout>
      {/* Breadcrumb */}
      <Breadcrumb items={[{ label: 'Dashboard' }]} />

      {/* Page Title */}
      <div className="mt-8 mb-8">
        <h1 className="text-3xl font-bold text-neutral-900">
          Welcome, {user?.first_name || 'Guest'}
        </h1>
        <p className="text-neutral-600 mt-2">Here's your financial overview</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card>
          <div>
            <p className="text-neutral-600 text-sm font-medium">Total Expenses</p>
            <p className="text-3xl font-bold text-primary-900 mt-2">$0.00</p>
            <p className="text-xs text-neutral-500 mt-2">Last 30 days</p>
          </div>
        </Card>
        <Card>
          <div>
            <p className="text-neutral-600 text-sm font-medium">This Month</p>
            <p className="text-3xl font-bold text-primary-900 mt-2">$0.00</p>
            <p className="text-xs text-neutral-500 mt-2">Currently</p>
          </div>
        </Card>
        <Card>
          <div>
            <p className="text-neutral-600 text-sm font-medium">Budget Left</p>
            <p className="text-3xl font-bold text-success-600 mt-2">$0.00</p>
            <p className="text-xs text-neutral-500 mt-2">Available</p>
          </div>
        </Card>
      </div>

      {/* Recent Expenses */}
      <Card>
        <div>
          <h2 className="text-xl font-bold text-neutral-900 mb-4">
            Recent Expenses
          </h2>
          <p className="text-neutral-600">
            No expenses yet. Start tracking your expenses!
          </p>
        </div>
      </Card>
    </MainLayout>
  );
}
