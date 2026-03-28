import { ReactNode, useState } from 'react';

type AlertVariant = 'success' | 'warning' | 'error' | 'info';

interface AlertProps {
  variant?: AlertVariant;
  title?: string;
  children: ReactNode;
  onClose?: () => void;
  closeable?: boolean;
}

const variantStyles: Record<AlertVariant, { bg: string; border: string; text: string; icon: string }> = {
  success: {
    bg: 'bg-success-50',
    border: 'border-l-4 border-success-500',
    text: 'text-success-800',
    icon: 'text-success-500',
  },
  warning: {
    bg: 'bg-warning-50',
    border: 'border-l-4 border-warning-500',
    text: 'text-warning-800',
    icon: 'text-warning-500',
  },
  error: {
    bg: 'bg-error-50',
    border: 'border-l-4 border-error-500',
    text: 'text-error-800',
    icon: 'text-error-500',
  },
  info: {
    bg: 'bg-primary-50',
    border: 'border-l-4 border-primary-500',
    text: 'text-primary-800',
    icon: 'text-primary-500',
  },
};

const icons: Record<AlertVariant, string> = {
  success: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
  warning: 'M12 8v4m0 4v.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
  error: 'M10 14l-2-2m0 0l-2-2m2 2l2-2m-2 2l-2 2',
  info: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
};

export function Alert({
  variant = 'info',
  title,
  children,
  onClose,
  closeable = true,
}: AlertProps) {
  const [isVisible, setIsVisible] = useState(true);

  const handleClose = () => {
    setIsVisible(false);
    onClose?.();
  };

  if (!isVisible) return null;

  const styles = variantStyles[variant];

  return (
    <div className={`${styles.bg} ${styles.border} p-4 rounded-md`}>
      <div className="flex items-start">
        <svg
          className={`w-5 h-5 ${styles.icon} mt-0.5 flex-shrink-0`}
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path fillRule="evenodd" d={icons[variant]} clipRule="evenodd" />
        </svg>
        <div className="ml-3 flex-1">
          {title && <h3 className={`text-sm font-medium ${styles.text}`}>{title}</h3>}
          <div className={`text-sm ${styles.text} ${title ? 'mt-1' : ''}`}>{children}</div>
        </div>
        {closeable && (
          <button
            onClick={handleClose}
            className={`ml-3 inline-flex ${styles.icon} hover:opacity-70 focus:outline-none`}
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                clipRule="evenodd"
              />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
}
