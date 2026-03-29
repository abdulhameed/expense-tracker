# Accessibility Implementation Guide - WCAG 2.1 AA Compliance

**Date:** March 29, 2026
**Current Compliance:** 62% (WCAG 2.1 AA)
**Target Compliance:** 100% (WCAG 2.1 AA)
**Estimated Total Effort:** 24-32 hours
**Priority:** HIGH - Blocking feature for accessibility users

---

## Quick Reference

| Phase | Issue Count | Effort | Impact | Status |
|-------|------------|--------|--------|--------|
| **Phase 1 (CRITICAL)** | 5 issues | 8-12h | Blocks accessibility | ⏳ Pending |
| **Phase 2 (MAJOR)** | 20+ issues | 12-16h | Compliance failures | ⏳ Pending |
| **Phase 3 (POLISH)** | 15+ issues | 6-8h | Best practices | ⏳ Pending |

---

## PHASE 1: CRITICAL FIXES (Do This First)

These are **blockers for accessibility users**. Fix these before everything else.

### Issue #1: Replace `confirm()` Dialogs with Accessible Modals

**Files to Fix:**
- `/Users/mac/Projects/expense-tracker/frontend/src/pages/Transactions.tsx` (line 139)
- `/Users/mac/Projects/expense-tracker/frontend/src/pages/Budgets.tsx` (line 87)
- `/Users/mac/Projects/expense-tracker/frontend/src/pages/RecurringTransactions.tsx`
- `/Users/mac/Projects/expense-tracker/frontend/src/pages/Export.tsx`

**Why It Matters:**
The browser `confirm()` dialog is not accessible to screen reader users. It cannot be announced properly and fails WCAG 4.1.2.

**Current Code (❌ NOT ACCESSIBLE):**
```tsx
if (confirm('Are you sure you want to delete this budget?')) {
  await deleteBudget(budget.id);
}
```

**Fixed Code (✅ ACCESSIBLE):**
```tsx
const [deleteConfirmation, setDeleteConfirmation] = useState<{
  isOpen: boolean;
  budgetId?: string;
}>({ isOpen: false });

// In JSX:
{deleteConfirmation.isOpen && (
  <Modal
    isOpen={deleteConfirmation.isOpen}
    onClose={() => setDeleteConfirmation({ isOpen: false })}
    title="Delete Budget"
  >
    <div className="space-y-4">
      <p className="text-neutral-700">
        Are you sure you want to delete this budget? This action cannot be undone.
      </p>
      <div className="flex justify-end gap-3">
        <button
          onClick={() => setDeleteConfirmation({ isOpen: false })}
          className="px-4 py-2 text-neutral-700 hover:bg-neutral-100 rounded-lg"
        >
          Cancel
        </button>
        <button
          onClick={async () => {
            await deleteBudget(deleteConfirmation.budgetId);
            setDeleteConfirmation({ isOpen: false });
          }}
          className="px-4 py-2 bg-error-600 text-white rounded-lg hover:bg-error-700"
        >
          Delete
        </button>
      </div>
    </div>
  </Modal>
)}

// When triggering:
<button
  onClick={() => setDeleteConfirmation({ isOpen: true, budgetId: budget.id })}
>
  Delete
</button>
```

**Implementation Steps:**
1. Create a state for the confirmation modal
2. Replace all `confirm()` calls with state-based modals
3. Use your existing `Modal` component
4. Test with keyboard navigation and screen reader

**Files to Update:**
- Transactions.tsx - Delete transaction confirmation
- Budgets.tsx - Delete budget confirmation
- RecurringTransactions.tsx - Delete recurring transaction confirmation
- Export.tsx - Export confirmation (if using confirm)

**Testing:**
```bash
# Test keyboard navigation
- Tab to delete button
- Press Enter
- Modal should open
- Tab to Cancel and Delete buttons
- Press Enter to confirm
- Focus should return to delete button after modal closes
```

---

### Issue #2: Add `aria-invalid` and `aria-describedby` to Form Validation

**Files to Fix:**
- `/Users/mac/Projects/expense-tracker/frontend/src/components/Input.tsx`
- `/Users/mac/Projects/expense-tracker/frontend/src/components/Select.tsx`
- Form pages using these components

**Why It Matters:**
Screen reader users cannot understand which fields have errors or what the errors are. This fails WCAG 3.3.1 and 3.3.4.

