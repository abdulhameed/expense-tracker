import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import { Avatar } from './Avatar';

export function TopNav() {
  const { user, logout } = useAuthStore();
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
    <nav className="bg-white border-b border-neutral-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex justify-between items-center">
          {/* Logo */}
          <Link to="/dashboard" className="text-2xl font-bold text-primary-900 hover:text-primary-700">
            Expense Tracker
          </Link>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center gap-8">
            <Link
              to="/dashboard"
              className="text-neutral-600 hover:text-neutral-900 font-medium transition-colors"
            >
              Dashboard
            </Link>
            <Link
              to="/transactions"
              className="text-neutral-600 hover:text-neutral-900 font-medium transition-colors"
            >
              Transactions
            </Link>
            <Link
              to="/reports"
              className="text-neutral-600 hover:text-neutral-900 font-medium transition-colors"
            >
              Reports
            </Link>
          </div>

          {/* User Menu */}
          <div className="relative">
            <button
              onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
              className="flex items-center gap-3 p-2 rounded-lg hover:bg-neutral-100 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <Avatar
                initials={userInitials}
                alt={user ? `${user.first_name} ${user.last_name}` : 'User'}
                size="medium"
              />
              <div className="hidden sm:block text-left">
                <p className="text-sm font-medium text-neutral-900">
                  {user ? `${user.first_name} ${user.last_name}` : 'Guest'}
                </p>
                <p className="text-xs text-neutral-500">{user?.email}</p>
              </div>
            </button>

            {/* User Menu Dropdown */}
            {isUserMenuOpen && (
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-neutral-200 z-10">
                <Link
                  to="/settings"
                  className="block px-4 py-2 text-sm text-neutral-700 hover:bg-neutral-50 first:rounded-t-lg"
                  onClick={() => setIsUserMenuOpen(false)}
                >
                  Settings
                </Link>
                <Link
                  to="/profile"
                  className="block px-4 py-2 text-sm text-neutral-700 hover:bg-neutral-50"
                  onClick={() => setIsUserMenuOpen(false)}
                >
                  Profile
                </Link>
                <hr className="my-1" />
                <button
                  onClick={() => {
                    setIsUserMenuOpen(false);
                    handleLogout();
                  }}
                  className="block w-full text-left px-4 py-2 text-sm text-error-600 hover:bg-error-50 last:rounded-b-lg"
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
