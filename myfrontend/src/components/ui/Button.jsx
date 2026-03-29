import React, { forwardRef } from 'react';
import { cn } from '../../utils/cn';

const variants = {
  primary: 'bg-primary-600 text-white hover:bg-primary-700',
  secondary: 'bg-white border-2 border-neutral-300 text-neutral-700 hover:bg-neutral-50',
  ghost: 'bg-transparent text-primary-600 hover:bg-primary-50',
  danger: 'bg-error-600 text-white hover:bg-error-700',
  success: 'bg-success-600 text-white hover:bg-success-700',
};

const sizes = {
  sm: 'px-4 py-2 text-sm',
  md: 'px-6 py-3 text-base',
  lg: 'px-8 py-4 text-lg',
  icon: 'p-2',
};

export const Button = forwardRef(({ 
  children, 
  variant = 'primary', 
  size = 'md',
  className,
  ...props 
}, ref) => {
  return (
    <button
      ref={ref}
      className={cn(
        'font-medium rounded-lg',
        'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        'transition-colors duration-200',
        variants[variant],
        sizes[size],
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
});

Button.displayName = 'Button';
