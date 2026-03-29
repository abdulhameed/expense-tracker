import { useId } from 'react';

interface ToggleProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  disabled?: boolean;
  label?: string;
  description?: string;
}

export function Toggle({ checked, onChange, disabled = false, label, description }: ToggleProps) {
  const id = useId();
  const descriptionId = description ? `${id}-description` : undefined;

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center gap-3">
        <button
          id={id}
          role="switch"
          aria-checked={checked}
          aria-label={label}
          aria-describedby={descriptionId}
          disabled={disabled}
          onClick={() => onChange(!checked)}
          className={`relative inline-flex h-6 w-11 items-center rounded-full
            transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
            ${checked ? 'bg-primary-600' : 'bg-neutral-300'}
            ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
        >
          <span
            className={`inline-block h-4 w-4 transform rounded-full bg-white
              transition-transform ${checked ? 'translate-x-6' : 'translate-x-1'}`}
            aria-hidden="true"
          />
        </button>
        {label && (
          <label htmlFor={id} className="text-sm font-medium text-neutral-700">
            {label}
          </label>
        )}
      </div>
      {description && (
        <p id={descriptionId} className="text-xs text-neutral-500">
          {description}
        </p>
      )}
    </div>
  );
}
