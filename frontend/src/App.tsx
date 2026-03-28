import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useEffect } from 'react';
import { useAuthStore } from '@/store/authStore';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { Login } from '@/pages/Login';
import { Register } from '@/pages/Register';
import { Dashboard } from '@/pages/Dashboard';
import { Transactions } from '@/pages/Transactions';
import { TransactionCreate } from '@/pages/TransactionCreate';
import { TransactionEdit } from '@/pages/TransactionEdit';
import { TransactionDetail } from '@/pages/TransactionDetail';
import { Categories } from '@/pages/Categories';
import { Reports } from '@/pages/Reports';
import { Analytics } from '@/pages/Analytics';
import { Budgets } from '@/pages/Budgets';
import { Export } from '@/pages/Export';
import { VerifyEmail } from '@/pages/VerifyEmail';
import { ForgotPassword } from '@/pages/ForgotPassword';
import { ResetPassword } from '@/pages/ResetPassword';

export default function App() {
  const { isAuthenticated, getCurrentUser } = useAuthStore();

  useEffect(() => {
    // Try to restore auth state on app load
    if (!isAuthenticated) {
      getCurrentUser();
    }
  }, [isAuthenticated, getCurrentUser]);

  return (
    <BrowserRouter>
      <Routes>
        {/* Auth Pages */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/verify-email" element={<VerifyEmail />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />

        {/* Protected Pages */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        {/* Transaction Pages */}
        <Route
          path="/transactions"
          element={
            <ProtectedRoute>
              <Transactions />
            </ProtectedRoute>
          }
        />
        <Route
          path="/transactions/new"
          element={
            <ProtectedRoute>
              <TransactionCreate />
            </ProtectedRoute>
          }
        />
        <Route
          path="/transactions/:id/edit"
          element={
            <ProtectedRoute>
              <TransactionEdit />
            </ProtectedRoute>
          }
        />
        <Route
          path="/transactions/:id"
          element={
            <ProtectedRoute>
              <TransactionDetail />
            </ProtectedRoute>
          }
        />

        {/* Category Pages */}
        <Route
          path="/categories"
          element={
            <ProtectedRoute>
              <Categories />
            </ProtectedRoute>
          }
        />

        {/* Reports & Analytics Pages */}
        <Route
          path="/reports"
          element={
            <ProtectedRoute>
              <Reports />
            </ProtectedRoute>
          }
        />
        <Route
          path="/analytics"
          element={
            <ProtectedRoute>
              <Analytics />
            </ProtectedRoute>
          }
        />

        {/* Budget Management Page */}
        <Route
          path="/budgets"
          element={
            <ProtectedRoute>
              <Budgets />
            </ProtectedRoute>
          }
        />

        {/* Data Export Page */}
        <Route
          path="/export"
          element={
            <ProtectedRoute>
              <Export />
            </ProtectedRoute>
          }
        />

        {/* Root redirect */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
