import { ProjectMember, MemberRole } from '@/types/api';
import { Modal } from './Modal';
import { CheckCircleIcon, XCircleIcon } from '@heroicons/react/20/solid';

export interface MemberPermissionsDisplayProps {
  member: ProjectMember | null;
  isOpen: boolean;
  onClose: () => void;
}

const ROLE_DESCRIPTIONS: Record<MemberRole, string> = {
  owner: 'Full control of the project. Can manage team members, edit settings, and perform all actions.',
  admin: 'Can manage team members, create/edit/delete transactions, and view reports.',
  member: 'Can create and edit transactions, view reports, but cannot manage team.',
  viewer: 'Can only view transactions and reports. Cannot make any changes.',
};

const PERMISSIONS = [
  { key: 'can_create_transactions', label: 'Create Transactions' },
  { key: 'can_edit_transactions', label: 'Edit Transactions' },
  { key: 'can_delete_transactions', label: 'Delete Transactions' },
  { key: 'can_view_reports', label: 'View Reports' },
  { key: 'can_invite_members', label: 'Invite Members' },
];

export function MemberPermissionsDisplay({
  member,
  isOpen,
  onClose,
}: MemberPermissionsDisplayProps) {
  if (!member) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`${member.first_name} ${member.last_name} - Permissions`}
    >
      <div className="space-y-6">
        {/* Role Description */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-medium text-blue-900 mb-1">Role: {member.role.toUpperCase()}</h4>
          <p className="text-sm text-blue-800">{ROLE_DESCRIPTIONS[member.role]}</p>
        </div>

        {/* Permission List */}
        <div>
          <h4 className="font-medium text-gray-900 mb-3">Detailed Permissions</h4>
          <div className="space-y-2">
            {PERMISSIONS.map(({ key, label }) => {
              const hasPermission = member[key as keyof ProjectMember];
              const isGranted = typeof hasPermission === 'boolean' && hasPermission;

              return (
                <div key={key} className="flex items-center gap-3 py-2 px-3 bg-gray-50 rounded">
                  {isGranted ? (
                    <CheckCircleIcon
                      className="h-5 w-5 text-green-600"
                      aria-hidden="true"
                    />
                  ) : (
                    <XCircleIcon
                      className="h-5 w-5 text-gray-400"
                      aria-hidden="true"
                    />
                  )}
                  <span className={isGranted ? 'text-gray-900' : 'text-gray-600'}>
                    {label}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Info */}
        <div className="text-xs text-gray-600 bg-gray-50 rounded p-3">
          <p>
            <strong>Email:</strong> {member.email}
          </p>
          <p>
            <strong>Joined:</strong> {new Date(member.joined_at).toLocaleDateString()}
          </p>
        </div>
      </div>
    </Modal>
  );
}