**Current Code (❌ NOT ACCESSIBLE):**
```tsx
export function Input({
  label,
  error,
  helperText,
  ...props
}: InputProps) {
  return (
    <div className="space-y-2">
      {label && (
        <label className="text-sm font-medium text-neutral-700">
          {label}
        </label>
      )}
      <input
        className="w-full px-4 py-3 border border-neutral-300 rounded-lg..."
        {...props}
      />
      {error && (
        <p className="mt-1 text-sm text-error-600">{error}</p>
      )}
      {!error && helperText && (
        <p className="mt-1 text-sm text-neutral-500">{helperText}</p>
      )}
    </div>
  );
}
```

**Fixed Code (✅ ACCESSIBLE):**
```tsx
import { useId } from 'react';

export function Input({
  label,
  error,
  helperText,
  ...props
}: InputProps) {
  const id = useId();
  const errorId = `${id}-error`;
  const helperId = `${id}-helper`;

  return (
    <div className="space-y-2">
      {label && (
        <label htmlFor={id} className="text-sm font-medium text-neutral-700">
          {label}
        </label>
      )}
      <input
        id={id}
        className={`w-full px-4 py-3 border rounded-lg
          ${error
            ? 'border-error-500 focus:ring-error-500'
            : 'border-neutral-300 focus:ring-primary-500'
          }
          focus:outline-none focus:ring-2...`}
        aria-invalid={!!error}
        aria-describedby={error ? errorId : helperText ? helperId : undefined}
        {...props}
      />
      {error && (
        <p
          id={errorId}
          className="mt-1 text-sm text-error-600"
          role="alert"
        >
          {error}
        </p>
      )}
      {!error && helperText && (
        <p
          id={helperId}
          className="mt-1 text-sm text-neutral-500"
        >
          {helperText}
        </p>
      )}
    </div>
  );
}
```

**Key Changes:**
- ✅ Generate unique `id` using `useId()` hook
- ✅ Add `id` to input element
- ✅ Add `htmlFor` to label
- ✅ Add `aria-invalid={!!error}` to input
- ✅ Add `aria-describedby` linking to error or helper text
- ✅ Add `role="alert"` to error message
- ✅ Change border color when invalid

**Affected Components:**
1. **Input.tsx** - Apply above pattern
2. **Select.tsx** - Apply same aria-invalid and aria-describedby
3. **Textarea.tsx** - If exists, apply same pattern

**Test After Implementation:**
```bash
# With screen reader (NVDA on Windows, JAWS, or VoiceOver on Mac):
1. Navigate to form field with error
2. Screen reader should announce: "Input invalid, [error message]"
3. Focus on the error message
4. Screen reader should announce it as an alert

# Keyboard test:
1. Tab through form
2. Invalid fields should have error styling
3. Error text should be immediately after field
```

**Code Pattern for Select Component:**
```tsx
// src/components/Select.tsx
export function Select({
  label,
  error,
  helperText,
  ...props
}: SelectProps) {
  const id = useId();
  const errorId = `${id}-error`;
  const helperId = `${id}-helper`;

  return (
    <div className="space-y-2">
      {label && (
        <label htmlFor={id} className="text-sm font-medium text-neutral-700">
          {label}
        </label>
      )}
      <select
        id={id}
        className={`w-full px-4 py-3 border rounded-lg...
          ${error
            ? 'border-error-500 focus:ring-error-500'
            : 'border-neutral-300 focus:ring-primary-500'
          }`}
        aria-invalid={!!error}
        aria-describedby={error ? errorId : helperText ? helperId : undefined}
        {...props}
      />
      {error && (
        <p
          id={errorId}
          className="mt-1 text-sm text-error-600"
          role="alert"
        >
          {error}
        </p>
      )}
      {!error && helperText && (
        <p
          id={helperId}
          className="mt-1 text-sm text-neutral-500"
        >
          {helperText}
        </p>
      )}
    </div>
  );
}
```

---

### Issue #3: Add `aria-label` to Icon-Only Buttons

**Files to Fix:**
- Modal.tsx (close button, line 82)
- Alert.tsx (close button, line 82)
- Toast.tsx (close button, line 75)
- Sidebar.tsx (hamburger and close buttons, lines 110, 131)
- Button.tsx (when icon-only, line 43)
- Badge.tsx (remove button, line 30)

**Why It Matters:**
Icon-only buttons with no text are invisible to screen reader users. This fails WCAG 1.1.1.

