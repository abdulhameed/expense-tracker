import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import { useThemeStore } from '@/store/themeStore';
import { Avatar } from './Avatar';

export function TopNav() {
  const { user, logout } = useAuthStore();
  const { theme, toggleTheme } = useThemeStore();
  const navigate = useNavigate();
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const userInitials = user ? `${user.first_name?.[0] || ''}${user.last_name?.[0] || ''}` : '?';

  return (
    <nav className="bg-white dark:bg-neutral-900 border-b border-neutral-200 dark:border-neutral-800 shadow-sm">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex justify-between items-center">
          {/* Logo */}
          <Link to="/dashboard" className="text-2xl font-bold text-primary-900 dark:text-primary-50 hover:text-primary-700 dark:hover:text-primary-100">
            Expense Tracker
          </Link>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center gap-8">
            <Link
              to="/dashboard"
              className="text-neutral-600 dark:text-neutral-300 hover:text-neutral-900 dark:hover:text-white font-medium transition-colors"
            >
              Dashboard
            </Link>
            <Link
              to="/transactions"
              className="text-neutral-600 dark:text-neutral-300 hover:text-neutral-900 dark:hover:text-white font-medium transition-colors"
            >
              Transactions
            </Link>
            <Link
              to="/reports"
              className="text-neutral-600 dark:text-neutral-300 hover:text-neutral-900 dark:hover:text-white font-medium transition-colors"
            >
              Reports
            </Link>

            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500"
              aria-label="Toggle theme"
              title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
            >
              {theme === 'light' ? (
                <svg className="w-5 h-5 text-neutral-600" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
                </svg>
              ) : (
                <svg className="w-5 h-5 text-neutral-300" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4.293 1.707a1 1 0 011.414-1.414l.707.707a1 1 0 11-1.414 1.414l-.707-.707zm2 2a1 1 0 011.414 1.414l-.707.707a1 1 0 11-1.414-1.414l.707-.707zM10 7a3 3 0 100 6 3 3 0 000-6zm-4.293-1.707a1 1 0 011.414 1.414l-.707.707a1 1 0 11-1.414-1.414l.707-.707zm2-2a1 1 0 011.414 1.414l-.707.707a1 1 0 01-1.414-1.414l.707-.707zM10 18a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zm4.293-1.707a1 1 0 011.414 1.414l-.707.707a1 1 0 11-1.414-1.414l.707-.707zm2-2a1 1 0 011.414 1.414l-.707.707a1 1 0 11-1.414-1.414l.707-.707zM3 10a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zm4.293-1.707a1 1 0 011.414 1.414l-.707.707a1 1 0 11-1.414-1.414l.707-.707zm2-2a1 1 0 011.414 1.414l-.707.707a1 1 0 01-1.414-1.414l.707-.707z" clipRule="evenodd" />
                </svg>
              )}
            </button>
          </div>

          {/* User Menu */}
          <div className="relative">
            <button
              onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
              className="flex items-center gap-3 p-2 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <Avatar
                initials={userInitials}
                alt={user ? `${user.first_name} ${user.last_name}` : 'User'}
                size="medium"
              />
              <div className="hidden sm:block text-left">
                <p className="text-sm font-medium text-neutral-900 dark:text-white">
                  {user ? `${user.first_name} ${user.last_name}` : 'Guest'}
                </p>
                <p className="text-xs text-neutral-500 dark:text-neutral-400">{user?.email}</p>
              </div>
            </button>

            {/* User Menu Dropdown */}
            {isUserMenuOpen && (
              <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-neutral-800 rounded-lg shadow-lg border border-neutral-200 dark:border-neutral-700 z-10">
                <Link
                  to="/settings"
                  className="block px-4 py-2 text-sm text-neutral-700 dark:text-neutral-300 hover:bg-neutral-50 dark:hover:bg-neutral-700 first:rounded-t-lg"
                  onClick={() => setIsUserMenuOpen(false)}
                >
                  Settings
                </Link>
                <Link
                  to="/profile"
                  className="block px-4 py-2 text-sm text-neutral-700 dark:text-neutral-300 hover:bg-neutral-50 dark:hover:bg-neutral-700"
                  onClick={() => setIsUserMenuOpen(false)}
                >
                  Profile
                </Link>
                <hr className="my-1 border-neutral-200 dark:border-neutral-700" />
                <button
                  onClick={() => {
                    setIsUserMenuOpen(false);
                    handleLogout();
                  }}
                  className="block w-full text-left px-4 py-2 text-sm text-error-600 dark:text-error-400 hover:bg-error-50 dark:hover:bg-neutral-700 last:rounded-b-lg"
                >
                  Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
