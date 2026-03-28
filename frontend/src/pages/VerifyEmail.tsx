import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Card, Button, Alert, Spinner } from '@/components';
import apiClient from '@/services/api';

export function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('');

  const token = searchParams.get('token');

  useEffect(() => {
    const verifyEmail = async () => {
      if (!token) {
        setStatus('error');
        setMessage('Verification token is missing. Please check your email link.');
        return;
      }

      try {
        const response = await apiClient.post('/auth/verify-email/', { token });
        setStatus('success');
        setMessage(response.data.message || 'Your email has been verified successfully!');

        // Redirect to login after 3 seconds
        setTimeout(() => {
          navigate('/login');
        }, 3000);
      } catch (error: any) {
        setStatus('error');
        setMessage(
          error.response?.data?.detail ||
            'Email verification failed. Your token may have expired. Please request a new verification email.'
        );
      }
    };

    verifyEmail();
  }, [token, navigate]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <Card className="shadow-xl">
          <div className="text-center">
            {status === 'loading' && (
              <>
                <div className="flex justify-center mb-6">
                  <Spinner size="large" />
                </div>
                <h1 className="text-2xl font-bold text-neutral-900 mb-2">
                  Verifying Email
                </h1>
                <p className="text-neutral-600">
                  Please wait while we verify your email address...
                </p>
              </>
            )}

            {status === 'success' && (
              <>
                <div className="flex justify-center mb-6">
                  <div className="w-16 h-16 bg-success-100 rounded-full flex items-center justify-center">
                    <svg
                      className="w-8 h-8 text-success-600"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                  </div>
                </div>
                <h1 className="text-2xl font-bold text-neutral-900 mb-4">
                  Email Verified!
                </h1>
                <Alert variant="success" closeable={false}>
                  {message}
                </Alert>
                <p className="text-neutral-600 text-sm mt-6">
                  You will be redirected to the login page in a few seconds.
                </p>
                <Button
                  isFullWidth
                  onClick={() => navigate('/login')}
                  className="mt-6"
                >
                  Go to Login
                </Button>
              </>
            )}

            {status === 'error' && (
              <>
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
                  Verification Failed
                </h1>
                <Alert variant="error" closeable={false}>
                  {message}
                </Alert>
                <div className="flex gap-3 mt-6">
                  <Button
                    variant="secondary"
                    isFullWidth
                    onClick={() => navigate('/login')}
                  >
                    Back to Login
                  </Button>
                  <Button
                    isFullWidth
                    onClick={() => navigate('/register')}
                  >
                    Create New Account
                  </Button>
                </div>
              </>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