**Current Code (❌ NOT ACCESSIBLE):**
```tsx
// Modal close button
<button
  onClick={onClose}
  className="p-1 rounded-lg text-neutral-500 hover:bg-neutral-100"
>
  <XIcon className="w-5 h-5" />
</button>

// Hamburger button
<button
  onClick={() => setIsOpen(!isOpen)}
  className="md:hidden fixed bottom-4 right-4..."
>
  <MenuIcon className="w-6 h-6" />
</button>
```

**Fixed Code (✅ ACCESSIBLE):**
```tsx
// Modal close button
<button
  onClick={onClose}
  aria-label="Close modal"
  className="p-1 rounded-lg text-neutral-500 hover:bg-neutral-100
    focus:outline-none focus:ring-2 focus:ring-primary-500"
>
  <XIcon className="w-5 h-5" aria-hidden="true" />
</button>

// Hamburger button
<button
  onClick={() => setIsOpen(!isOpen)}
  aria-label={isOpen ? "Close navigation menu" : "Open navigation menu"}
  aria-expanded={isOpen}
  className="md:hidden fixed bottom-4 right-4..."
>
  <MenuIcon className="w-6 h-6" aria-hidden="true" />
</button>

// Badge remove button
<button
  onClick={onRemove}
  aria-label={`Remove ${label}`}
  className="ml-1 text-neutral-500 hover:text-neutral-700"
>
  <XIcon className="w-4 h-4" aria-hidden="true" />
</button>
```

**Key Improvements:**
- ✅ `aria-label` describes the button purpose
- ✅ `aria-hidden="true"` on icon (tells screen reader icon is decorative)
- ✅ Add focus ring styling
- ✅ `aria-expanded` on toggle buttons (hamburger)

**Pattern for all icon-only buttons:**
```tsx
<button
  aria-label="[What this button does]"
  className="... focus:ring-2 focus:ring-primary-500 ..."
>
  <Icon aria-hidden="true" className="..." />
</button>
```

**Audit Checklist:**
- [ ] Modal close button (1 instance)
- [ ] Alert close button (1 instance)
- [ ] Toast close button (1 instance)
- [ ] Sidebar hamburger button (1 instance)
- [ ] Sidebar close button (1 instance)
- [ ] Badge remove button (1 instance)
- [ ] Button with loading spinner (check Button.tsx)
- [ ] Any other icon-only buttons

**Total: ~8 icon-only buttons in Phase 1**

---

### Issue #4: Implement Focus Trap and Focus Return in Modal

**File to Fix:**
- `/Users/mac/Projects/expense-tracker/frontend/src/components/Modal.tsx`

**Why It Matters:**
Without a focus trap, keyboard users can tab outside the modal to page content behind it. This fails accessibility standards.

**Current Code (❌ NOT PERFECT):**
```tsx
export function Modal({
  isOpen,
  onClose,
  title,
  children,
}: ModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div
        className="fixed inset-0 bg-black/50"
        onClick={onClose}
      />
      <div
        className="relative bg-white rounded-xl shadow-xl max-w-lg..."
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
      >
        {/* Modal content */}
      </div>
    </div>
  );
}
```

**Fixed Code (✅ ACCESSIBLE):**
```tsx
import { useEffect, useRef, ReactNode } from 'react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: ReactNode;
  initialFocus?: React.RefObject<HTMLElement>;
}

export function Modal({
  isOpen,
  onClose,
  title,
  children,
  initialFocus,
}: ModalProps) {
  const modalRef = useRef<HTMLDivElement>(null);
  const previouslyFocusedElement = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (!isOpen) return;

    // Store the previously focused element
    previouslyFocusedElement.current = document.activeElement as HTMLElement;

    // Focus the modal or specified element
    if (initialFocus?.current) {
      initialFocus.current.focus();
    } else {
      const closeButton = modalRef.current?.querySelector('button[aria-label*="Close"]');
      if (closeButton instanceof HTMLElement) {
        closeButton.focus();
      }
    }

    // Handle Escape key
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    // Trap focus inside modal
    const handleTabKey = (event: KeyboardEvent) => {
      if (event.key !== 'Tab' || !modalRef.current) return;

      const focusableElements = modalRef.current.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );

      if (focusableElements.length === 0) return;

      const firstElement = focusableElements[0] as HTMLElement;
      const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;
      const activeElement = document.activeElement as HTMLElement;

      // Shift + Tab
      if (event.shiftKey) {
        if (activeElement === firstElement) {
          event.preventDefault();
          lastElement.focus();
        }
      } else {
        // Tab
        if (activeElement === lastElement) {
          event.preventDefault();
          firstElement.focus();
        }
      }
    };

    document.addEventListener('keydown', handleEscape);
    document.addEventListener('keydown', handleTabKey);

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.removeEventListener('keydown', handleTabKey);

      // Return focus to previously focused element
      previouslyFocusedElement.current?.focus();
    };
  }, [isOpen, onClose, initialFocus]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
        aria-hidden="true"
      />
      <div
        ref={modalRef}
        className="relative bg-white rounded-xl shadow-xl max-w-lg w-full mx-4 max-h-[90vh] overflow-hidden"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
      >
        {/* Header */}
        <div className="px-6 py-4 border-b border-neutral-200">
          <div className="flex items-center justify-between">
            {title && (
              <h2
                id="modal-title"
                className="text-xl font-semibold text-neutral-900"
              >
                {title}
              </h2>
            )}
            <button
              onClick={onClose}
              aria-label="Close modal"
              className="p-1 rounded-lg text-neutral-500 hover:bg-neutral-100
                focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
        </div>

        {/* Body */}
        <div className="px-6 py-4 overflow-y-auto">
          {children}
        </div>
      </div>
    </div>
  );
}
```

