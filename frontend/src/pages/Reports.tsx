import { useEffect, useState } from 'react';
import { useTransactionStore } from '@/store/transactionStore';
import { MainLayout, Card, Breadcrumb, Button, Spinner, Alert } from '@/components';
import { LineChart, PieChart } from '@/components';
import { formatCurrency, formatDate } from '@/utils/formatters';

export function Reports() {
  const { reportData, fetchReport, isLoading, error } = useTransactionStore();
  const [dateRange, setDateRange] = useState<'7d' | '30d' | '90d' | 'custom'>('30d');
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');

  // Set initial date range
  useEffect(() => {
    const today = new Date();
    const end = today.toISOString().split('T')[0];

    let start: string;
    switch (dateRange) {
      case '7d':
        start = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
        break;
      case '30d':
        start = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
        break;
      case '90d':
        start = new Date(today.getTime() - 90 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
        break;
      case 'custom':
        if (!startDate || !endDate) return;
        fetchReport(startDate, endDate);
        return;
      default:
        start = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    }

    setStartDate(start);
    setEndDate(end);
    fetchReport(start, end);
  }, [dateRange]);

  const handleCustomDateChange = () => {
    if (startDate && endDate) {
      fetchReport(startDate, endDate);
    }
  };

  // Prepare chart data from monthly trends
  const monthlyChartData = reportData?.monthly_trends.map((trend) => ({
    name: new Date(trend.month + '-01').toLocaleString('default', { month: 'short', year: 'numeric' }),
    income: trend.income,
    expenses: trend.expenses,
    net: trend.net,
  })) || [];

  // Prepare pie chart data from category breakdown
  const categoryChartData = reportData?.by_category.map((cat) => ({
    name: cat.category_name,
    value: cat.amount,
  })) || [];

  if (isLoading && !reportData) {
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
          { label: 'Reports' },
        ]}
      />

      {/* Page Header */}
      <div className="mt-8 mb-8">
        <h1 className="text-3xl font-bold text-neutral-900">Reports</h1>
        <p className="text-neutral-600 mt-2">Generate and view detailed financial reports</p>
      </div>

      {/* Date Range Selector */}
      <Card className="mb-8">
        <div>
          <h3 className="text-lg font-bold text-neutral-900 mb-4">Select Report Period</h3>

          {/* Preset Range Buttons */}
          <div className="flex gap-2 mb-6">
            {(['7d', '30d', '90d'] as const).map((range) => (
              <button
                key={range}
                onClick={() => setDateRange(range)}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  dateRange === range
                    ? 'bg-primary-600 text-white'
                    : 'bg-neutral-100 text-neutral-700 hover:bg-neutral-200'
                }`}
              >
                {range === '7d' ? 'Last 7 Days' : range === '30d' ? 'Last 30 Days' : 'Last 90 Days'}
              </button>
            ))}
            <button
              onClick={() => setDateRange('custom')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                dateRange === 'custom'
                  ? 'bg-primary-600 text-white'
                  : 'bg-neutral-100 text-neutral-700 hover:bg-neutral-200'
              }`}
            >
              Custom Range
            </button>
          </div>

          {/* Custom Date Range */}
          {dateRange === 'custom' && (
            <div className="flex gap-4 mb-4">
              <div className="flex-1">
                <label className="block text-sm font-medium text-neutral-700 mb-2">
                  Start Date
                </label>
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <div className="flex-1">
                <label className="block text-sm font-medium text-neutral-700 mb-2">
                  End Date
                </label>
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <div className="flex items-end">
                <Button onClick={handleCustomDateChange}>Generate Report</Button>
              </div>
            </div>
          )}

          {reportData && (
            <div className="text-sm text-neutral-600">
              Report Period: {formatDate(reportData.period.start_date)} to {formatDate(reportData.period.end_date)}
            </div>
          )}
        </div>
      </Card>

      {error && (
        <Alert variant="error" closeable className="mb-8">
          {error}
        </Alert>
      )}

      {reportData && (
        <>
          {/* Summary Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <Card>
              <div>
                <p className="text-neutral-600 text-sm font-medium">Total Income</p>
                <p className="text-2xl font-bold text-success-600 mt-2">
                  {formatCurrency(reportData.summary.total_income)}
                </p>
              </div>
            </Card>

            <Card>
              <div>
                <p className="text-neutral-600 text-sm font-medium">Total Expenses</p>
                <p className="text-2xl font-bold text-error-600 mt-2">
                  {formatCurrency(reportData.summary.total_expenses)}
                </p>
              </div>
            </Card>

            <Card>
              <div>
                <p className="text-neutral-600 text-sm font-medium">Net Balance</p>
                <p
                  className={`text-2xl font-bold mt-2 ${
                    reportData.summary.net_balance >= 0 ? 'text-primary-600' : 'text-error-600'
                  }`}
                >
                  {formatCurrency(reportData.summary.net_balance)}
                </p>
              </div>
            </Card>

            <Card>
              <div>
                <p className="text-neutral-600 text-sm font-medium">Transactions</p>
                <p className="text-2xl font-bold text-primary-600 mt-2">
                  {reportData.summary.transaction_count}
                </p>
              </div>
            </Card>
          </div>

          {/* Charts Section */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            {/* Monthly Trends */}
            <Card className="lg:col-span-2">
              <div>
                <h2 className="text-lg font-bold text-neutral-900 mb-6">Monthly Trends</h2>
                <LineChart
                  data={monthlyChartData}
                  lines={[
                    { key: 'income', color: '#10b981', name: 'Income' },
                    { key: 'expenses', color: '#ef4444', name: 'Expenses' },
                    { key: 'net', color: '#3b82f6', name: 'Net' },
                  ]}
                  height={300}
                />
              </div>
            </Card>

            {/* Category Breakdown */}
            <Card>
              <div>
                <h2 className="text-lg font-bold text-neutral-900 mb-6">Spending by Category</h2>
                <PieChart data={categoryChartData} height={300} showLegend={true} />
              </div>
            </Card>
          </div>

          {/* Top Categories */}
          <Card className="mb-8">
            <div>
              <h2 className="text-lg font-bold text-neutral-900 mb-6">Top Spending Categories</h2>
              <div className="space-y-4">
                {reportData.top_categories.map((category) => (
                  <div key={category.category_id} className="flex items-center justify-between pb-4 border-b border-neutral-200 last:border-b-0">
                    <div>
                      <p className="font-medium text-neutral-900">{category.category_name}</p>
                      <p className="text-sm text-neutral-500">{category.transaction_count} transactions</p>
                    </div>
                    <p className="text-lg font-bold text-primary-600">
                      {formatCurrency(category.total_amount)}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </Card>

          {/* Recurring Transactions Summary */}
          <Card>
            <div>
              <h2 className="text-lg font-bold text-neutral-900 mb-6">Recurring Transactions</h2>
              {reportData.recurring_summary.length > 0 ? (
                <div className="space-y-4">
                  {reportData.recurring_summary.map((recurring) => (
                    <div key={recurring.transaction_id} className="flex items-center justify-between pb-4 border-b border-neutral-200 last:border-b-0">
                      <div>
                        <p className="font-medium text-neutral-900">{recurring.title}</p>
                        <p className="text-sm text-neutral-500">
                          {recurring.frequency} • {recurring.category_name}
                        </p>
                      </div>
                      <p className="text-lg font-bold text-primary-600">
                        {formatCurrency(recurring.amount)}
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-neutral-600">No recurring transactions found</p>
              )}
            </div>
          </Card>
        </>
      )}
    </MainLayout>
  );
}
