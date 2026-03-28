import { ReactNode, useEffect, useState } from 'react';

type ToastVariant = 'success' | 'warning' | 'error' | 'info';

interface ToastProps {
  variant?: ToastVariant;
  message: string;
  duration?: number;
  onClose?: () => void;
  action?: {
    label: string;
    onClick: () => void;
  };
}

const variantStyles: Record<ToastVariant, { bg: string; text: string; icon: string }> = {
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

export function Toast({
  variant = 'info',
  message,
  duration = 4000,
  onClose,
  action,
}: ToastProps) {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    if (duration <= 0) return;

    const timer = setTimeout(() => {
      setIsVisible(false);
      onClose?.();
    }, duration);

    return () => clearTimeout(timer);
  }, [duration, onClose]);

  const handleClose = () => {
    setIsVisible(false);
    onClose?.();
  };

  if (!isVisible) return null;

  const styles = variantStyles[variant];

  return (
    <div
      className={`${styles.bg} ${styles.text} rounded-lg shadow-lg p-4 flex items-center gap-3 max-w-md`}
      role="alert"
    >
      <svg
        className="w-5 h-5 flex-shrink-0"
        fill="currentColor"
        viewBox="0 0 20 20"
      >
        <path fillRule="evenodd" d={styles.icon} clipRule="evenodd" />
      </svg>
      <p className="flex-1 text-sm font-medium">{message}</p>
      {action && (
        <button
          onClick={action.onClick}
          className="ml-2 font-medium hover:opacity-80 focus:outline-none"
        >
          {action.label}
        </button>
      )}
      <button
        onClick={handleClose}
        className="ml-3 hover:opacity-80 focus:outline-none"
        aria-label="Close notification"
      >
        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path
            fillRule="evenodd"
            d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
            clipRule="evenodd"
          />
        </svg>
      </button>
    </div>
  );
}
