import { useEffect, useState } from 'react';
import { useTransactionStore } from '@/store/transactionStore';
import { MainLayout, Card, Breadcrumb, Spinner, Alert } from '@/components';
import { LineChart, BarChart } from '@/components';
import { formatCurrency } from '@/utils/formatters';

export function Analytics() {
  const { analyticsData, fetchAnalytics, isLoading, error } = useTransactionStore();
  const [comparisonType, setComparisonType] = useState<'month' | 'quarter' | 'year'>('month');

  useEffect(() => {
    fetchAnalytics();
  }, [fetchAnalytics]);

  if (isLoading && !analyticsData) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center min-h-screen">
          <Spinner size="large" />
        </div>
      </MainLayout>
    );
  }

  const getComparisonLabel = (type: string): string => {
    switch (type) {
      case 'month':
        return 'Month-over-Month';
      case 'quarter':
        return 'Quarter-over-Quarter';
      case 'year':
        return 'Year-over-Year';
      default:
        return '';
    }
  };

  // Prepare comparison chart data
  const comparisonChartData = analyticsData
    ? [
        {
          name: 'Current Period',
          income: analyticsData.comparison.current_period.income,
          expenses: analyticsData.comparison.current_period.expenses,
          net: analyticsData.comparison.current_period.net,
        },
        {
          name: 'Previous Period',
          income: analyticsData.comparison.previous_period.income,
          expenses: analyticsData.comparison.previous_period.expenses,
          net: analyticsData.comparison.previous_period.net,
        },
      ]
    : [];

  // Prepare category trends chart data
  const categoryTrendChartData = analyticsData
    ? analyticsData.category_trends.map((trend) => ({
        name: trend.category_name,
        current: trend.current_month,
        previous: trend.previous_month,
        change: trend.change_percentage,
      }))
    : [];

  return (
    <MainLayout>
      {/* Breadcrumb */}
      <Breadcrumb
        items={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Analytics' },
        ]}
      />

      {/* Page Header */}
      <div className="mt-8 mb-8">
        <h1 className="text-3xl font-bold text-neutral-900">Analytics</h1>
        <p className="text-neutral-600 mt-2">Detailed insights and trends analysis</p>
      </div>

      {error && (
        <Alert variant="error" closeable className="mb-8">
          {error}
        </Alert>
      )}

      {analyticsData && (
        <>
          {/* Period Comparison Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            {/* Current Period */}
            <Card>
              <div>
                <h3 className="text-lg font-bold text-neutral-900 mb-4">Current Period</h3>
                <div className="space-y-3">
                  <div>
                    <p className="text-neutral-600 text-sm">Income</p>
                    <p className="text-2xl font-bold text-success-600">
                      {formatCurrency(analyticsData.comparison.current_period.income)}
                    </p>
                  </div>
                  <div>
                    <p className="text-neutral-600 text-sm">Expenses</p>
                    <p className="text-2xl font-bold text-error-600">
                      {formatCurrency(analyticsData.comparison.current_period.expenses)}
                    </p>
                  </div>
                  <div className="pt-2 border-t border-neutral-200">
                    <p className="text-neutral-600 text-sm">Net Balance</p>
                    <p
                      className={`text-2xl font-bold ${
                        analyticsData.comparison.current_period.net >= 0
                          ? 'text-primary-600'
                          : 'text-error-600'
                      }`}
                    >
                      {formatCurrency(analyticsData.comparison.current_period.net)}
                    </p>
                  </div>
                </div>
              </div>
            </Card>

            {/* Previous Period */}
            <Card>
              <div>
                <h3 className="text-lg font-bold text-neutral-900 mb-4">Previous Period</h3>
                <div className="space-y-3">
                  <div>
                    <p className="text-neutral-600 text-sm">Income</p>
                    <p className="text-2xl font-bold text-success-600">
                      {formatCurrency(analyticsData.comparison.previous_period.income)}
                    </p>
                  </div>
                  <div>
                    <p className="text-neutral-600 text-sm">Expenses</p>
                    <p className="text-2xl font-bold text-error-600">
                      {formatCurrency(analyticsData.comparison.previous_period.expenses)}
                    </p>
                  </div>
                  <div className="pt-2 border-t border-neutral-200">
                    <p className="text-neutral-600 text-sm">Net Balance</p>
                    <p
                      className={`text-2xl font-bold ${
                        analyticsData.comparison.previous_period.net >= 0
                          ? 'text-primary-600'
                          : 'text-error-600'
                      }`}
                    >
                      {formatCurrency(analyticsData.comparison.previous_period.net)}
                    </p>
                  </div>
                </div>
              </div>
            </Card>
          </div>

          {/* Spending Velocity */}
          <Card className="mb-8">
            <div>
              <h3 className="text-lg font-bold text-neutral-900 mb-6">Spending Velocity</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                  <p className="text-neutral-600 text-sm font-medium mb-2">Average Daily Income</p>
                  <p className="text-4xl font-bold text-success-600">
                    {formatCurrency(analyticsData.spending_velocity.average_daily_income)}
                  </p>
                  <p className="text-xs text-neutral-500 mt-2">Per day on average</p>
                </div>
                <div>
                  <p className="text-neutral-600 text-sm font-medium mb-2">Average Daily Spend</p>
                  <p className="text-4xl font-bold text-error-600">
                    {formatCurrency(analyticsData.spending_velocity.average_daily_spend)}
                  </p>
                  <p className="text-xs text-neutral-500 mt-2">Per day on average</p>
                </div>
              </div>
            </div>
          </Card>

          {/* Period Comparison Chart */}
          <Card className="mb-8">
            <div>
              <h3 className="text-lg font-bold text-neutral-900 mb-6">Period Comparison</h3>
              <BarChart
                data={comparisonChartData}
                bars={[
                  { key: 'income', color: '#10b981', name: 'Income' },
                  { key: 'expenses', color: '#ef4444', name: 'Expenses' },
                  { key: 'net', color: '#3b82f6', name: 'Net' },
                ]}
                height={300}
              />
              {/* Hidden Data Table for Screen Readers */}
              <table className="sr-only">
                <caption>Period Comparison Chart Data</caption>
                <thead>
                  <tr>
                    <th scope="col">Period</th>
                    <th scope="col">Income</th>
                    <th scope="col">Expenses</th>
                    <th scope="col">Net</th>
                  </tr>
                </thead>
                <tbody>
                  {comparisonChartData.map((item) => (
                    <tr key={item.name}>
                      <td>{item.name}</td>
                      <td>{formatCurrency(item.income)}</td>
                      <td>{formatCurrency(item.expenses)}</td>
                      <td>{formatCurrency(item.net)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>

          {/* Change Indicators */}
          <Card className="mb-8">
            <div>
              <h3 className="text-lg font-bold text-neutral-900 mb-6">Period Changes</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-neutral-50 rounded-lg">
                  <p className="text-neutral-600 text-sm font-medium mb-2">Income Change</p>
                  <div className="flex items-baseline gap-2">
                    <p
                      className={`text-2xl font-bold ${
                        analyticsData.comparison.change_percentage.income >= 0
                          ? 'text-success-600'
                          : 'text-error-600'
                      }`}
                    >
                      {analyticsData.comparison.change_percentage.income > 0 ? '+' : ''}
                      {analyticsData.comparison.change_percentage.income.toFixed(1)}%
                    </p>
                    <span
                      className={`text-lg ${
                        analyticsData.comparison.change_percentage.income >= 0 ? 'text-success-600' : 'text-error-600'
                      }`}
                      aria-hidden="true"
                    >
                      {analyticsData.comparison.change_percentage.income >= 0 ? '↑' : '↓'}
                    </span>
                    <span className="sr-only">
                      {analyticsData.comparison.change_percentage.income >= 0 ? 'increase' : 'decrease'}
                    </span>
                  </div>
                </div>

                <div className="p-4 bg-neutral-50 rounded-lg">
                  <p className="text-neutral-600 text-sm font-medium mb-2">Expense Change</p>
                  <div className="flex items-baseline gap-2">
                    <p
                      className={`text-2xl font-bold ${
                        analyticsData.comparison.change_percentage.expenses <= 0
                          ? 'text-success-600'
                          : 'text-error-600'
                      }`}
                    >
                      {analyticsData.comparison.change_percentage.expenses > 0 ? '+' : ''}
                      {analyticsData.comparison.change_percentage.expenses.toFixed(1)}%
                    </p>
                    <span
                      className={`text-lg ${
                        analyticsData.comparison.change_percentage.expenses <= 0 ? 'text-success-600' : 'text-error-600'
                      }`}
                      aria-hidden="true"
                    >
                      {analyticsData.comparison.change_percentage.expenses >= 0 ? '↑' : '↓'}
                    </span>
                    <span className="sr-only">
                      {analyticsData.comparison.change_percentage.expenses >= 0 ? 'increase' : 'decrease'}
                    </span>
                  </div>
                </div>

                <div className="p-4 bg-neutral-50 rounded-lg">
                  <p className="text-neutral-600 text-sm font-medium mb-2">Net Change</p>
                  <div className="flex items-baseline gap-2">
                    <p
                      className={`text-2xl font-bold ${
                        analyticsData.comparison.change_percentage.net >= 0 ? 'text-success-600' : 'text-error-600'
                      }`}
                    >
                      {analyticsData.comparison.change_percentage.net > 0 ? '+' : ''}
                      {analyticsData.comparison.change_percentage.net.toFixed(1)}%
                    </p>
                    <span
                      className={`text-lg ${
                        analyticsData.comparison.change_percentage.net >= 0 ? 'text-success-600' : 'text-error-600'
                      }`}
                      aria-hidden="true"
                    >
                      {analyticsData.comparison.change_percentage.net >= 0 ? '↑' : '↓'}
                    </span>
                    <span className="sr-only">
                      {analyticsData.comparison.change_percentage.net >= 0 ? 'increase' : 'decrease'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </Card>

          {/* Category Trends */}
          <Card>
            <div>
              <h3 className="text-lg font-bold text-neutral-900 mb-6">Category Trends</h3>
              {analyticsData.category_trends.length > 0 ? (
                <div className="space-y-4">
                  {analyticsData.category_trends.map((trend) => (
                    <div key={trend.category_name} className="flex items-center justify-between pb-4 border-b border-neutral-200 last:border-b-0">
                      <div>
                        <p className="font-medium text-neutral-900">{trend.category_name}</p>
                        <p className="text-sm text-neutral-500">
                          Current: {formatCurrency(trend.current_month)} | Previous:{' '}
                          {formatCurrency(trend.previous_month)}
                        </p>
                      </div>
                      <div
                        className={`text-lg font-bold ${
                          trend.change_percentage >= 0 ? 'text-error-600' : 'text-success-600'
                        }`}
                      >
                        {trend.change_percentage > 0 ? '+' : ''}
                        {trend.change_percentage.toFixed(1)}%
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-neutral-600">No category trends available</p>
              )}
            </div>
          </Card>
        </>
      )}
    </MainLayout>
  );
}