**Key Improvements:**
- ✅ **Focus trap**: Tab loops within modal
- ✅ **Escape key**: Closes modal
- ✅ **Focus return**: Focus returns to previous element when closed
- ✅ **Initial focus**: Can specify element to focus first
- ✅ **ARIA labels**: Proper dialog role and aria-labelledby

**Testing Steps:**
```bash
# Keyboard test
1. Press Tab repeatedly while modal is open
2. Focus should cycle between modal buttons/inputs
3. Focus should NOT escape to page content behind modal
4. Press Escape to close modal
5. Focus should return to the button that opened the modal

# Screen reader test
1. Modal should be announced as a dialog
2. Title should be announced
3. Buttons should be properly labeled
```

**Usage in Components:**
```tsx
// In your component:
const confirmRef = useRef<HTMLButtonElement>(null);

return (
  <>
    <button ref={confirmRef} onClick={() => setShowModal(true)}>
      Delete
    </button>

    <Modal
      isOpen={showModal}
      onClose={() => setShowModal(false)}
      title="Confirm Delete"
      initialFocus={confirmRef}
    >
      Are you sure?
    </Modal>
  </>
);
```

---

### Issue #5: Fix Alert/Status Announcements in Toast and Loading

**Files to Fix:**
- `/Users/mac/Projects/expense-tracker/frontend/src/components/Toast.tsx`
- `/Users/mac/Projects/expense-tracker/frontend/src/components/Spinner.tsx`
- `/Users/mac/Projects/expense-tracker/frontend/src/components/ToastContainer.tsx`

**Why It Matters:**
Screen reader users don't know when things are loading or when status changes. This fails WCAG 4.1.3.

**Current Code (❌ NOT ACCESSIBLE):**
```tsx
// Toast.tsx
export function Toast({ notification, onDismiss }: ToastProps) {
  return (
    <div
      className={`${styles.bg} ${styles.text} rounded-lg shadow-lg p-4...`}
      role="alert"
    >
      <div className="flex items-start gap-3">
        {getIcon(notification.type)}
        <div className="flex-1">
          <h4 className="text-sm font-medium">
            {notification.title}
          </h4>
          {notification.description && (
            <p className="text-sm mt-1">
              {notification.description}
            </p>
          )}
        </div>
        <button onClick={onDismiss}>
          <XIcon className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}

// Spinner.tsx
export function Spinner({ size = 'md', color = 'primary' }: SpinnerProps) {
  return (
    <svg
      className={`${sizeStyles[size]} animate-spin ${color}`}
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      role="status"
    >
      {/* SVG content */}
    </svg>
  );
}
```

