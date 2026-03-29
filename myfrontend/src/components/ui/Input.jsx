import React, { forwardRef } from 'react';
import { cn } from '../../utils/cn';

export const Input = forwardRef(({ className, wrapperClassName, label, hint, error, id, type = 'text', leftIcon, ...props }, ref) => {
  const inputId = id || React.useId();

  return (
    <div className={cn("space-y-2", wrapperClassName)}>
      {label && (
        <label htmlFor={inputId} className="text-sm font-medium text-neutral-700 block">
          {label}
        </label>
      )}
      <div className="relative">
        {leftIcon && (
          <span className="absolute left-4 top-1/2 -translate-y-1/2 text-neutral-500 font-mono">
            {leftIcon}
          </span>
        )}
        <input
          id={inputId}
          ref={ref}
          type={type}
          className={cn(
            "w-full px-4 py-3 border border-neutral-300 rounded-lg text-neutral-900",
            "placeholder:text-neutral-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
            "disabled:bg-neutral-100 disabled:cursor-not-allowed transition-colors",
            leftIcon && "pl-8",
            error && "border-error-500 focus:ring-error-500",
            className
          )}
          {...props}
        />
      </div>
      {hint && !error && <p className="text-sm text-neutral-500">{hint}</p>}
      {error && <p className="text-sm text-error-600">{error}</p>}
    </div>
  );
});
Input.displayName = 'Input';
