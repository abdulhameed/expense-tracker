import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import { Button, Input, Card, Alert, Checkbox } from '@/components';

export function Register() {
  const navigate = useNavigate();
  const { register, isLoading, error, clearError } = useAuthStore();
  const [formData, setFormData] = useState({
    email: '',
    first_name: '',
    last_name: '',
    password: '',
    password_confirm: '',
    agreeToTerms: false,
  });
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
    if (validationErrors[name]) {
      setValidationErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
    clearError();
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!formData.email) {
      errors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      errors.email = 'Please enter a valid email address';
    }

    if (!formData.first_name) {
      errors.first_name = 'First name is required';
    }

    if (!formData.last_name) {
      errors.last_name = 'Last name is required';
    }

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

    if (!formData.agreeToTerms) {
      errors.agreeToTerms = 'You must agree to the Terms of Service';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();

    if (!validateForm()) {
      return;
    }

    try {
      await register(
        formData.email,
        formData.first_name,
        formData.last_name,
        formData.password,
        formData.password_confirm
      );
      navigate('/dashboard');
    } catch (err) {
      console.error('Registration error:', err);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center p-4 py-8">
      <div className="w-full max-w-md">
        <Card className="shadow-xl">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-primary-900 mb-2">
              Expense Tracker
            </h1>
            <p className="text-neutral-600">Create your account</p>
          </div>

          {/* Alerts */}
          {error && (
            <Alert variant="error" closeable>
              {error}
            </Alert>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-5 mt-6">
            {/* Email Field */}
            <Input
              id="email"
              type="email"
              name="email"
              label="Email Address"
              value={formData.email}
              onChange={handleChange}
              placeholder="you@example.com"
              disabled={isLoading}
              error={validationErrors.email}
              required
            />

            {/* Name Fields */}
            <div className="grid grid-cols-2 gap-4">
              <Input
                id="first_name"
                type="text"
                name="first_name"
                label="First Name"
                value={formData.first_name}
                onChange={handleChange}
                placeholder="John"
                disabled={isLoading}
                error={validationErrors.first_name}
                required
              />
              <Input
                id="last_name"
                type="text"
                name="last_name"
                label="Last Name"
                value={formData.last_name}
                onChange={handleChange}
                placeholder="Doe"
                disabled={isLoading}
                error={validationErrors.last_name}
                required
              />
            </div>

            {/* Password Fields */}
            <Input
              id="password"
              type="password"
              name="password"
              label="Password"
              value={formData.password}
              onChange={handleChange}
              placeholder="At least 8 characters"
              disabled={isLoading}
              error={validationErrors.password}
              variant="password"
              helperText="Use a mix of letters, numbers, and symbols for security"
              required
            />

            <Input
              id="password_confirm"
              type="password"
              name="password_confirm"
              label="Confirm Password"
              value={formData.password_confirm}
              onChange={handleChange}
              placeholder="Re-enter your password"
              disabled={isLoading}
              error={validationErrors.password_confirm}
              variant="password"
              required
            />

            {/* Terms Agreement */}
            <div>
              <Checkbox
                id="agreeToTerms"
                name="agreeToTerms"
                label={
                  <span>
                    I agree to the{' '}
                    <a href="#" className="text-primary-600 hover:underline">
                      Terms of Service
                    </a>{' '}
                    and{' '}
                    <a href="#" className="text-primary-600 hover:underline">
                      Privacy Policy
                    </a>
                  </span>
                }
                checked={formData.agreeToTerms}
                onChange={handleChange}
                disabled={isLoading}
              />
              {validationErrors.agreeToTerms && (
                <p className="mt-1 text-sm text-error-600">{validationErrors.agreeToTerms}</p>
              )}
            </div>

            {/* Submit Button */}
            <Button
              type="submit"
              isFullWidth
              isLoading={isLoading}
              disabled={isLoading}
            >
              {isLoading ? 'Creating account...' : 'Create account'}
            </Button>
          </form>

          {/* Footer */}
          <div className="mt-8 pt-6 border-t border-neutral-200 text-center">
            <p className="text-neutral-600 text-sm">
              Already have an account?{' '}
              <Link
                to="/login"
                className="text-primary-600 hover:text-primary-700 font-semibold"
              >
                Sign in
              </Link>
            </p>
          </div>
        </Card>
      </div>
    </div>
  );
}