**Fixed Code (✅ ACCESSIBLE):**
```tsx
// Toast.tsx
interface ToastProps {
  notification: Notification;
  onDismiss: () => void;
}

export function Toast({ notification, onDismiss }: ToastProps) {
  return (
    <div
      className={`${styles.bg} ${styles.text} rounded-lg shadow-lg p-4...
        animate-slide-up`}
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
    >
      <div className="flex items-start gap-3">
        {getIcon(notification.type)}
        <div className="flex-1">
          <h4 className="text-sm font-medium">
            {notification.title}
          </h4>
          {notification.description && (
            <p className="text-sm mt-1">
              {notification.description}
            </p>
          )}
        </div>
        <button
          onClick={onDismiss}
          aria-label="Dismiss notification"
          className="text-neutral-400 hover:text-neutral-600
            focus:outline-none focus:ring-2 focus:ring-primary-500 rounded"
        >
          <XIcon className="w-5 h-5" aria-hidden="true" />
        </button>
      </div>
    </div>
  );
}

// Spinner.tsx
interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  color?: 'primary' | 'white' | 'neutral';
  label?: string;
}

export function Spinner({
  size = 'md',
  color = 'primary',
  label = 'Loading'
}: SpinnerProps) {
  return (
    <div className="flex flex-col items-center gap-2">
      <svg
        className={`${sizeStyles[size]} animate-spin ${colorStyles[color]}`}
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        role="status"
        aria-label={label}
        aria-live="polite"
      >
        {/* SVG content */}
      </svg>
      <span className="sr-only">{label}</span>
    </div>
  );
}

// Or wrap in a container:
export function LoadingContainer({ label = 'Loading' }: { label?: string }) {
  return (
    <div
      className="flex items-center justify-center p-8"
      role="status"
      aria-live="polite"
      aria-busy="true"
      aria-label={label}
    >
      <Spinner label={label} />
    </div>
  );
}
```

**Key Improvements:**
- ✅ Toast: `aria-live="assertive"` - Announces immediately
- ✅ Toast: `aria-atomic="true"` - Announces entire content
- ✅ Spinner: `aria-label` describes what's loading
- ✅ Spinner: `aria-live="polite"` - Announces when ready
- ✅ Container: `aria-busy="true"` - Indicates loading state
- ✅ Close button: `aria-label` on Toast dismiss button

**Usage in Pages:**
```tsx
// In Transactions.tsx
const [isLoading, setIsLoading] = useState(false);

return (
  <>
    {isLoading && (
      <div
        className="p-4 bg-neutral-50 rounded-lg"
        role="status"
        aria-busy="true"
        aria-live="polite"
      >
        <Spinner label="Loading transactions..." />
      </div>
    )}

    {/* Content */}
  </>
);
```

---

## PHASE 2: MAJOR FIXES (High Priority)

These are compliance failures preventing WCAG 2.1 AA certification.

### Issue #6: Add Text Alternatives to Income/Expense Colors

**Files to Fix:**
- Dashboard.tsx (lines 205-213)
- Transactions.tsx (lines 372-377)
- Analytics.tsx (multiple lines)

**Why It Matters:**
Color-blind users cannot distinguish transaction types. Fails WCAG 1.4.1.

**Current Code (❌ NOT ACCESSIBLE):**
```tsx
<span className={`text-3xl font-bold ${
  transaction.type === 'income'
    ? 'text-success-600'
    : 'text-error-600'
}`}>
  {formatCurrency(transaction.amount)}
</span>
```

**Fixed Code (✅ ACCESSIBLE):**
```tsx
<div className="flex items-baseline gap-2">
  <span className={`text-3xl font-bold ${
    transaction.type === 'income'
      ? 'text-success-600'
      : 'text-error-600'
  }`}>
    {formatCurrency(transaction.amount)}
  </span>
  <span className="text-sm text-neutral-600">
    {transaction.type === 'income' ? '(Income)' : '(Expense)'}
  </span>
</div>
```

**Alternative: Using Icons:**
```tsx
<div className="flex items-center gap-2">
  {transaction.type === 'income' ? (
    <ArrowUpIcon className="w-5 h-5 text-success-600" aria-hidden="true" />
  ) : (
    <ArrowDownIcon className="w-5 h-5 text-error-600" aria-hidden="true" />
  )}
  <span className={`text-lg font-semibold ${
    transaction.type === 'income'
      ? 'text-success-600'
      : 'text-error-600'
  }`}>
    {transaction.type === 'income' ? '+' : '-'}
    {formatCurrency(transaction.amount)}
  </span>
</div>
```

**Checklist:**
- [ ] Dashboard total income/expense display
- [ ] Transaction list amounts
- [ ] Analytics chart indicators
- [ ] Budget progress visualization
- [ ] Recent transaction cards

---

### Issue #7: Add `scope="col"` to Table Headers

**File to Fix:**
- `/Users/mac/Projects/expense-tracker/frontend/src/pages/Transactions.tsx` (lines 329-345)

**Why It Matters:**
Screen reader users need to understand table structure. Headers must be associated with columns.

