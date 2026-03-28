import { forwardRef, InputHTMLAttributes } from 'react';

interface RadioProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Radio = forwardRef<HTMLInputElement, RadioProps>(
  (
    {
      label,
      error,
      className,
      id,
      disabled,
      ...props
    },
    ref
  ) => {
    const radioId = id || `radio-${Math.random().toString(36).substr(2, 9)}`;

    const baseRadioStyles =
      'w-4 h-4 text-primary-600 border-neutral-300 focus:ring-2 focus:ring-primary-500 disabled:bg-neutral-100 disabled:cursor-not-allowed';
    const combinedRadioClassName = `${baseRadioStyles} ${className || ''}`;

    return (
      <div className="flex items-start">
        <input
          ref={ref}
          type="radio"
          id={radioId}
          disabled={disabled}
          className={combinedRadioClassName}
          {...props}
        />
        {label && (
          <label
            htmlFor={radioId}
            className="ml-3 text-sm font-medium text-neutral-700 cursor-pointer disabled:cursor-not-allowed"
          >
            {label}
          </label>
        )}
        {error && <p className="mt-1 text-sm text-error-600">{error}</p>}
      </div>
    );
  }
);

Radio.displayName = 'Radio';
