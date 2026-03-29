import { useEffect, useState } from 'react';
import { Notification, NotificationType } from '@/utils/notifications';

interface ToastProps {
  notification: Notification;
  onClose: (id: string) => void;
}

const variantStyles: Record<NotificationType, { bg: string; text: string; icon: string }> = {
  success: {
    bg: 'bg-success-600',
    text: 'text-white',
    icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
  },
  warning: {
    bg: 'bg-warning-600',
    text: 'text-white',
    icon: 'M12 8v4m0 4v.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
  },
  error: {
    bg: 'bg-error-600',
    text: 'text-white',
    icon: 'M10 14l-2-2m0 0l-2-2m2 2l2-2m-2 2l-2 2',
  },
  info: {
    bg: 'bg-primary-600',
    text: 'text-white',
    icon: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
  },
};

export function Toast({ notification, onClose }: ToastProps) {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    if (!notification.duration || notification.duration <= 0) return;

    const timer = setTimeout(() => {
      setIsVisible(false);
      onClose(notification.id);
    }, notification.duration);

    return () => clearTimeout(timer);
  }, [notification.duration, notification.id, onClose]);

  const handleClose = () => {
    setIsVisible(false);
    onClose(notification.id);
  };

  if (!isVisible) return null;

  const styles = variantStyles[notification.type];

  return (
    <div
      className={`${styles.bg} ${styles.text} rounded-lg shadow-lg p-4 flex flex-col gap-2 max-w-md animate-in fade-in slide-in-from-right-2 duration-300`}
      role="alert"
    >
      <div className="flex items-start gap-3">
        <svg
          className="w-5 h-5 flex-shrink-0 mt-0.5"
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path fillRule="evenodd" d={styles.icon} clipRule="evenodd" />
        </svg>
        <div className="flex-1">
          {notification.title && (
            <p className="font-semibold text-sm">{notification.title}</p>
          )}
          <p className="text-sm opacity-95">{notification.message}</p>
        </div>
        <button
          onClick={handleClose}
          className="flex-shrink-0 hover:opacity-70 focus:outline-none transition-opacity"
          aria-label="Close notification"
        >
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
              clipRule="evenodd"
            />
          </svg>
        </button>
      </div>
    </div>
  );
}
