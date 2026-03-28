import { useEffect, useState } from 'react';
import { useAuthStore } from '@/store/authStore';
import { useTransactionStore } from '@/store/transactionStore';
import { MainLayout, Card, Breadcrumb, LineChart, PieChart, Spinner } from '@/components';
import { formatCurrency, formatDate } from '@/utils/formatters';

export function Dashboard() {
  const { user, getCurrentUser } = useAuthStore();
  const { stats, fetchStats, fetchTransactions, transactions, isLoading, error } =
    useTransactionStore();
  const [dateRange, setDateRange] = useState<'7d' | '30d' | '90d' | 'all'>('30d');

  useEffect(() => {
    if (!user) {
      getCurrentUser();
    }
  }, [user, getCurrentUser]);

  useEffect(() => {
    const now = new Date();
    let startDate: string | undefined;

    switch (dateRange) {
      case '7d':
        startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
        break;
      case '30d':
        startDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
          .toISOString()
          .split('T')[0];
        break;
      case '90d':
        startDate = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000)
          .toISOString()
          .split('T')[0];
        break;
    }

    fetchStats(startDate);
    fetchTransactions({ limit: 5 });
  }, [dateRange, fetchStats, fetchTransactions]);

  const chartData = [
    { name: 'Mon', income: 1200, expenses: 900, net: 300 },
    { name: 'Tue', income: 1500, expenses: 1000, net: 500 },
    { name: 'Wed', income: 1100, expenses: 800, net: 300 },
    { name: 'Thu', income: 1600, expenses: 1200, net: 400 },
    { name: 'Fri', income: 1400, expenses: 1100, net: 300 },
    { name: 'Sat', income: 900, expenses: 600, net: 300 },
    { name: 'Sun', income: 1800, expenses: 1400, net: 400 },
  ];

  const categoryData = [
    { name: 'Groceries', value: 450 },
    { name: 'Transport', value: 250 },
    { name: 'Entertainment', value: 180 },
    { name: 'Utilities', value: 320 },
    { name: 'Other', value: 200 },
  ];

  if (isLoading && !stats) {
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
      <Breadcrumb items={[{ label: 'Dashboard' }]} />

      {/* Page Header */}
      <div className="mt-8 mb-8 flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-neutral-900">
            Welcome, {user?.first_name || 'Guest'}
          </h1>
          <p className="text-neutral-600 mt-2">Here's your financial overview</p>
        </div>

        {/* Date Range Selector */}
        <div className="flex gap-2">
          {(['7d', '30d', '90d', 'all'] as const).map((range) => (
            <button
              key={range}
              onClick={() => setDateRange(range)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                dateRange === range
                  ? 'bg-primary-600 text-white'
                  : 'bg-neutral-100 text-neutral-700 hover:bg-neutral-200'
              }`}
            >
              {range === '7d' ? '7 Days' : range === '30d' ? '30 Days' : range === '90d' ? '90 Days' : 'All Time'}
            </button>
          ))}
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card>
          <div>
            <p className="text-neutral-600 text-sm font-medium">Total Income</p>
            <p className="text-3xl font-bold text-success-600 mt-3">
              {stats ? formatCurrency(stats.total_income) : '$0.00'}
            </p>
            <p className="text-xs text-neutral-500 mt-2">This period</p>
          </div>
        </Card>

        <Card>
          <div>
            <p className="text-neutral-600 text-sm font-medium">Total Expenses</p>
            <p className="text-3xl font-bold text-error-600 mt-3">
              {stats ? formatCurrency(stats.total_expenses) : '$0.00'}
            </p>
            <p className="text-xs text-neutral-500 mt-2">This period</p>
          </div>
        </Card>

        <Card>
          <div>
            <p className="text-neutral-600 text-sm font-medium">Net Balance</p>
            <p
              className={`text-3xl font-bold mt-3 ${
                stats && stats.net_balance >= 0 ? 'text-primary-600' : 'text-error-600'
              }`}
            >
              {stats ? formatCurrency(stats.net_balance) : '$0.00'}
            </p>
            <p className="text-xs text-neutral-500 mt-2">Income - Expenses</p>
          </div>
        </Card>

        <Card>
          <div>
            <p className="text-neutral-600 text-sm font-medium">Transactions</p>
            <p className="text-3xl font-bold text-primary-600 mt-3">
              {stats?.transactions_count || 0}
            </p>
            <p className="text-xs text-neutral-500 mt-2">Total count</p>
          </div>
        </Card>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Line Chart - Income vs Expenses */}
        <Card className="lg:col-span-2">
          <div>
            <h2 className="text-lg font-bold text-neutral-900 mb-6">Income vs Expenses</h2>
            <LineChart
              data={chartData}
              lines={[
                { key: 'income', color: '#10b981', name: 'Income' },
                { key: 'expenses', color: '#ef4444', name: 'Expenses' },
                { key: 'net', color: '#3b82f6', name: 'Net' },
              ]}
              height={300}
            />
          </div>
        </Card>

        {/* Pie Chart - Spending by Category */}
        <Card>
          <div>
            <h2 className="text-lg font-bold text-neutral-900 mb-6">Spending by Category</h2>
            <PieChart data={categoryData} height={300} showLegend={true} />
          </div>
        </Card>
      </div>

      {/* Recent Transactions */}
      <Card>
        <div>
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-lg font-bold text-neutral-900">Recent Transactions</h2>
            <a href="/transactions" className="text-primary-600 hover:text-primary-700 text-sm font-medium">
              View All →
            </a>
          </div>

          {transactions.length === 0 ? (
            <p className="text-neutral-600 py-8 text-center">
              No transactions yet. Start tracking your expenses!
            </p>
          ) : (
            <div className="space-y-3">
              {transactions.slice(0, 5).map((transaction) => (
                <div
                  key={transaction.id}
                  className="flex items-center justify-between p-4 bg-neutral-50 rounded-lg hover:bg-neutral-100 transition-colors"
                >
                  <div className="flex-1">
                    <p className="font-medium text-neutral-900">{transaction.title}</p>
                    <p className="text-sm text-neutral-500">
                      {formatDate(transaction.date)} • {transaction.category?.name}
                    </p>
                  </div>
                  <p
                    className={`text-lg font-bold ${
                      transaction.type === 'income'
                        ? 'text-success-600'
                        : 'text-error-600'
                    }`}
                  >
                    {transaction.type === 'income' ? '+' : '-'}
                    {formatCurrency(transaction.amount)}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      </Card>

      {error && (
        <div className="mt-8 p-4 bg-error-50 border border-error-200 rounded-lg">
          <p className="text-error-800">{error}</p>
        </div>
      )}
    </MainLayout>
  );
}
