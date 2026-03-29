import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Button, Input, Card, Alert, Spinner } from '@/components';
import apiClient from '@/services/api';

export function ResetPassword() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get('token');

  const [formData, setFormData] = useState({
    password: '',
    password_confirm: '',
  });
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [tokenValid, setTokenValid] = useState(true);
  const [tokenChecking, setTokenChecking] = useState(true);

  // Verify token on mount
  useEffect(() => {
    const verifyToken = async () => {
      if (!token) {
        setTokenValid(false);
        setError('Reset token is missing. Please check your email link.');
        setTokenChecking(false);
        return;
      }

      try {
        // Optionally verify the token with the backend
        setTokenValid(true);
        setTokenChecking(false);
      } catch (err) {
        setTokenValid(false);
        setError('Reset token is invalid or has expired.');
        setTokenChecking(false);
      }
    };

    verifyToken();
  }, [token]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    if (validationErrors[name]) {
      setValidationErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
    setError('');
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!formData.password) {
      errors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      errors.password = 'Password must be at least 8 characters';
    }

    if (!formData.password_confirm) {
      errors.password_confirm = 'Please confirm your password';
    } else if (formData.password !== formData.password_confirm) {
      errors.password_confirm = 'Passwords do not match';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);
    try {
      await apiClient.post('/auth/password/confirm/', {
        token,
        password: formData.password,
        password_confirm: formData.password_confirm,
      });

      // Success - redirect to login
      navigate('/login', {
        state: {
          message: 'Password reset successful! Please log in with your new password.',
        },
      });
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          'Failed to reset password. Please try again or request a new reset link.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  if (tokenChecking) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          <Card className="shadow-xl">
            <div className="text-center">
              <Spinner size="large" />
              <p className="text-neutral-600 mt-4">Verifying reset link...</p>
            </div>
          </Card>
        </div>
      </div>
    );
  }

  if (!tokenValid) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          <Card className="shadow-xl">
            <div className="text-center">
              <div className="flex justify-center mb-6">
                <div className="w-16 h-16 bg-error-100 rounded-full flex items-center justify-center">
                  <svg
                    className="w-8 h-8 text-error-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </div>
              </div>
              <h1 className="text-2xl font-bold text-neutral-900 mb-4">
                Invalid or Expired Link
              </h1>
              <Alert variant="error" closeable={false}>
                {error}
              </Alert>
              <Button
                isFullWidth
                onClick={() => navigate('/forgot-password')}
                className="mt-6"
              >
                Request New Reset Link
              </Button>
            </div>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <Card className="shadow-xl">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-primary-900 mb-2">
              Create New Password
            </h1>
            <p className="text-neutral-600">
              Enter your new password below
            </p>
          </div>

          {/* Alert */}
          {error && (
            <Alert variant="error" closeable>
              {error}
            </Alert>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-5 mt-6" autoComplete="on">
            {/* Password Field */}
            <Input
              id="password"
              type="password"
              name="password"
              label="New Password"
              value={formData.password}
              onChange={handleChange}
              placeholder="At least 8 characters"
              autoComplete="new-password"
              disabled={isLoading}
              error={validationErrors.password}
              variant="password"
              helperText="Use a mix of letters, numbers, and symbols for security"
              required
            />

            {/* Confirm Password Field */}
            <Input
              id="password_confirm"
              type="password"
              name="password_confirm"
              label="Confirm Password"
              value={formData.password_confirm}
              onChange={handleChange}
              placeholder="Re-enter your password"
              autoComplete="new-password"
              disabled={isLoading}
              error={validationErrors.password_confirm}
              variant="password"
              required
            />

            {/* Submit Button */}
            <Button
              type="submit"
              isFullWidth
              isLoading={isLoading}
              disabled={isLoading}
            >
              Reset Password
            </Button>
          </form>

          {/* Footer */}
          <div className="mt-8 pt-6 border-t border-neutral-200 text-center">
            <p className="text-neutral-600 text-sm">
              Remember your password?{' '}
              <a
                href="/login"
                className="text-primary-600 hover:text-primary-700 font-semibold"
              >
                Sign in
              </a>
            </p>
          </div>
        </Card>
      </div>
    </div>
  );
}
