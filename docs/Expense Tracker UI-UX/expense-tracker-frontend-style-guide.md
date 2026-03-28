# Expense Tracker - Frontend Style Guide & Component Specifications

**Version:** 1.0  
**Last Updated:** March 27, 2026  
**Design System:** Professional Dashboard Style  
**Framework:** React + Tailwind CSS + shadcn/ui

---

## Table of Contents
1. [Design Philosophy](#design-philosophy)
2. [Color System](#color-system)
3. [Typography](#typography)
4. [Spacing & Layout](#spacing--layout)
5. [Components Library](#components-library)
6. [Page Layouts](#page-layouts)
7. [Data Visualization](#data-visualization)
8. [Animations & Interactions](#animations--interactions)
9. [Responsive Design](#responsive-design)
10. [Accessibility Guidelines](#accessibility-guidelines)
11. [Implementation Guide](#implementation-guide)

---

## 1. Design Philosophy

### Core Principles

**Clarity First**
- Financial data must be immediately understandable
- Clear visual hierarchy guides users to important information
- No decorative elements that don't serve a purpose

**Professional Yet Friendly**
- Clean, modern aesthetic that builds trust
- Approachable for personal use, credible for business
- Balanced between corporate and consumer

**Data-Driven Design**
- Charts and visualizations are first-class citizens
- Numbers should be prominent and scannable
- Context always provided for financial metrics

**Consistent & Predictable**
- Similar actions look similar across the app
- Patterns established early are maintained throughout
- User expectations are never violated

---

## 2. Color System

### Primary Palette

```css
/* Primary - Trust & Stability */
--primary-50: #EFF6FF;    /* Lightest */
--primary-100: #DBEAFE;
--primary-200: #BFDBFE;
--primary-300: #93C5FD;
--primary-400: #60A5FA;
--primary-500: #3B82F6;   /* Main primary */
--primary-600: #2563EB;   /* Hover states */
--primary-700: #1D4ED8;
--primary-800: #1E40AF;
--primary-900: #1E3A8A;   /* Darkest */

/* Success - Income & Positive Actions */
--success-50: #F0FDF4;
--success-100: #DCFCE7;
--success-500: #10B981;   /* Main success */
--success-600: #059669;   /* Hover */
--success-700: #047857;

/* Error - Expenses & Alerts */
--error-50: #FEF2F2;
--error-100: #FEE2E2;
--error-500: #EF4444;     /* Main error */
--error-600: #DC2626;     /* Hover */
--error-700: #B91C1C;

/* Warning - Budget Alerts */
--warning-50: #FFFBEB;
--warning-100: #FEF3C7;
--warning-500: #F59E0B;   /* Main warning */
--warning-600: #D97706;   /* Hover */
--warning-700: #B45309;

/* Neutral - Text & Backgrounds */
--neutral-50: #F9FAFB;    /* Background */
--neutral-100: #F3F4F6;   /* Card background */
--neutral-200: #E5E7EB;   /* Borders */
--neutral-300: #D1D5DB;
--neutral-400: #9CA3AF;   /* Disabled text */
--neutral-500: #6B7280;   /* Secondary text */
--neutral-600: #4B5563;
--neutral-700: #374151;   /* Body text */
--neutral-800: #1F2937;   /* Headings */
--neutral-900: #111827;   /* Emphasis */
```

### Semantic Colors

```css
/* Application-Specific Colors */
--income-color: var(--success-500);
--expense-color: var(--error-500);
--budget-progress: var(--primary-500);
--budget-warning: var(--warning-500);
--budget-exceeded: var(--error-500);

/* UI Element Colors */
--background: #FFFFFF;
--background-secondary: var(--neutral-50);
--card-background: #FFFFFF;
--border: var(--neutral-200);
--text-primary: var(--neutral-900);
--text-secondary: var(--neutral-600);
--text-tertiary: var(--neutral-500);
```

### Color Usage Guidelines

**Income (Green)**
- Use for: Income transactions, positive balance changes, budget surplus
- Icon color: `--success-600`
- Background: `--success-50`

**Expenses (Red)**
- Use for: Expense transactions, negative balance changes, budget deficit
- Icon color: `--error-600`
- Background: `--error-50`

**Primary (Blue)**
- Use for: Primary actions, links, active states, charts
- Buttons, links, selected items

**Neutral (Gray)**
- Use for: Text, borders, backgrounds, disabled states
- Maintain strong contrast ratios

---

## 3. Typography

### Font Family

```css
/* Primary Font - Inter */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

--font-family-base: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* Monospace for Numbers */
--font-family-mono: 'SF Mono', 'Monaco', 'Consolas', monospace;
```

### Type Scale

```css
/* Display - Hero sections */
--text-display: 3.75rem;      /* 60px */
--text-display-weight: 800;
--text-display-line-height: 1.1;

/* Headings */
--text-h1: 2.25rem;           /* 36px */
--text-h1-weight: 700;
--text-h1-line-height: 1.2;

--text-h2: 1.875rem;          /* 30px */
--text-h2-weight: 600;
--text-h2-line-height: 1.3;

--text-h3: 1.5rem;            /* 24px */
--text-h3-weight: 600;
--text-h3-line-height: 1.4;

--text-h4: 1.25rem;           /* 20px */
--text-h4-weight: 600;
--text-h4-line-height: 1.4;

/* Body Text */
--text-body-lg: 1.125rem;     /* 18px */
--text-body-lg-weight: 400;
--text-body-lg-line-height: 1.6;

--text-body: 1rem;            /* 16px */
--text-body-weight: 400;
--text-body-line-height: 1.5;

--text-body-sm: 0.875rem;     /* 14px */
--text-body-sm-weight: 400;
--text-body-sm-line-height: 1.5;

/* UI Elements */
--text-caption: 0.75rem;      /* 12px */
--text-caption-weight: 500;
--text-caption-line-height: 1.4;

--text-label: 0.875rem;       /* 14px */
--text-label-weight: 500;
--text-label-line-height: 1.4;

/* Financial Numbers - Use Monospace */
--text-amount-lg: 2rem;       /* 32px */
--text-amount: 1.5rem;        /* 24px */
--text-amount-sm: 1.25rem;    /* 20px */
--text-amount-font: var(--font-family-mono);
--text-amount-weight: 600;
```

### Typography Examples

```html
<!-- Page Title -->
<h1 class="text-3xl font-bold text-neutral-900">Dashboard</h1>

<!-- Section Title -->
<h2 class="text-2xl font-semibold text-neutral-800">Recent Transactions</h2>

<!-- Card Title -->
<h3 class="text-lg font-semibold text-neutral-800">Monthly Summary</h3>

<!-- Body Text -->
<p class="text-base text-neutral-700">Your expense tracking overview</p>

<!-- Small Text -->
<p class="text-sm text-neutral-600">Last updated 2 hours ago</p>

<!-- Financial Amount -->
<span class="text-2xl font-semibold font-mono text-neutral-900">$1,234.56</span>

<!-- Label -->
<label class="text-sm font-medium text-neutral-700">Transaction Title</label>

<!-- Caption -->
<span class="text-xs text-neutral-500">March 2026</span>
```

---

## 4. Spacing & Layout

### Spacing Scale

```css
/* Based on 4px base unit */
--space-0: 0;
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-5: 1.25rem;   /* 20px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
--space-20: 5rem;     /* 80px */
--space-24: 6rem;     /* 96px */
```

### Common Spacing Patterns

```css
/* Component Padding */
--padding-card: var(--space-6);          /* 24px */
--padding-modal: var(--space-8);         /* 32px */
--padding-button-sm: var(--space-2) var(--space-4);
--padding-button-md: var(--space-3) var(--space-6);
--padding-button-lg: var(--space-4) var(--space-8);

/* Section Spacing */
--spacing-section: var(--space-12);      /* 48px between sections */
--spacing-component: var(--space-6);     /* 24px between components */
--spacing-element: var(--space-4);       /* 16px between elements */

/* Container Widths */
--container-sm: 640px;
--container-md: 768px;
--container-lg: 1024px;
--container-xl: 1280px;
--container-2xl: 1536px;
```

### Layout Grid

```css
/* 12-column grid system */
.grid-container {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: var(--space-6);
  padding: var(--space-6);
}

/* Common Layouts */
.grid-2-col {
  grid-template-columns: repeat(2, 1fr);
}

.grid-3-col {
  grid-template-columns: repeat(3, 1fr);
}

.grid-4-col {
  grid-template-columns: repeat(4, 1fr);
}

/* Asymmetric Layouts */
.grid-sidebar {
  grid-template-columns: 250px 1fr;  /* Sidebar + Main */
}

.grid-detail {
  grid-template-columns: 2fr 1fr;    /* Main + Detail Panel */
}
```

---

## 5. Components Library

### 5.1 Buttons

#### Primary Button
```jsx
<button className="
  px-6 py-3 
  bg-primary-600 
  text-white 
  font-medium 
  rounded-lg 
  hover:bg-primary-700 
  active:bg-primary-800
  focus:outline-none 
  focus:ring-2 
  focus:ring-primary-500 
  focus:ring-offset-2
  disabled:bg-neutral-300 
  disabled:cursor-not-allowed
  transition-colors 
  duration-200
">
  Create Transaction
</button>
```

**Variants:**
- **Secondary:** `bg-white border-2 border-neutral-300 text-neutral-700`
- **Ghost:** `bg-transparent text-primary-600 hover:bg-primary-50`
- **Danger:** `bg-error-600 hover:bg-error-700`
- **Success:** `bg-success-600 hover:bg-success-700`

**Sizes:**
- **Small:** `px-4 py-2 text-sm`
- **Medium (default):** `px-6 py-3 text-base`
- **Large:** `px-8 py-4 text-lg`

#### Icon Button
```jsx
<button className="
  p-2 
  rounded-lg 
  text-neutral-600 
  hover:bg-neutral-100 
  hover:text-neutral-900
  focus:outline-none 
  focus:ring-2 
  focus:ring-primary-500
  transition-colors 
  duration-200
">
  <Icon className="w-5 h-5" />
</button>
```

### 5.2 Cards

#### Standard Card
```jsx
<div className="
  bg-white 
  rounded-xl 
  border border-neutral-200 
  p-6 
  shadow-sm 
  hover:shadow-md 
  transition-shadow 
  duration-200
">
  <h3 className="text-lg font-semibold text-neutral-900 mb-4">
    Card Title
  </h3>
  <div className="text-neutral-700">
    Card content goes here
  </div>
</div>
```

#### Stat Card
```jsx
<div className="
  bg-white 
  rounded-xl 
  border border-neutral-200 
  p-6
">
  <div className="flex items-center justify-between mb-2">
    <span className="text-sm font-medium text-neutral-600">
      Total Income
    </span>
    <span className="p-2 bg-success-50 rounded-lg">
      <TrendingUpIcon className="w-5 h-5 text-success-600" />
    </span>
  </div>
  <div className="text-3xl font-semibold font-mono text-neutral-900">
    $12,450.00
  </div>
  <div className="mt-2 text-sm text-success-600 flex items-center gap-1">
    <ArrowUpIcon className="w-4 h-4" />
    <span>12.5% from last month</span>
  </div>
</div>
```

#### Transaction Card
```jsx
<div className="
  bg-white 
  border border-neutral-200 
  rounded-lg 
  p-4 
  hover:bg-neutral-50 
  cursor-pointer
  transition-colors
">
  <div className="flex items-center justify-between">
    <div className="flex items-center gap-3">
      <div className="p-2 bg-primary-50 rounded-lg">
        <ShoppingBagIcon className="w-5 h-5 text-primary-600" />
      </div>
      <div>
        <h4 className="font-medium text-neutral-900">Office Supplies</h4>
        <p className="text-sm text-neutral-500">Mar 12, 2026</p>
      </div>
    </div>
    <div className="text-right">
      <div className="font-semibold font-mono text-error-600">-$45.99</div>
      <span className="text-xs text-neutral-500">Business</span>
    </div>
  </div>
</div>
```

### 5.3 Forms

#### Text Input
```jsx
<div className="space-y-2">
  <label className="text-sm font-medium text-neutral-700">
    Transaction Title
  </label>
  <input
    type="text"
    className="
      w-full 
      px-4 py-3 
      border border-neutral-300 
      rounded-lg 
      text-neutral-900
      placeholder:text-neutral-400
      focus:outline-none 
      focus:ring-2 
      focus:ring-primary-500 
      focus:border-transparent
      disabled:bg-neutral-100 
      disabled:cursor-not-allowed
    "
    placeholder="Enter transaction title"
  />
  <p className="text-sm text-neutral-500">
    A brief description of the transaction
  </p>
</div>
```

#### Select Dropdown
```jsx
<div className="space-y-2">
  <label className="text-sm font-medium text-neutral-700">
    Category
  </label>
  <select className="
    w-full 
    px-4 py-3 
    border border-neutral-300 
    rounded-lg 
    text-neutral-900
    bg-white
    focus:outline-none 
    focus:ring-2 
    focus:ring-primary-500 
    focus:border-transparent
  ">
    <option>Select a category</option>
    <option>Food & Dining</option>
    <option>Transportation</option>
    <option>Shopping</option>
  </select>
</div>
```

#### Amount Input (Special)
```jsx
<div className="space-y-2">
  <label className="text-sm font-medium text-neutral-700">
    Amount
  </label>
  <div className="relative">
    <span className="absolute left-4 top-1/2 -translate-y-1/2 text-neutral-500 font-mono">
      $
    </span>
    <input
      type="number"
      step="0.01"
      className="
        w-full 
        pl-8 pr-4 py-3 
        border border-neutral-300 
        rounded-lg 
        text-neutral-900
        font-mono
        text-lg
        focus:outline-none 
        focus:ring-2 
        focus:ring-primary-500 
        focus:border-transparent
      "
      placeholder="0.00"
    />
  </div>
</div>
```

#### Date Picker
```jsx
<div className="space-y-2">
  <label className="text-sm font-medium text-neutral-700">
    Transaction Date
  </label>
  <input
    type="date"
    className="
      w-full 
      px-4 py-3 
      border border-neutral-300 
      rounded-lg 
      text-neutral-900
      focus:outline-none 
      focus:ring-2 
      focus:ring-primary-500 
      focus:border-transparent
    "
  />
</div>
```

#### Radio Group
```jsx
<div className="space-y-2">
  <label className="text-sm font-medium text-neutral-700">
    Transaction Type
  </label>
  <div className="flex gap-4">
    <label className="flex items-center gap-2 cursor-pointer">
      <input 
        type="radio" 
        name="type" 
        value="expense"
        className="w-4 h-4 text-primary-600 focus:ring-primary-500"
      />
      <span className="text-neutral-700">Expense</span>
    </label>
    <label className="flex items-center gap-2 cursor-pointer">
      <input 
        type="radio" 
        name="type" 
        value="income"
        className="w-4 h-4 text-primary-600 focus:ring-primary-500"
      />
      <span className="text-neutral-700">Income</span>
    </label>
  </div>
</div>
```

### 5.4 Badges & Tags

#### Status Badge
```jsx
<!-- Success -->
<span className="
  inline-flex 
  items-center 
  px-3 py-1 
  rounded-full 
  text-xs 
  font-medium 
  bg-success-50 
  text-success-700
">
  Paid
</span>

<!-- Warning -->
<span className="
  inline-flex 
  items-center 
  px-3 py-1 
  rounded-full 
  text-xs 
  font-medium 
  bg-warning-50 
  text-warning-700
">
  Pending
</span>

<!-- Error -->
<span className="
  inline-flex 
  items-center 
  px-3 py-1 
  rounded-full 
  text-xs 
  font-medium 
  bg-error-50 
  text-error-700
">
  Overdue
</span>
```

#### Category Tag
```jsx
<span className="
  inline-flex 
  items-center 
  gap-1 
  px-3 py-1 
  rounded-lg 
  text-sm 
  font-medium 
  bg-primary-50 
  text-primary-700
">
  <ShoppingBagIcon className="w-4 h-4" />
  Shopping
</span>
```

### 5.5 Navigation

#### Top Navigation Bar
```jsx
<nav className="
  bg-white 
  border-b border-neutral-200 
  px-6 py-4
">
  <div className="flex items-center justify-between max-w-7xl mx-auto">
    <div className="flex items-center gap-8">
      <div className="flex items-center gap-2">
        <Logo className="w-8 h-8 text-primary-600" />
        <span className="text-xl font-bold text-neutral-900">
          ExpenseTracker
        </span>
      </div>
      <div className="hidden md:flex items-center gap-6">
        <a href="/dashboard" className="text-neutral-700 hover:text-primary-600 font-medium">
          Dashboard
        </a>
        <a href="/transactions" className="text-neutral-700 hover:text-primary-600 font-medium">
          Transactions
        </a>
        <a href="/reports" className="text-neutral-700 hover:text-primary-600 font-medium">
          Reports
        </a>
      </div>
    </div>
    <div className="flex items-center gap-4">
      <button className="p-2 rounded-lg text-neutral-600 hover:bg-neutral-100">
        <BellIcon className="w-5 h-5" />
      </button>
      <button className="flex items-center gap-2">
        <img src="/avatar.jpg" className="w-8 h-8 rounded-full" />
      </button>
    </div>
  </div>
</nav>
```

#### Sidebar Navigation
```jsx
<aside className="
  w-64 
  bg-white 
  border-r border-neutral-200 
  h-screen 
  fixed 
  left-0 
  top-0
  p-6
">
  <div className="mb-8">
    <div className="flex items-center gap-2 mb-2">
      <Logo className="w-8 h-8 text-primary-600" />
      <span className="text-xl font-bold text-neutral-900">
        ExpenseTracker
      </span>
    </div>
  </div>
  
  <nav className="space-y-1">
    <a href="/dashboard" className="
      flex items-center gap-3 
      px-4 py-3 
      rounded-lg 
      bg-primary-50 
      text-primary-700 
      font-medium
    ">
      <DashboardIcon className="w-5 h-5" />
      Dashboard
    </a>
    <a href="/transactions" className="
      flex items-center gap-3 
      px-4 py-3 
      rounded-lg 
      text-neutral-700 
      hover:bg-neutral-50
      font-medium
    ">
      <TransactionIcon className="w-5 h-5" />
      Transactions
    </a>
    <a href="/projects" className="
      flex items-center gap-3 
      px-4 py-3 
      rounded-lg 
      text-neutral-700 
      hover:bg-neutral-50
      font-medium
    ">
      <FolderIcon className="w-5 h-5" />
      Projects
    </a>
  </nav>
</aside>
```

### 5.6 Modals & Dialogs

#### Modal Structure
```jsx
<div className="fixed inset-0 z-50 flex items-center justify-center">
  {/* Backdrop */}
  <div className="fixed inset-0 bg-black/50 backdrop-blur-sm" />
  
  {/* Modal */}
  <div className="
    relative 
    bg-white 
    rounded-xl 
    shadow-xl 
    max-w-lg 
    w-full 
    mx-4
    max-h-[90vh]
    overflow-hidden
  ">
    {/* Header */}
    <div className="px-6 py-4 border-b border-neutral-200">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-neutral-900">
          Create Transaction
        </h2>
        <button className="p-1 rounded-lg text-neutral-500 hover:bg-neutral-100">
          <XIcon className="w-5 h-5" />
        </button>
      </div>
    </div>
    
    {/* Body */}
    <div className="px-6 py-4 overflow-y-auto">
      Modal content goes here
    </div>
    
    {/* Footer */}
    <div className="px-6 py-4 border-t border-neutral-200 flex justify-end gap-3">
      <button className="px-4 py-2 text-neutral-700 hover:bg-neutral-100 rounded-lg">
        Cancel
      </button>
      <button className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700">
        Save
      </button>
    </div>
  </div>
</div>
```

### 5.7 Tables

#### Transaction Table
```jsx
<div className="bg-white rounded-xl border border-neutral-200 overflow-hidden">
  <table className="w-full">
    <thead className="bg-neutral-50 border-b border-neutral-200">
      <tr>
        <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
          Date
        </th>
        <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
          Description
        </th>
        <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
          Category
        </th>
        <th className="px-6 py-3 text-right text-xs font-medium text-neutral-500 uppercase tracking-wider">
          Amount
        </th>
        <th className="px-6 py-3 text-right text-xs font-medium text-neutral-500 uppercase tracking-wider">
          Actions
        </th>
      </tr>
    </thead>
    <tbody className="divide-y divide-neutral-200">
      <tr className="hover:bg-neutral-50">
        <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-600">
          Mar 12, 2026
        </td>
        <td className="px-6 py-4">
          <div className="text-sm font-medium text-neutral-900">
            Office Supplies
          </div>
          <div className="text-sm text-neutral-500">
            Printer paper and ink
          </div>
        </td>
        <td className="px-6 py-4 whitespace-nowrap">
          <span className="px-2 py-1 text-xs font-medium bg-primary-50 text-primary-700 rounded">
            Office
          </span>
        </td>
        <td className="px-6 py-4 whitespace-nowrap text-right">
          <span className="text-sm font-semibold font-mono text-error-600">
            -$45.99
          </span>
        </td>
        <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
          <button className="text-neutral-600 hover:text-primary-600">
            <MoreIcon className="w-5 h-5" />
          </button>
        </td>
      </tr>
    </tbody>
  </table>
</div>
```

### 5.8 Alerts & Notifications

#### Success Alert
```jsx
<div className="
  flex items-start gap-3 
  p-4 
  bg-success-50 
  border border-success-200 
  rounded-lg
">
  <CheckCircleIcon className="w-5 h-5 text-success-600 flex-shrink-0 mt-0.5" />
  <div className="flex-1">
    <h4 className="text-sm font-medium text-success-900">
      Transaction created successfully
    </h4>
    <p className="text-sm text-success-700 mt-1">
      Your expense has been recorded and reports have been updated.
    </p>
  </div>
  <button className="text-success-600 hover:text-success-700">
    <XIcon className="w-5 h-5" />
  </button>
</div>
```

#### Warning Alert
```jsx
<div className="
  flex items-start gap-3 
  p-4 
  bg-warning-50 
  border border-warning-200 
  rounded-lg
">
  <AlertIcon className="w-5 h-5 text-warning-600 flex-shrink-0 mt-0.5" />
  <div className="flex-1">
    <h4 className="text-sm font-medium text-warning-900">
      Budget threshold reached
    </h4>
    <p className="text-sm text-warning-700 mt-1">
      You've spent 80% of your monthly budget for "Dining Out".
    </p>
  </div>
</div>
```

#### Toast Notification
```jsx
<div className="
  fixed 
  bottom-4 
  right-4 
  z-50 
  bg-white 
  shadow-lg 
  rounded-lg 
  border border-neutral-200
  p-4
  min-w-[320px]
  animate-slide-up
">
  <div className="flex items-start gap-3">
    <CheckCircleIcon className="w-5 h-5 text-success-600 flex-shrink-0" />
    <div className="flex-1">
      <h4 className="text-sm font-medium text-neutral-900">
        Changes saved
      </h4>
      <p className="text-sm text-neutral-600 mt-1">
        Your transaction has been updated.
      </p>
    </div>
    <button className="text-neutral-400 hover:text-neutral-600">
      <XIcon className="w-5 h-5" />
    </button>
  </div>
</div>
```

---

## 6. Page Layouts

### 6.1 Dashboard Layout

```
┌─────────────────────────────────────────────────────────────┐
│  Top Navigation Bar                                         │
├──────────┬──────────────────────────────────────────────────┤
│          │                                                  │
│ Sidebar  │  Main Content Area                               │
│          │  ┌────────────────────────────────────────────┐  │
│ - Dash   │  │ Page Header                                │  │
│ - Trans  │  │ Dashboard                                  │  │
│ - Proj   │  └────────────────────────────────────────────┘  │
│ - Report │                                                  │
│ - Budget │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐          │
│ - Team   │  │Stat 1│ │Stat 2│ │Stat 3│ │Stat 4│          │
│          │  └──────┘ └──────┘ └──────┘ └──────┘          │
│          │                                                  │
│          │  ┌────────────────────────────────────────────┐  │
│          │  │ Chart: Income vs Expenses                  │  │
│          │  │                                            │  │
│          │  └────────────────────────────────────────────┘  │
│          │                                                  │
│          │  ┌──────────────────┐ ┌──────────────────────┐  │
│          │  │Recent            │ │Budget Status         │  │
│          │  │Transactions      │ │                      │  │
│          │  └──────────────────┘ └──────────────────────┘  │
└──────────┴──────────────────────────────────────────────────┘
```

### 6.2 Transaction List Layout

```
┌─────────────────────────────────────────────────────────────┐
│  Transactions                         [+ New Transaction]   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Filters: [All ▼] [Date Range] [Category] [Search...]      │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ Date   │ Description      │ Category │ Amount    │ ⋮│  │
│  ├─────────────────────────────────────────────────────┤  │
│  │ Mar 12 │ Office Supplies  │ Office   │ -$45.99   │ ⋮│  │
│  │ Mar 11 │ Client Lunch     │ Food     │ -$67.50   │ ⋮│  │
│  │ Mar 10 │ Monthly Salary   │ Income   │ +$5000.00 │ ⋮│  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  Pagination: [← Previous] [1] [2] [3] ... [Next →]         │
└─────────────────────────────────────────────────────────────┘
```

### 6.3 Create Transaction Modal

```
┌─────────────────────────────────────────┐
│ Create Transaction              [X]     │
├─────────────────────────────────────────┤
│                                         │
│ Transaction Type                        │
│ ○ Expense  ○ Income                     │
│                                         │
│ Title                                   │
│ [________________]                      │
│                                         │
│ Amount                                  │
│ $ [________________]                    │
│                                         │
│ Category                                │
│ [Select category ▼]                     │
│                                         │
│ Date                                    │
│ [Mar 12, 2026]                          │
│                                         │
│ Description (optional)                  │
│ [________________]                      │
│ [________________]                      │
│                                         │
│ Payment Method                          │
│ [Credit Card ▼]                         │
│                                         │
│ Attach Receipt                          │
│ [Upload File] or drag and drop          │
│                                         │
├─────────────────────────────────────────┤
│                 [Cancel]  [Save]        │
└─────────────────────────────────────────┘
```

---

## 7. Data Visualization

### 7.1 Chart Types

#### Line Chart - Spending Trends
```jsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

<LineChart width={600} height={300} data={data}>
  <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
  <XAxis 
    dataKey="month" 
    stroke="#6B7280"
    style={{ fontSize: '12px' }}
  />
  <YAxis 
    stroke="#6B7280"
    style={{ fontSize: '12px' }}
  />
  <Tooltip 
    contentStyle={{
      backgroundColor: '#FFFFFF',
      border: '1px solid #E5E7EB',
      borderRadius: '8px',
      padding: '12px'
    }}
  />
  <Legend />
  <Line 
    type="monotone" 
    dataKey="income" 
    stroke="#10B981" 
    strokeWidth={2}
    dot={{ fill: '#10B981', r: 4 }}
  />
  <Line 
    type="monotone" 
    dataKey="expenses" 
    stroke="#EF4444" 
    strokeWidth={2}
    dot={{ fill: '#EF4444', r: 4 }}
  />
</LineChart>
```

#### Bar Chart - Category Breakdown
```jsx
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

<BarChart width={600} height={300} data={data}>
  <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
  <XAxis dataKey="category" stroke="#6B7280" />
  <YAxis stroke="#6B7280" />
  <Tooltip />
  <Bar 
    dataKey="amount" 
    fill="#3B82F6" 
    radius={[8, 8, 0, 0]}
  />
</BarChart>
```

#### Pie Chart - Expense Distribution
```jsx
import { PieChart, Pie, Cell, Tooltip, Legend } from 'recharts';

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

<PieChart width={400} height={400}>
  <Pie
    data={data}
    cx={200}
    cy={200}
    labelLine={false}
    outerRadius={120}
    fill="#8884d8"
    dataKey="value"
  >
    {data.map((entry, index) => (
      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
    ))}
  </Pie>
  <Tooltip />
  <Legend />
</PieChart>
```

### 7.2 Progress Bars

#### Budget Progress
```jsx
<div className="space-y-2">
  <div className="flex justify-between text-sm">
    <span className="text-neutral-700 font-medium">Dining Out</span>
    <span className="text-neutral-600">$450 / $600</span>
  </div>
  <div className="h-2 bg-neutral-200 rounded-full overflow-hidden">
    <div 
      className="h-full bg-primary-600 rounded-full transition-all duration-300"
      style={{ width: '75%' }}
    />
  </div>
  <div className="text-xs text-neutral-500">
    75% of budget used
  </div>
</div>
```

#### Warning State (>80%)
```jsx
<div className="h-2 bg-neutral-200 rounded-full overflow-hidden">
  <div 
    className="h-full bg-warning-500 rounded-full"
    style={{ width: '85%' }}
  />
</div>
```

#### Exceeded State (>100%)
```jsx
<div className="h-2 bg-neutral-200 rounded-full overflow-hidden">
  <div 
    className="h-full bg-error-600 rounded-full"
    style={{ width: '100%' }}
  />
</div>
```

### 7.3 Mini Sparklines

```jsx
<div className="flex items-end gap-1 h-8">
  {data.map((value, index) => (
    <div 
      key={index}
      className="w-1 bg-primary-600 rounded-t"
      style={{ height: `${(value / maxValue) * 100}%` }}
    />
  ))}
</div>
```

---

## 8. Animations & Interactions

### 8.1 Transition Utilities

```css
/* Smooth transitions */
.transition-all {
  transition: all 0.2s ease-in-out;
}

.transition-colors {
  transition: color 0.2s ease-in-out, background-color 0.2s ease-in-out;
}

.transition-transform {
  transition: transform 0.2s ease-in-out;
}

/* Hover effects */
.hover-lift:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.hover-scale:hover {
  transform: scale(1.05);
}
```

### 8.2 Loading States

#### Skeleton Loader
```jsx
<div className="animate-pulse space-y-4">
  <div className="h-4 bg-neutral-200 rounded w-3/4" />
  <div className="h-4 bg-neutral-200 rounded" />
  <div className="h-4 bg-neutral-200 rounded w-5/6" />
</div>
```

#### Spinner
```jsx
<div className="animate-spin rounded-full h-8 w-8 border-4 border-neutral-200 border-t-primary-600" />
```

#### Button Loading State
```jsx
<button 
  disabled
  className="px-6 py-3 bg-primary-600 text-white rounded-lg opacity-50 cursor-not-allowed"
>
  <div className="flex items-center gap-2">
    <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
    <span>Saving...</span>
  </div>
</button>
```

### 8.3 Micro-interactions

#### Success Checkmark Animation
```css
@keyframes checkmark {
  0% {
    transform: scale(0);
    opacity: 0;
  }
  50% {
    transform: scale(1.2);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

.animate-checkmark {
  animation: checkmark 0.3s ease-in-out;
}
```

#### Slide In From Right
```css
@keyframes slide-in-right {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.animate-slide-in-right {
  animation: slide-in-right 0.3s ease-out;
}
```

---

## 9. Responsive Design

### 9.1 Breakpoints

```css
/* Tailwind default breakpoints */
sm: 640px   /* Small devices */
md: 768px   /* Tablets */
lg: 1024px  /* Laptops */
xl: 1280px  /* Desktops */
2xl: 1536px /* Large screens */
```

### 9.2 Mobile-First Approach

```jsx
{/* Stack cards on mobile, grid on desktop */}
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
  <StatCard />
  <StatCard />
  <StatCard />
  <StatCard />
</div>

{/* Hide sidebar on mobile, show on desktop */}
<aside className="hidden lg:block">
  <Sidebar />
</aside>

{/* Responsive text sizes */}
<h1 className="text-2xl md:text-3xl lg:text-4xl font-bold">
  Dashboard
</h1>

{/* Responsive padding */}
<div className="p-4 md:p-6 lg:p-8">
  Content
</div>
```

### 9.3 Mobile Navigation

```jsx
{/* Mobile hamburger menu */}
<button className="lg:hidden p-2">
  <MenuIcon className="w-6 h-6" />
</button>

{/* Mobile drawer */}
<div className="
  fixed inset-0 z-50 
  bg-white 
  transform transition-transform
  translate-x-0 lg:translate-x-full
">
  <nav className="p-6">
    {/* Mobile navigation links */}
  </nav>
</div>
```

---

## 10. Accessibility Guidelines

### 10.1 Color Contrast

- **Text:** Minimum 4.5:1 contrast ratio for normal text
- **Large Text:** Minimum 3:1 contrast ratio (18pt+ or 14pt+ bold)
- **UI Elements:** Minimum 3:1 contrast ratio for buttons, borders

### 10.2 Keyboard Navigation

```jsx
{/* Focusable elements */}
<button className="
  focus:outline-none 
  focus:ring-2 
  focus:ring-primary-500 
  focus:ring-offset-2
">
  Click me
</button>

{/* Skip to main content link */}
<a 
  href="#main-content" 
  className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4"
>
  Skip to main content
</a>
```

### 10.3 ARIA Labels

```jsx
{/* Button with icon only */}
<button aria-label="Delete transaction">
  <TrashIcon className="w-5 h-5" />
</button>

{/* Form inputs */}
<label htmlFor="amount" className="sr-only">
  Transaction amount
</label>
<input 
  id="amount"
  type="number"
  aria-describedby="amount-help"
/>
<p id="amount-help" className="text-sm text-neutral-500">
  Enter the transaction amount
</p>

{/* Loading state */}
<div role="status" aria-live="polite">
  <div className="animate-spin..." />
  <span className="sr-only">Loading...</span>
</div>
```

### 10.4 Screen Reader Support

```jsx
{/* Amount with screen reader context */}
<span className="sr-only">Expense amount: </span>
<span aria-label="45 dollars and 99 cents">$45.99</span>

{/* Status messages */}
<div role="alert" aria-live="assertive">
  Transaction saved successfully
</div>
```

---

## 11. Implementation Guide

### 11.1 Tech Stack

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.10.0",
    "tailwindcss": "^3.3.0",
    "@headlessui/react": "^1.7.0",
    "@heroicons/react": "^2.0.0",
    "recharts": "^2.5.0",
    "date-fns": "^2.29.0",
    "axios": "^1.3.0",
    "react-query": "^3.39.0",
    "zustand": "^4.3.0"
  }
}
```

### 11.2 Project Structure

```
src/
├── components/
│   ├── ui/
│   │   ├── Button.jsx
│   │   ├── Card.jsx
│   │   ├── Input.jsx
│   │   ├── Modal.jsx
│   │   └── ...
│   ├── layout/
│   │   ├── Navbar.jsx
│   │   ├── Sidebar.jsx
│   │   └── Layout.jsx
│   ├── features/
│   │   ├── transactions/
│   │   │   ├── TransactionList.jsx
│   │   │   ├── TransactionCard.jsx
│   │   │   └── CreateTransactionModal.jsx
│   │   ├── dashboard/
│   │   │   ├── StatCard.jsx
│   │   │   ├── SpendingChart.jsx
│   │   │   └── RecentTransactions.jsx
│   │   └── ...
├── pages/
│   ├── Dashboard.jsx
│   ├── Transactions.jsx
│   ├── Projects.jsx
│   └── Reports.jsx
├── hooks/
│   ├── useTransactions.js
│   ├── useProjects.js
│   └── ...
├── utils/
│   ├── formatters.js
│   ├── api.js
│   └── ...
├── styles/
│   └── globals.css
└── App.jsx
```

### 11.3 Tailwind Configuration

```js
// tailwind.config.js
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#EFF6FF',
          100: '#DBEAFE',
          200: '#BFDBFE',
          300: '#93C5FD',
          400: '#60A5FA',
          500: '#3B82F6',
          600: '#2563EB',
          700: '#1D4ED8',
          800: '#1E40AF',
          900: '#1E3A8A',
        },
        // Add other custom colors
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['SF Mono', 'Monaco', 'monospace'],
      },
      boxShadow: {
        'sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        'md': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
        'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
        'xl': '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
```

### 11.4 Reusable Component Example

```jsx
// components/ui/Button.jsx
import { forwardRef } from 'react';
import { cn } from '@/utils/cn';

const variants = {
  primary: 'bg-primary-600 text-white hover:bg-primary-700',
  secondary: 'bg-white border-2 border-neutral-300 text-neutral-700 hover:bg-neutral-50',
  ghost: 'bg-transparent text-primary-600 hover:bg-primary-50',
  danger: 'bg-error-600 text-white hover:bg-error-700',
};

const sizes = {
  sm: 'px-4 py-2 text-sm',
  md: 'px-6 py-3 text-base',
  lg: 'px-8 py-4 text-lg',
};

const Button = forwardRef(({ 
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

export default Button;
```

### 11.5 Utility Functions

```js
// utils/formatters.js

// Format currency
export const formatCurrency = (amount, currency = 'USD') => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  }).format(amount);
};

// Format date
export const formatDate = (date, format = 'MMM dd, yyyy') => {
  return format(new Date(date), format);
};

// Calculate percentage
export const calculatePercentage = (value, total) => {
  if (total === 0) return 0;
  return ((value / total) * 100).toFixed(1);
};

// Get amount color class
export const getAmountColor = (type) => {
  return type === 'income' ? 'text-success-600' : 'text-error-600';
};
```

---

## Design Checklist

### Before Development
- [ ] Review and approve color palette
- [ ] Choose primary font (Inter recommended)
- [ ] Set up Tailwind CSS configuration
- [ ] Install necessary dependencies
- [ ] Create component library structure

### During Development
- [ ] Use consistent spacing (4px base unit)
- [ ] Apply proper color contrast ratios
- [ ] Implement responsive breakpoints
- [ ] Add loading states to all async actions
- [ ] Include hover/focus states on interactive elements
- [ ] Test keyboard navigation
- [ ] Add ARIA labels where needed

### Before Launch
- [ ] Run accessibility audit (WCAG 2.1 AA)
- [ ] Test on mobile devices
- [ ] Verify all colors meet contrast requirements
- [ ] Check all interactive elements are keyboard accessible
- [ ] Test with screen readers
- [ ] Validate responsive design on all breakpoints

---

## Resources

### Design Tools
- **Figma:** For mockups and prototypes
- **Tailwind CSS Docs:** https://tailwindcss.com
- **Heroicons:** https://heroicons.com
- **Recharts:** https://recharts.org

### Inspiration
- **Stripe Dashboard:** Clean, professional design
- **Linear:** Modern, fast interface
- **Notion:** Card-based layouts
- **Airtable:** Data tables and grids

### Accessibility
- **WCAG Guidelines:** https://www.w3.org/WAI/WCAG21/quickref/
- **WebAIM Contrast Checker:** https://webaim.org/resources/contrastchecker/
- **ARIA Authoring Practices:** https://www.w3.org/WAI/ARIA/apg/

---

**Document Version:** 1.0  
**Last Updated:** March 27, 2026  
**Maintained By:** Frontend Team

This style guide is a living document and should be updated as the design system evolves.