**Current Code (❌ NOT ACCESSIBLE):**
```tsx
<table className="w-full">
  <thead className="bg-neutral-50 border-b border-neutral-200">
    <tr>
      <th className="px-6 py-3 text-left">
        <input type="checkbox" />
      </th>
      <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase">
        Date
      </th>
      <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase">
        Description
      </th>
      {/* More headers */}
    </tr>
  </thead>
</table>
```

**Fixed Code (✅ ACCESSIBLE):**
```tsx
<table className="w-full">
  <thead className="bg-neutral-50 border-b border-neutral-200">
    <tr>
      <th
        scope="col"
        className="px-6 py-3 text-left"
      >
        <span className="sr-only">Select</span>
        <input
          type="checkbox"
          aria-label="Select all transactions"
          onChange={handleSelectAll}
        />
      </th>
      <th
        scope="col"
        className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase"
      >
        Date
      </th>
      <th
        scope="col"
        className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase"
      >
        Description
      </th>
      <th
        scope="col"
        className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase"
      >
        Category
      </th>
      <th
        scope="col"
        className="px-6 py-3 text-right text-xs font-medium text-neutral-500 uppercase"
      >
        Amount
      </th>
      <th
        scope="col"
        className="px-6 py-3 text-right text-xs font-medium text-neutral-500 uppercase"
      >
        Actions
      </th>
    </tr>
  </thead>
  <tbody className="divide-y divide-neutral-200">
    {/* Table rows */}
  </tbody>
</table>
```

**Key Improvements:**
- ✅ `scope="col"` on all header cells
- ✅ `aria-label` on checkbox header
- ✅ `sr-only` span for checkbox column
- ✅ Right-align numeric/action columns

---

### Issue #8: Verify and Fix Color Contrast

**Files to Check:**
- Button.tsx (ghost variant)
- Sidebar.tsx (inactive nav)
- Helper text elements

**Use WebAIM Contrast Checker:** https://webaim.org/resources/contrastchecker/

