/**
 * Calculate sum of amounts
 * @param amounts - Array of amounts
 * @returns Sum of amounts
 */
export function calculateSum(amounts: number[]): number {
  return amounts.reduce((sum, amount) => sum + amount, 0);
}

/**
 * Calculate average of amounts
 * @param amounts - Array of amounts
 * @returns Average amount
 */
export function calculateAverage(amounts: number[]): number {
  if (amounts.length === 0) return 0;
  return calculateSum(amounts) / amounts.length;
}

/**
 * Calculate percentage of value relative to total
 * @param value - The value
 * @param total - The total
 * @returns Percentage (0-100)
 */
export function calculatePercentage(value: number, total: number): number {
  if (total === 0) return 0;
  return (value / total) * 100;
}

/**
 * Calculate difference and percentage change
 * @param currentValue - Current value
 * @param previousValue - Previous value
 * @returns Object with difference and percentage change
 */
export function calculateChange(currentValue: number, previousValue: number): {
  difference: number;
  percentageChange: number;
  isIncrease: boolean;
} {
  const difference = currentValue - previousValue;
  const percentageChange = previousValue === 0 ? 0 : (difference / previousValue) * 100;

  return {
    difference,
    percentageChange,
    isIncrease: difference > 0,
  };
}

/**
 * Round number to specified decimal places
 * @param num - Number to round
 * @param decimals - Number of decimal places (default: 2)
 * @returns Rounded number
 */
export function roundAmount(num: number, decimals = 2): number {
  return Math.round(num * Math.pow(10, decimals)) / Math.pow(10, decimals);
}

/**
 * Calculate monthly budget progress
 * @param spent - Amount spent
 * @param budget - Budget limit
 * @returns Object with spent, remaining, percentage
 */
export function calculateBudgetProgress(spent: number, budget: number): {
  spent: number;
  remaining: number;
  percentage: number;
  isOverBudget: boolean;
} {
  const remaining = Math.max(0, budget - spent);
  const percentage = calculatePercentage(spent, budget);
  const isOverBudget = spent > budget;

  return {
    spent,
    remaining,
    percentage: Math.min(100, percentage),
    isOverBudget,
  };
}

/**
 * Aggregate transactions by category
 * @param transactions - Array of transactions
 * @returns Object with category totals
 */
export function aggregateByCategory(
  transactions: Array<{ category: string; amount: number }>
): Record<string, number> {
  return transactions.reduce(
    (acc, transaction) => {
      acc[transaction.category] = (acc[transaction.category] || 0) + transaction.amount;
      return acc;
    },
    {} as Record<string, number>
  );
}

/**
 * Group transactions by date
 * @param transactions - Array of transactions
 * @returns Object with date keys and transaction arrays
 */
export function groupByDate(
  transactions: Array<{ date: string; [key: string]: any }>
): Record<string, Array<{ date: string; [key: string]: any }>> {
  return transactions.reduce(
    (acc, transaction) => {
      const date = transaction.date.split('T')[0]; // Get YYYY-MM-DD part
      if (!acc[date]) {
        acc[date] = [];
      }
      acc[date].push(transaction);
      return acc;
    },
    {} as Record<string, Array<{ date: string; [key: string]: any }>>
  );
}
