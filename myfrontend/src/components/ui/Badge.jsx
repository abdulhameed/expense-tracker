import React from 'react';
import { cn } from '../../utils/cn';

const variants = {
  success: 'bg-success-50 text-success-700',
  warning: 'bg-warning-50 text-warning-700',
  error: 'bg-error-50 text-error-700',
  primary: 'bg-primary-50 text-primary-700',
  neutral: 'bg-neutral-100 text-neutral-700',
};

export const Badge = ({ children, variant = 'primary', className, icon }) => {
  return (
    <span className={cn(
      "inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium",
      variants[variant],
      className
    )}>
      {icon}
      {children}
    </span>
  );
};
