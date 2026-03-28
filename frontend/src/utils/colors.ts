/**
 * Get color class for transaction amount (green for income, red for expense)
 * @param amount - The amount
 * @param isIncome - Whether this is income (true) or expense (false)
 * @returns Color class name
 */
export function getAmountColor(amount: number, isIncome: boolean): string {
  if (isIncome || amount > 0) {
    return 'text-success-600';
  }
  return 'text-error-600';
}

/**
 * Get amount display string with appropriate sign
 * @param amount - The amount
 * @param isIncome - Whether this is income
 * @returns Amount string with sign
 */
export function formatAmountWithSign(amount: number, isIncome: boolean): string {
  const absoluteAmount = Math.abs(amount);
  if (isIncome || amount > 0) {
    return `+$${absoluteAmount.toFixed(2)}`;
  }
  return `-$${absoluteAmount.toFixed(2)}`;
}

/**
 * Get status badge color class
 * @param status - Status type
 * @returns Color class name
 */
export function getStatusColor(status: 'pending' | 'completed' | 'failed'): string {
  const colors: Record<string, string> = {
    pending: 'text-warning-600',
    completed: 'text-success-600',
    failed: 'text-error-600',
  };
  return colors[status] || 'text-neutral-600';
}

/**
 * Category color palette
 */
export const categoryColors = [
  '#3b82f6', // blue
  '#8b5cf6', // purple
  '#ec4899', // pink
  '#f59e0b', // amber
  '#10b981', // emerald
  '#06b6d4', // cyan
  '#6366f1', // indigo
  '#f97316', // orange
  '#ef4444', // red
  '#14b8a6', // teal
];

/**
 * Get color for category by index or name
 * @param categoryId - Category ID or index
 * @returns Hex color code
 */
export function getCategoryColor(categoryId: number | string): string {
  const index = typeof categoryId === 'number' ? categoryId : categoryId.charCodeAt(0);
  return categoryColors[index % categoryColors.length];
}

/**
 * Convert hex color to RGB
 * @param hex - Hex color code
 * @returns RGB color object
 */
export function hexToRgb(hex: string): { r: number; g: number; b: number } | null {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16),
      }
    : null;
}

/**
 * Get contrasting text color (black or white) based on background color
 * @param bgColor - Background hex color
 * @returns Text color class (text-black or text-white)
 */
export function getContrastingTextColor(bgColor: string): string {
  const rgb = hexToRgb(bgColor);
  if (!rgb) return 'text-white';

  const luminance = (0.299 * rgb.r + 0.587 * rgb.g + 0.114 * rgb.b) / 255;
  return luminance > 0.5 ? 'text-black' : 'text-white';
}
