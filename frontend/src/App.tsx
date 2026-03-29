import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useEffect } from 'react';
import { useAuthStore } from '@/store/authStore';
import { useThemeStore } from '@/store/themeStore';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { ToastContainer } from '@/components/ToastContainer';
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
import { RecurringTransactions } from '@/pages/RecurringTransactions';
import { Settings } from '@/pages/Settings';
import { DataImport } from '@/pages/DataImport';
import { NotificationCenter } from '@/pages/NotificationCenter';
import { VerifyEmail } from '@/pages/VerifyEmail';
import { ForgotPassword } from '@/pages/ForgotPassword';
import { ResetPassword } from '@/pages/ResetPassword';
import { TeamMembers } from '@/pages/TeamMembers';
import { Invitations } from '@/pages/Invitations';
import { Documents } from '@/pages/Documents';
import { ActivityLog } from '@/pages/ActivityLog';

export default function App() {
  const { isAuthenticated, getCurrentUser } = useAuthStore();
  const { initializeTheme } = useThemeStore();

  useEffect(() => {
    // Initialize theme on app load
    initializeTheme();
  }, [initializeTheme]);

  useEffect(() => {
    // Try to restore auth state on app load
    if (!isAuthenticated) {
      getCurrentUser();
    }
  }, [isAuthenticated, getCurrentUser]);

  return (
    <BrowserRouter>
      <ToastContainer />
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

        {/* Recurring Transactions Page */}
        <Route
          path="/recurring"
          element={
            <ProtectedRoute>
              <RecurringTransactions />
            </ProtectedRoute>
          }
        />

        {/* Settings Page */}
        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <Settings />
            </ProtectedRoute>
          }
        />

        {/* Data Import Page */}
        <Route
          path="/import"
          element={
            <ProtectedRoute>
              <DataImport />
            </ProtectedRoute>
          }
        />

        {/* Notification Center Page */}
        <Route
          path="/notifications"
          element={
            <ProtectedRoute>
              <NotificationCenter />
            </ProtectedRoute>
          }
        />

        {/* Document Management Page */}
        <Route
          path="/documents"
          element={
            <ProtectedRoute>
              <Documents />
            </ProtectedRoute>
          }
        />

        {/* Activity Log Page */}
        <Route
          path="/activity-log"
          element={
            <ProtectedRoute>
              <ActivityLog />
            </ProtectedRoute>
          }
        />

        {/* Team Collaboration Pages */}
        <Route
          path="/projects/:projectId/team"
          element={
            <ProtectedRoute>
              <TeamMembers />
            </ProtectedRoute>
          }
        />

        <Route
          path="/invitations"
          element={
            <ProtectedRoute>
              <Invitations />
            </ProtectedRoute>
          }
        />

        {/* Root redirect */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
