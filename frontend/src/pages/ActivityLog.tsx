import { useState, useEffect } from 'react';
import { MainLayout, Card, Breadcrumb, ActivityLog as ActivityLogComponent, Input, Select, Spinner } from '@/components';
import { ActivityLogEntry } from '@/components/ActivityLog';

export function ActivityLog() {
  const [entries, setEntries] = useState<ActivityLogEntry[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [filterAction, setFilterAction] = useState<string>('all');
  const [filterEntity, setFilterEntity] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');

  // Mock data for demonstration
  const mockEntries: ActivityLogEntry[] = [
    {
      id: 1,
      action: 'CREATE',
      description: 'Created a new transaction',
      entity_type: 'Transaction',
      entity_id: 123,
      user: {
        id: 1,
        first_name: 'John',
        last_name: 'Doe',
        email: 'john@example.com',
      },
      timestamp: new Date(Date.now() - 5 * 60000).toISOString(),
      ip_address: '192.168.1.1',
      status: 'success',
      details: {
        amount: 50.00,
        category: 'Food',
      },
    },
    {
      id: 2,
      action: 'UPDATE',
      description: 'Updated transaction amount',
      entity_type: 'Transaction',
      entity_id: 122,
      user: {
        id: 1,
        first_name: 'John',
        last_name: 'Doe',
        email: 'john@example.com',
      },
      timestamp: new Date(Date.now() - 30 * 60000).toISOString(),
      ip_address: '192.168.1.1',
      status: 'success',
      details: {
        old_amount: 45.00,
        new_amount: 50.00,
      },
    },
    {
      id: 3,
      action: 'DELETE',
      description: 'Deleted transaction',
      entity_type: 'Transaction',
      entity_id: 121,
      user: {
        id: 2,
        first_name: 'Jane',
        last_name: 'Smith',
        email: 'jane@example.com',
      },
      timestamp: new Date(Date.now() - 2 * 3600000).toISOString(),
      ip_address: '192.168.1.2',
      status: 'success',
    },
    {
      id: 4,
      action: 'EXPORT',
      description: 'Exported transactions to CSV',
      entity_type: 'Export',
      user: {
        id: 1,
        first_name: 'John',
        last_name: 'Doe',
        email: 'john@example.com',
      },
      timestamp: new Date(Date.now() - 6 * 3600000).toISOString(),
      ip_address: '192.168.1.1',
      status: 'success',
      details: {
        format: 'CSV',
        rows: 42,
      },
    },
    {
      id: 5,
      action: 'LOGIN',
      description: 'User logged in',
      entity_type: 'Authentication',
      user: {
        id: 1,
        first_name: 'John',
        last_name: 'Doe',
        email: 'john@example.com',
      },
      timestamp: new Date(Date.now() - 24 * 3600000).toISOString(),
      ip_address: '192.168.1.1',
      status: 'success',
    },
  ];

  useEffect(() => {
    // Simulate loading activity logs
    setIsLoading(true);

    // In a real app, you would fetch from an API endpoint
    // const fetchActivityLogs = async () => {
    //   try {
    //     const response = await activityService.getAuditLogs({
    //       page: currentPage,
    //       limit: 20,
    //       action: filterAction === 'all' ? undefined : filterAction,
    //       entity_type: filterEntity === 'all' ? undefined : filterEntity,
    //       search: searchQuery || undefined,
    //     });
    //     setEntries(response.data);
    //     setTotalPages(response.totalPages);
    //   } catch (error) {
    //     console.error('Failed to fetch activity logs:', error);
    //   }
    // };

    const timer = setTimeout(() => {
      const filtered = mockEntries.filter((entry) => {
        const matchesAction = filterAction === 'all' || entry.action === filterAction;
        const matchesEntity = filterEntity === 'all' || entry.entity_type === filterEntity;
        const matchesSearch = !searchQuery ||
          entry.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
          entry.user.first_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          entry.user.last_name.toLowerCase().includes(searchQuery.toLowerCase());

        return matchesAction && matchesEntity && matchesSearch;
      });

      setEntries(filtered);
      setTotalPages(1);
      setIsLoading(false);
    }, 300);

    return () => clearTimeout(timer);
  }, [currentPage, filterAction, filterEntity, searchQuery]);

  const uniqueActions = ['all', ...new Set(mockEntries.map((e) => e.action))];
  const uniqueEntities = ['all', ...new Set(mockEntries.map((e) => e.entity_type))];

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Breadcrumb */}
        <Breadcrumb
          items={[
            { label: 'Dashboard', href: '/dashboard' },
            { label: 'Activity Log', href: '/activity-log' },
          ]}
        />

        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-neutral-900 dark:text-white">
            Activity Audit Log
          </h1>
          <p className="text-neutral-600 dark:text-neutral-400 mt-2">
            Track all actions and changes in your account
          </p>
        </div>

        {/* Filters Card */}
        <Card>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Input
              placeholder="Search by user or action..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setCurrentPage(1);
              }}
            />
            <Select
              label="Action"
              value={filterAction}
              onChange={(e) => {
                setFilterAction(e.target.value);
                setCurrentPage(1);
              }}
              options={uniqueActions.map((action) => ({
                value: action,
                label: action === 'all' ? 'All Actions' : action.replace(/_/g, ' '),
              }))}
            />
            <Select
              label="Entity Type"
              value={filterEntity}
              onChange={(e) => {
                setFilterEntity(e.target.value);
                setCurrentPage(1);
              }}
              options={uniqueEntities.map((entity) => ({
                value: entity,
                label: entity === 'all' ? 'All Types' : entity,
              }))}
            />
            <div className="pt-6">
              <button
                onClick={() => {
                  setFilterAction('all');
                  setFilterEntity('all');
                  setSearchQuery('');
                  setCurrentPage(1);
                }}
                className="w-full px-4 py-2 border border-neutral-300 dark:border-neutral-600 rounded-lg text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors"
              >
                Clear Filters
              </button>
            </div>
          </div>
        </Card>

        {/* Activity Log Table */}
        <Card>
          {isLoading ? (
            <div className="flex justify-center py-12">
              <Spinner />
            </div>
          ) : (
            <ActivityLogComponent
              entries={entries}
              isLoading={isLoading}
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={setCurrentPage}
            />
          )}
        </Card>

        {/* Info Box */}
        <Card className="bg-primary-50 dark:bg-primary-900/10 border border-primary-200 dark:border-primary-800">
          <div className="flex gap-3">
            <div className="flex-shrink-0 text-primary-600 dark:text-primary-400 mt-1">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 5v8a2 2 0 01-2 2h-5l-5 4v-4H4a2 2 0 01-2-2V5a2 2 0 012-2h12a2 2 0 012 2zm-11-1H7v2h2V4zm2 2H9v2h2V4zm2 0h-2v2h2V4z" clipRule="evenodd" />
              </svg>
            </div>
            <div>
              <h3 className="font-semibold text-primary-900 dark:text-primary-100">
                About Activity Logs
              </h3>
              <p className="text-sm text-primary-800 dark:text-primary-200 mt-1">
                This log shows all actions performed in your account, including user logins, transaction changes, exports, and more. Click on any entry to see detailed information.
              </p>
            </div>
          </div>
        </Card>
      </div>
    </MainLayout>
  );
}
