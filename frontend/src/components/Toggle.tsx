interface ToggleProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  disabled?: boolean;
  label?: string;
}

export function Toggle({ checked, onChange, disabled = false, label }: ToggleProps) {
  return (
    <label className="flex items-center cursor-pointer">
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        disabled={disabled}
        className="sr-only"
      />
      <div className={`relative w-10 h-6 rounded-full transition-colors ${
        checked ? 'bg-primary-600' : 'bg-neutral-300'
      } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}>
        <div
          className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${
            checked ? 'translate-x-4' : ''
          }`}
        />
      </div>
      {label && <span className="ml-3 text-sm font-medium text-neutral-900">{label}</span>}
    </label>
  );
}
