import { useState, useEffect } from 'react';
import { MainLayout, Card, Breadcrumb, Button } from '@/components';
import { notificationService, Notification, NotificationType } from '@/utils/notifications';

const notificationTypeColors: Record<NotificationType, { bg: string; text: string; badge: string }> = {
  success: {
    bg: 'bg-success-50',
    text: 'text-success-700',
    badge: 'bg-success-100 text-success-700',
  },
  error: {
    bg: 'bg-error-50',
    text: 'text-error-700',
    badge: 'bg-error-100 text-error-700',
  },
  warning: {
    bg: 'bg-warning-50',
    text: 'text-warning-700',
    badge: 'bg-warning-100 text-warning-700',
  },
  info: {
    bg: 'bg-primary-50',
    text: 'text-primary-700',
    badge: 'bg-primary-100 text-primary-700',
  },
};

export function NotificationCenter() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [filter, setFilter] = useState<NotificationType | 'all'>('all');

  useEffect(() => {
    // Load initial notifications
    setNotifications(notificationService.getAll());

    // Subscribe to notification changes
    const unsubscribe = notificationService.subscribe((updatedNotifications) => {
      setNotifications(updatedNotifications);
    });

    return unsubscribe;
  }, []);

  const filteredNotifications =
    filter === 'all'
      ? notifications
      : notifications.filter((n) => n.type === filter);

  const getTypeIcon = (type: NotificationType) => {
    switch (type) {
      case 'success':
        return '✓';
      case 'error':
        return '✕';
      case 'warning':
        return '⚠';
      case 'info':
        return 'ℹ';
    }
  };

  const formatTime = (timestamp: number) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - timestamp;

    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    if (diff < 604800000) return `${Math.floor(diff / 86400000)}d ago`;

    return date.toLocaleDateString();
  };

  const handleClearAll = () => {
    notificationService.clear();
  };

  const handleRemove = (id: string) => {
    notificationService.remove(id);
  };

  return (
    <MainLayout>
      {/* Breadcrumb */}
      <Breadcrumb
        items={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Notifications' },
        ]}
      />

      {/* Page Header */}
      <div className="mt-8 mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-neutral-900">Notifications</h1>
          <p className="text-neutral-600 mt-2">
            {filteredNotifications.length > 0
              ? `You have ${filteredNotifications.length} notification${filteredNotifications.length === 1 ? '' : 's'}`
              : 'No notifications'}
          </p>
        </div>
        {notifications.length > 0 && (
          <Button
            onClick={handleClearAll}
            className="px-4 py-2 text-neutral-700 bg-neutral-100 hover:bg-neutral-200 rounded-lg text-sm"
          >
            Clear All
          </Button>
        )}
      </div>

      {/* Filter Tabs */}
      {notifications.length > 0 && (
        <div className="mb-6 flex gap-2 border-b border-neutral-200">
          {['all', 'success', 'error', 'warning', 'info'].map((type) => (
            <button
              key={type}
              onClick={() => setFilter(type as NotificationType | 'all')}
              className={`px-4 py-3 font-medium text-sm transition-colors border-b-2 ${
                filter === type
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-neutral-600 hover:text-neutral-900'
              }`}
            >
              {type.charAt(0).toUpperCase() + type.slice(1)}
            </button>
          ))}
        </div>
      )}

      {/* Notifications List */}
      {filteredNotifications.length > 0 ? (
        <div className="space-y-3">
          {filteredNotifications.map((notification) => {
            const colors = notificationTypeColors[notification.type];
            return (
              <Card
                key={notification.id}
                className={`${colors.bg} border-l-4`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4 flex-1">
                    <div className={`${colors.text} text-xl font-bold pt-0.5`}>
                      {getTypeIcon(notification.type)}
                    </div>
                    <div className="flex-1 min-w-0">
                      {notification.title && (
                        <h3 className={`${colors.text} font-semibold text-sm mb-1`}>
                          {notification.title}
                        </h3>
                      )}
                      <p className={`${colors.text} text-sm opacity-90 break-words`}>
                        {notification.message}
                      </p>
                      <p className="text-xs text-neutral-500 mt-2">
                        {formatTime(notification.timestamp)}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => handleRemove(notification.id)}
                    className={`flex-shrink-0 ml-4 px-3 py-1 rounded text-sm font-medium ${colors.badge} hover:opacity-80 transition-opacity`}
                  >
                    Dismiss
                  </button>
                </div>
              </Card>
            );
          })}
        </div>
      ) : (
        <Card className="text-center py-12">
          <div className="text-5xl mb-4">🔔</div>
          <h2 className="text-xl font-semibold text-neutral-900 mb-2">
            No notifications
          </h2>
          <p className="text-neutral-600">
            {filter !== 'all'
              ? `You don't have any ${filter} notifications`
              : 'Check back later for updates'}
          </p>
        </Card>
      )}
    </MainLayout>
  );
}
