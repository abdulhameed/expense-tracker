import { useEffect, useState } from 'react';
import { notificationService, Notification } from '@/utils/notifications';
import { Toast } from './Toast';

export function ToastContainer() {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  useEffect(() => {
    // Subscribe to notification changes
    const unsubscribe = notificationService.subscribe((updatedNotifications) => {
      setNotifications(updatedNotifications);
    });

    return unsubscribe;
  }, []);

  const handleClose = (id: string) => {
    notificationService.remove(id);
  };

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-3 pointer-events-none">
      {notifications.map((notification) => (
        <div key={notification.id} className="pointer-events-auto">
          <Toast notification={notification} onClose={handleClose} />
        </div>
      ))}
    </div>
  );
}
