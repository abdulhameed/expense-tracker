import { useState } from 'react';
import { Spinner, Badge } from '@/components';
import { formatDate, formatRelativeTime } from '@/utils/formatters';

export interface ActivityLogEntry {
  id: number;
  action: string;
  description?: string;
  entity_type: string;
  entity_id?: number;
  user: {
    id: number;
    first_name: string;
    last_name: string;
    email: string;
  };
  timestamp: string;
  ip_address?: string;
  status: 'success' | 'failed' | 'pending';
  details?: Record<string, any>;
}

interface ActivityLogProps {
  entries: ActivityLogEntry[];
  isLoading?: boolean;
  onPageChange?: (page: number) => void;
  totalPages?: number;
  currentPage?: number;
  maxEntries?: number;
}

const actionColors: Record<string, 'primary' | 'success' | 'error' | 'warning'> = {
  CREATE: 'success',
  UPDATE: 'primary',
  DELETE: 'error',
  LOGIN: 'success',
  LOGOUT: 'warning',
  EXPORT: 'primary',
  IMPORT: 'primary',
  DOWNLOAD: 'primary',
};

export function ActivityLog({
  entries,
  isLoading = false,
  onPageChange,
  totalPages = 1,
  currentPage = 1,
  maxEntries = 20,
}: ActivityLogProps) {
  const [expandedId, setExpandedId] = useState<number | null>(null);

  const getActionColor = (action: string) => {
    return actionColors[action] || 'primary';
  };

  const getActionLabel = (action: string) => {
    return action.replace(/_/g, ' ').toUpperCase();
  };

  return (
    <div className="space-y-4">
      <div className="overflow-x-auto border border-neutral-200 dark:border-neutral-700 rounded-lg">
        <table className="w-full">
          <thead className="bg-neutral-50 dark:bg-neutral-800 border-b border-neutral-200 dark:border-neutral-700">
            <tr>
              <th className="px-6 py-3 text-left text-sm font-semibold text-neutral-900 dark:text-white">
                Action
              </th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-neutral-900 dark:text-white">
                Entity
              </th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-neutral-900 dark:text-white">
                User
              </th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-neutral-900 dark:text-white">
                Timestamp
              </th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-neutral-900 dark:text-white">
                Status
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-200 dark:divide-neutral-700">
            {isLoading ? (
              <tr>
                <td colSpan={5} className="px-6 py-8 text-center">
                  <Spinner />
                </td>
              </tr>
            ) : entries.length === 0 ? (
              <tr>
                <td
                  colSpan={5}
                  className="px-6 py-8 text-center text-neutral-500 dark:text-neutral-400"
                >
                  No activity logs found
                </td>
              </tr>
            ) : (
              entries.map((entry) => (
                <tr
                  key={entry.id}
                  className="hover:bg-neutral-50 dark:hover:bg-neutral-800 transition-colors cursor-pointer"
                  onClick={() =>
                    setExpandedId(expandedId === entry.id ? null : entry.id)
                  }
                >
                  <td className="px-6 py-3">
                    <Badge variant={getActionColor(entry.action)}>
                      {getActionLabel(entry.action)}
                    </Badge>
                  </td>
                  <td className="px-6 py-3 text-sm text-neutral-600 dark:text-neutral-400">
                    <span className="font-medium text-neutral-900 dark:text-white">
                      {entry.entity_type}
                    </span>
                    {entry.entity_id && (
                      <span className="ml-2">#{entry.entity_id}</span>
                    )}
                  </td>
                  <td className="px-6 py-3 text-sm text-neutral-600 dark:text-neutral-400">
                    <div className="font-medium text-neutral-900 dark:text-white">
                      {entry.user.first_name} {entry.user.last_name}
                    </div>
                    <div className="text-xs text-neutral-500 dark:text-neutral-500">
                      {entry.user.email}
                    </div>
                  </td>
                  <td className="px-6 py-3 text-sm text-neutral-600 dark:text-neutral-400">
                    <div title={formatDate(entry.timestamp)}>
                      {formatRelativeTime(entry.timestamp)}
                    </div>
                  </td>
                  <td className="px-6 py-3">
                    <Badge
                      variant={
                        entry.status === 'success'
                          ? 'success'
                          : entry.status === 'failed'
                          ? 'error'
                          : 'warning'
                      }
                    >
                      {entry.status.toUpperCase()}
                    </Badge>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Expanded Details */}
      {expandedId !== null && (
        <div className="bg-neutral-50 dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 rounded-lg p-4">
          {(() => {
            const entry = entries.find((e) => e.id === expandedId);
            if (!entry) return null;

            return (
              <div className="space-y-3">
                <h3 className="font-semibold text-neutral-900 dark:text-white">
                  Activity Details
                </h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-neutral-500 dark:text-neutral-400">
                      Description
                    </p>
                    <p className="text-neutral-900 dark:text-white font-medium">
                      {entry.description || 'N/A'}
                    </p>
                  </div>
                  <div>
                    <p className="text-neutral-500 dark:text-neutral-400">
                      IP Address
                    </p>
                    <p className="text-neutral-900 dark:text-white font-medium">
                      {entry.ip_address || 'N/A'}
                    </p>
                  </div>
                  <div>
                    <p className="text-neutral-500 dark:text-neutral-400">
                      Full Timestamp
                    </p>
                    <p className="text-neutral-900 dark:text-white font-medium text-xs">
                      {formatDate(entry.timestamp)}
                    </p>
                  </div>
                  <div>
                    <p className="text-neutral-500 dark:text-neutral-400">
                      Entity ID
                    </p>
                    <p className="text-neutral-900 dark:text-white font-medium">
                      {entry.entity_id || 'N/A'}
                    </p>
                  </div>
                </div>

                {entry.details && Object.keys(entry.details).length > 0 && (
                  <div>
                    <p className="text-neutral-500 dark:text-neutral-400 mb-2">
                      Additional Details
                    </p>
                    <pre className="bg-white dark:bg-neutral-900 p-3 rounded border border-neutral-200 dark:border-neutral-700 text-xs overflow-auto text-neutral-900 dark:text-neutral-100">
                      {JSON.stringify(entry.details, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            );
          })()}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && onPageChange && (
        <div className="flex justify-between items-center pt-4">
          <div className="text-sm text-neutral-600 dark:text-neutral-400">
            Page {currentPage} of {totalPages}
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => onPageChange(currentPage - 1)}
              disabled={currentPage === 1}
              className="px-4 py-2 border border-neutral-300 dark:border-neutral-600 rounded-lg text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Previous
            </button>
            <button
              onClick={() => onPageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
              className="px-4 py-2 border border-neutral-300 dark:border-neutral-600 rounded-lg text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