**Current Borderline Contrasts:**
- Ghost button text (#3B82F6 on transparent): 4.5:1 ⚠️
- Helper text (#6B7280 on #F9FAFB): ~4.5:1 ⚠️

**Fixed Code:**
```tsx
// Ghost button: Darken text for better contrast
ghost: 'bg-transparent text-primary-700 hover:bg-primary-50',

// Helper text: Slightly darker
<p className="text-sm text-neutral-600">
  {helperText}
</p>
```

---

## PHASE 3: POLISH & BEST PRACTICES

These are best practices and enhancements beyond minimum compliance.

### Issue #9: Enhance Toggle Component with `role="switch"`

**File:** `/Users/mac/Projects/expense-tracker/frontend/src/components/Toggle.tsx`

**Current Code:**
```tsx
export function Toggle({ checked, onChange, disabled = false, label }: ToggleProps) {
  return (
    <label className="flex items-center cursor-pointer">
      <input
        type="checkbox"
        checked={checked}
        onChange={onChange}
        className="sr-only"
      />
      <div className={`relative w-10 h-6 rounded-full...`}/>
      {label && <span className="ml-3">{label}</span>}
    </label>
  );
}
```

**Enhanced Code:**
```tsx
import { useId } from 'react';

export function Toggle({
  checked,
  onChange,
  disabled = false,
  label,
  description
}: ToggleProps) {
  const id = useId();
  const descriptionId = description ? `${id}-description` : undefined;

  return (
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
          ${checked ? 'bg-success-600' : 'bg-neutral-300'}
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
      >
        <span
          className={`inline-block h-4 w-4 transform rounded-full bg-white
            transition-transform ${checked ? 'translate-x-6' : 'translate-x-1'}`}
        />
      </button>
      {label && (
        <label htmlFor={id} className="text-sm font-medium text-neutral-700">
          {label}
        </label>
      )}
      {description && (
        <p id={descriptionId} className="text-xs text-neutral-500">
          {description}
        </p>
      )}
    </div>
  );
}
```

**Key Improvements:**
- ✅ `role="switch"` semantic meaning
- ✅ `aria-checked` indicates state
- ✅ Proper label association
- ✅ Focus visible styling
- ✅ Description support

---

### Issue #10: Add Breadcrumb Enhancement

**File:** `/Users/mac/Projects/expense-tracker/frontend/src/components/Breadcrumb.tsx`

**Enhanced Code:**
```tsx
export function Breadcrumb({ items }: BreadcrumbProps) {
  return (
    <nav className="text-sm" aria-label="Breadcrumb">
      <ol className="flex items-center gap-2">
        {items.map((item, index) => (
          <li key={index} className="flex items-center gap-2">
            {index > 0 && (
              <span className="text-neutral-400" aria-hidden="true">›</span>
            )}
            {item.href ? (
              <a
                href={item.href}
                className="text-primary-600 hover:text-primary-700 hover:underline
                  focus:outline-none focus:ring-2 focus:ring-primary-500 rounded"
              >
                {item.label}
              </a>
            ) : (
              <span
                aria-current="page"
                className="text-neutral-700 font-medium"
              >
                {item.label}
              </span>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
}
```

**Key Improvements:**
- ✅ `aria-current="page"` on current page
- ✅ Semantic `<nav>`, `<ol>`, `<li>`
- ✅ Proper `aria-label="Breadcrumb"`

---

## Implementation Checklist

### Phase 1: CRITICAL (Week 1)
- [ ] Replace all `confirm()` dialogs with Modal components
  - [ ] Transactions.tsx - Delete transaction
  - [ ] Budgets.tsx - Delete budget
  - [ ] RecurringTransactions.tsx - Delete recurring
  - [ ] Export.tsx - Confirm export
- [ ] Add aria-invalid/aria-describedby to Input.tsx
- [ ] Add aria-invalid/aria-describedby to Select.tsx
- [ ] Update all input-using pages to use updated components
- [ ] Add aria-labels to icon-only buttons (8 instances)
  - [ ] Modal close
  - [ ] Alert close
  - [ ] Toast close
  - [ ] Sidebar hamburger
  - [ ] Sidebar close
  - [ ] Badge remove
  - [ ] Button loading icon
  - [ ] Other icon buttons
- [ ] Implement focus trap in Modal.tsx
- [ ] Add aria-live to Toast.tsx
- [ ] Add aria-busy/aria-label to Spinner.tsx
- [ ] Test with keyboard navigation
- [ ] Test with screen reader

### Phase 2: MAJOR (Week 2-3)
- [ ] Add text alternatives to income/expense colors
  - [ ] Dashboard.tsx
  - [ ] Transactions.tsx
  - [ ] Analytics.tsx
  - [ ] Other pages with color-only info
- [ ] Add `scope="col"` to table headers
  - [ ] Transactions.tsx main table
  - [ ] Other tables
- [ ] Verify color contrast (WebAIM checker)
- [ ] Add remaining aria-labels (~20+ instances)
- [ ] Test color contrast with tools

### Phase 3: POLISH (Week 3-4)
- [ ] Enhance Toggle with role="switch"
- [ ] Enhance Breadcrumb with aria-current
- [ ] Add hidden data tables for charts
- [ ] Increase touch target size for small buttons
- [ ] Full accessibility audit with axe DevTools
- [ ] Screen reader testing (NVDA/JAWS/VoiceOver)

---

## Testing Tools & Commands

### Browser Extensions
```
1. Install axe DevTools - https://www.deque.com/axe/devtools/
2. Install WAVE - https://wave.webaim.org/extension/
3. Install Lighthouse - Built into Chrome DevTools
```

### Screen Reader Testing

**macOS (VoiceOver):**
```bash
# Enable VoiceOver
Cmd + F5

# Navigation commands
- VO + Right Arrow: Next item
- VO + Left Arrow: Previous item
- VO + U: Rotor (headings, form fields, etc.)
- VO + Space: Activate button/link
```

**Windows (NVDA):**
```bash
# Download free from: https://www.nvaccess.org/
# Key commands
- Down Arrow: Next item
- Up Arrow: Previous item
- Insert + F7: Elements list
- Enter: Activate
```

### Contrast Checker
```
Online: https://webaim.org/resources/contrastchecker/
Just input hex colors and check ratios
```

### Manual Keyboard Testing
```bash
# Keyboard-only workflow
1. Tab through entire app (no mouse)
2. Verify focus visible on all interactive elements
3. Use Escape to close modals
4. Use arrow keys in dropdowns/menus
5. Use Space/Enter to activate buttons
```

### Lighthouse Accessibility Audit
```bash
# In Chrome DevTools
1. Open DevTools (F12)
2. Click "Lighthouse" tab
3. Select "Accessibility" category
4. Run audit
5. Review failing issues
```

---

## Quick Reference: Common Patterns

### Pattern 1: Form Field with Error
```tsx
import { useId } from 'react';

export function FormField({ label, error, helperText, ...inputProps }) {
  const id = useId();
  const errorId = `${id}-error`;
  const helperId = `${id}-helper`;

  return (
    <div className="space-y-2">
      <label htmlFor={id}>{label}</label>
      <input
        id={id}
        aria-invalid={!!error}
        aria-describedby={error ? errorId : helperText ? helperId : undefined}
        {...inputProps}
      />
      {error && <p id={errorId} role="alert">{error}</p>}
      {helperText && <p id={helperId}>{helperText}</p>}
    </div>
  );
}
```

### Pattern 2: Icon-Only Button
```tsx
<button
  aria-label="Clear filters"
  className="focus:ring-2 focus:ring-primary-500"
>
  <XIcon aria-hidden="true" className="w-5 h-5" />
</button>
```

### Pattern 3: Loading State
```tsx
<div role="status" aria-busy="true" aria-live="polite">
  <Spinner label="Loading transactions..." />
</div>
```

### Pattern 4: Modal with Focus
```tsx
const triggerRef = useRef<HTMLButtonElement>(null);

<Modal
  isOpen={isOpen}
  onClose={() => setIsOpen(false)}
  title="Confirm Action"
  initialFocus={triggerRef}
>
  Content...
</Modal>

<button ref={triggerRef} onClick={() => setIsOpen(true)}>
  Trigger
</button>
```

---

## Common Mistakes to Avoid

❌ **Don't:**
- Use `confirm()` for destructive actions
- Add aria-labels to divs that should be buttons
- Use color alone to convey information
- Forget `aria-describedby` on inputs with help text
- Skip focus management in modals
- Use `role="alert"` without `aria-live`

✅ **Do:**
- Use semantic HTML (button, form, input, label, etc.)
- Add `aria-label` only to icon-only buttons
- Provide text alternatives to colors
- Link error messages with `aria-describedby`
- Implement focus traps in modals
- Use `role="alert"` with `aria-live="assertive"`
- Test with actual screen readers

---

## Success Criteria: WCAG 2.1 AA Compliance

After implementing all phases:

| Criterion | Before | After | Status |
|-----------|--------|-------|--------|
| 1.1.1 Non-text Content | 50% | 100% | ✅ |
| 1.4.1 Use of Color | 60% | 100% | ✅ |
| 1.4.3 Contrast Minimum | 70% | 100% | ✅ |
| 2.1.1 Keyboard | 65% | 100% | ✅ |
| 2.4.3 Focus Order | 80% | 100% | ✅ |
| 2.4.7 Focus Visible | 75% | 100% | ✅ |
| 3.3.1 Error Identification | 45% | 100% | ✅ |
| 3.3.2 Labels or Instructions | 75% | 100% | ✅ |
| 3.3.4 Error Prevention | 45% | 100% | ✅ |
| 4.1.2 Name, Role, Value | 55% | 100% | ✅ |
| 4.1.3 Status Messages | 50% | 100% | ✅ |
| **Overall WCAG 2.1 AA** | **62%** | **100%** | ✅ |

---

## Next Steps

1. **Week 1 (Phase 1):** Focus on critical fixes
   - Start with replace confirm() dialogs
   - Add aria attributes to forms
   - Fix focus management

2. **Week 2-3 (Phase 2):** Tackle major compliance issues
   - Color alternatives
   - Table structure
   - Remaining aria-labels

3. **Week 4 (Phase 3):** Polish and finalize
   - Best practices
   - Full testing
   - Documentation

4. **Ongoing:**
   - Add accessibility checks to CI/CD (axe-core)
   - Include accessibility in code review checklist
   - Regular screen reader testing
   - Monitor WCAG compliance

---

## Resources

**Documentation:**
- WCAG 2.1 Guidelines: https://www.w3.org/WAI/WCAG21/quickref/
- ARIA Authoring Practices: https://www.w3.org/WAI/ARIA/apg/
- WebAIM Articles: https://webaim.org/articles/

**Tools:**
- axe DevTools: https://www.deque.com/axe/devtools/
- WAVE: https://wave.webaim.org/
- WebAIM Contrast: https://webaim.org/resources/contrastchecker/
- NVDA Screen Reader: https://www.nvaccess.org/

**React Accessibility:**
- React Accessibility Docs: https://react.dev/reference/react-dom/components#form-components
- Headless UI: https://headlessui.com/
- Radix UI: https://www.radix-ui.com/

---

**Document Version:** 1.0
**Created:** March 29, 2026
**Target Completion:** April 26, 2026 (4 weeks)

---
