import { useState } from 'react';
import { Modal } from './Modal';
import { Button } from './Button';
import { Input } from './Input';
import { MemberRole } from '@/types/api';

export interface InviteMemberModalProps {
  isOpen: boolean;
  projectName: string;
  onClose: () => void;
  onInvite: (email: string, role: MemberRole) => Promise<void>;
  isLoading?: boolean;
  error?: string;
}

export function InviteMemberModal({
  isOpen,
  projectName,
  onClose,
  onInvite,
  isLoading = false,
  error,
}: InviteMemberModalProps) {
  const [email, setEmail] = useState('');
  const [role, setRole] = useState<MemberRole>('member');
  const [validationError, setValidationError] = useState('');
  const [submitError, setSubmitError] = useState(error || '');

  const validateEmail = (value: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(value);
  };

  const handleEmailChange = (value: string) => {
    setEmail(value);
    setValidationError('');
    setSubmitError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError('');
    setSubmitError('');

    // Validate
    if (!email.trim()) {
      setValidationError('Email is required');
      return;
    }

    if (!validateEmail(email)) {
      setValidationError('Please enter a valid email address');
      return;
    }

    try {
      await onInvite(email.trim(), role);
      // Success - reset form
      setEmail('');
      setRole('member');
      onClose();
    } catch (err) {
      setSubmitError(
        err instanceof Error ? err.message : 'Failed to send invitation'
      );
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Invite Team Member"
      description={`Invite a new member to the ${projectName} project`}
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Email Input */}
        <Input
          label="Email Address"
          type="email"
          value={email}
          onChange={(e) => handleEmailChange(e.target.value)}
          placeholder="member@example.com"
          error={validationError || submitError}
          disabled={isLoading}
          aria-invalid={!!(validationError || submitError)}
          aria-describedby={validationError || submitError ? 'email-error' : undefined}
        />

        {/* Role Selection */}
        <div>
          <label
            htmlFor="member-role"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Role
          </label>
          <select
            id="member-role"
            value={role}
            onChange={(e) => setRole(e.target.value as MemberRole)}
            disabled={isLoading}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:bg-gray-100"
            aria-label="Member role"
          >
            <option value="viewer">Viewer (read-only)</option>
            <option value="member">Member (create & edit)</option>
            <option value="admin">Admin (full access)</option>
          </select>
          <p className="mt-1 text-xs text-gray-600">
            {role === 'viewer' &&
              'Can view transactions and reports, but cannot make changes'}
            {role === 'member' &&
              'Can create and edit transactions, but cannot manage team or budget'}
            {role === 'admin' &&
              'Full access to all project features including team management'}
          </p>
        </div>

        {/* Error Message */}
        {(validationError || submitError) && (
          <div
            id="email-error"
            className="rounded-lg bg-red-50 border border-red-200 p-3"
            role="alert"
            aria-live="assertive"
          >
            <p className="text-sm text-red-800">{validationError || submitError}</p>
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-3 justify-end pt-4 border-t border-gray-200">
          <Button
            type="button"
            variant="ghost"
            onClick={onClose}
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            variant="primary"
            isLoading={isLoading}
            disabled={!email.trim() || isLoading}
          >
            Send Invitation
          </Button>
        </div>
      </form>
    </Modal>
  );
}
