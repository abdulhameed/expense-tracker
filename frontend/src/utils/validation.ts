/**
 * Validate email format
 * @param email - Email address to validate
 * @returns True if valid, false otherwise
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Validate password strength
 * @param password - Password to validate
 * @returns Object with strength level and feedback
 */
export function validatePassword(
  password: string
): { isValid: boolean; strength: 'weak' | 'medium' | 'strong'; feedback: string[] } {
  const feedback: string[] = [];
  let score = 0;

  if (password.length < 8) {
    feedback.push('At least 8 characters required');
  } else {
    score++;
  }

  if (password.length < 12) {
    feedback.push('Consider using 12+ characters for better security');
  } else {
    score++;
  }

  if (!/[A-Z]/.test(password)) {
    feedback.push('Add uppercase letters');
  } else {
    score++;
  }

  if (!/[a-z]/.test(password)) {
    feedback.push('Add lowercase letters');
  } else {
    score++;
  }

  if (!/[0-9]/.test(password)) {
    feedback.push('Add numbers');
  } else {
    score++;
  }

  if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    feedback.push('Add special characters');
  } else {
    score++;
  }

  let strength: 'weak' | 'medium' | 'strong' = 'weak';
  if (score >= 4) strength = 'medium';
  if (score >= 5) strength = 'strong';

  return {
    isValid: password.length >= 8,
    strength,
    feedback,
  };
}

/**
 * Validate amount format
 * @param amount - Amount string to validate
 * @returns True if valid, false otherwise
 */
export function isValidAmount(amount: string): boolean {
  const amountRegex = /^\d+(\.\d{1,2})?$/;
  const numAmount = parseFloat(amount);
  return amountRegex.test(amount) && numAmount > 0;
}

/**
 * Validate date format
 * @param dateString - Date string to validate
 * @returns True if valid, false otherwise
 */
export function isValidDate(dateString: string): boolean {
  const date = new Date(dateString);
  return date instanceof Date && !isNaN(date.getTime());
}

/**
 * Validate URL format
 * @param url - URL string to validate
 * @returns True if valid, false otherwise
 */
export function isValidUrl(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}
