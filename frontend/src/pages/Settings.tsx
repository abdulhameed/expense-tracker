import { useState, useEffect } from 'react';
import { useAuthStore } from '@/store/authStore';
import { MainLayout, Card, Breadcrumb, Button, Input, Select, Toggle } from '@/components';

export function Settings() {
  const { user } = useAuthStore();

  // Preferences state
  const [preferences, setPreferences] = useState({
    currency: localStorage.getItem('currency') || 'USD',
    dateFormat: localStorage.getItem('dateFormat') || 'MM/DD/YYYY',
    theme: localStorage.getItem('theme') || 'light',
    notifications: localStorage.getItem('notifications') === 'true',
    emailReports: localStorage.getItem('emailReports') === 'true',
    budgetAlerts: localStorage.getItem('budgetAlerts') === 'true',
  });

  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (saved) {
      const timer = setTimeout(() => setSaved(false), 3000);
      return () => clearTimeout(timer);
    }
  }, [saved]);

  const handleSave = () => {
    localStorage.setItem('currency', preferences.currency);
    localStorage.setItem('dateFormat', preferences.dateFormat);
    localStorage.setItem('theme', preferences.theme);
    localStorage.setItem('notifications', preferences.notifications.toString());
    localStorage.setItem('emailReports', preferences.emailReports.toString());
    localStorage.setItem('budgetAlerts', preferences.budgetAlerts.toString());

    // Apply theme
    if (preferences.theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }

    setSaved(true);
  };

  return (
    <MainLayout>
      {/* Breadcrumb */}
      <Breadcrumb
        items={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Settings' },
        ]}
      />

      {/* Page Header */}
      <div className="mt-8 mb-8">
        <h1 className="text-3xl font-bold text-neutral-900">Settings</h1>
        <p className="text-neutral-600 mt-2">Manage your preferences and account settings</p>
      </div>

      {saved && (
        <div className="mb-8 p-4 bg-success-50 border border-success-200 rounded-lg">
          <p className="text-success-800 font-medium">✓ Settings saved successfully</p>
        </div>
      )}

      {/* User Profile Section */}
      <Card className="mb-8">
        <div>
          <h2 className="text-xl font-bold text-neutral-900 mb-6">Profile Information</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-2">Email</label>
              <Input value={user?.email || ''} disabled />
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-2">Member Since</label>
              <Input
                value={user?.created_at ? new Date(user.created_at).toLocaleDateString() : ''}
                disabled
              />
            </div>
          </div>
        </div>
      </Card>

      {/* Display Preferences */}
      <Card className="mb-8">
        <div>
          <h2 className="text-xl font-bold text-neutral-900 mb-6">Display Preferences</h2>
          <div className="space-y-4">
            <Select
              label="Currency"
              value={preferences.currency}
              onChange={(e) => setPreferences({ ...preferences, currency: e.target.value })}
              options={[
                { value: 'USD', label: 'USD ($)' },
                { value: 'EUR', label: 'EUR (€)' },
                { value: 'GBP', label: 'GBP (£)' },
                { value: 'JPY', label: 'JPY (¥)' },
                { value: 'CAD', label: 'CAD (C$)' },
                { value: 'AUD', label: 'AUD (A$)' },
              ]}
            />

            <Select
              label="Date Format"
              value={preferences.dateFormat}
              onChange={(e) => setPreferences({ ...preferences, dateFormat: e.target.value })}
              options={[
                { value: 'MM/DD/YYYY', label: 'MM/DD/YYYY' },
                { value: 'DD/MM/YYYY', label: 'DD/MM/YYYY' },
                { value: 'YYYY-MM-DD', label: 'YYYY-MM-DD' },
                { value: 'DD-MMM-YYYY', label: 'DD-MMM-YYYY' },
              ]}
            />

            <Select
              label="Theme"
              value={preferences.theme}
              onChange={(e) => setPreferences({ ...preferences, theme: e.target.value })}
              options={[
                { value: 'light', label: 'Light' },
                { value: 'dark', label: 'Dark' },
                { value: 'system', label: 'System' },
              ]}
            />
          </div>
        </div>
      </Card>

      {/* Notification Preferences */}
      <Card className="mb-8">
        <div>
          <h2 className="text-xl font-bold text-neutral-900 mb-6">Notifications</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 border border-neutral-200 rounded-lg">
              <div>
                <p className="font-medium text-neutral-900">Push Notifications</p>
                <p className="text-sm text-neutral-600">Receive browser notifications for budget alerts</p>
              </div>
              <div className="ml-4">
                <Toggle
                  checked={preferences.notifications}
                  onChange={(checked) => setPreferences({ ...preferences, notifications: checked })}
                />
              </div>
            </div>

            <div className="flex items-center justify-between p-4 border border-neutral-200 rounded-lg">
              <div>
                <p className="font-medium text-neutral-900">Email Reports</p>
                <p className="text-sm text-neutral-600">Receive weekly summary reports via email</p>
              </div>
              <div className="ml-4">
                <Toggle
                  checked={preferences.emailReports}
                  onChange={(checked) => setPreferences({ ...preferences, emailReports: checked })}
                />
              </div>
            </div>

            <div className="flex items-center justify-between p-4 border border-neutral-200 rounded-lg">
              <div>
                <p className="font-medium text-neutral-900">Budget Alerts</p>
                <p className="text-sm text-neutral-600">Get notified when approaching budget limits</p>
              </div>
              <div className="ml-4">
                <Toggle
                  checked={preferences.budgetAlerts}
                  onChange={(checked) => setPreferences({ ...preferences, budgetAlerts: checked })}
                />
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Account Actions */}
      <Card>
        <div>
          <h2 className="text-xl font-bold text-neutral-900 mb-6">Account Actions</h2>
          <div className="space-y-4">
            <Button className="w-full bg-error-50 text-error-600 hover:bg-error-100 border border-error-200">
              Change Password
            </Button>
            <Button className="w-full bg-error-50 text-error-600 hover:bg-error-100 border border-error-200">
              Delete Account
            </Button>
          </div>
        </div>
      </Card>

      {/* Save Button */}
      <div className="mt-8 flex justify-end gap-3">
        <Button className="px-6 py-2 bg-primary-600 text-white hover:bg-primary-700 rounded-lg" onClick={handleSave}>
          Save Settings
        </Button>
      </div>
    </MainLayout>
  );
}
