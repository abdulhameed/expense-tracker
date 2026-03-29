import { ProjectMember, MemberRole } from '@/types/api';
import { Badge } from './Badge';
import { Button } from './Button';
import { Avatar } from './Avatar';

export interface MemberCardProps {
  member: ProjectMember;
  isOwner: boolean;
  canManageMembers: boolean;
  onChangeRole?: (newRole: MemberRole) => void;
  onRemove?: () => void;
  onViewPermissions?: () => void;
}

const ROLE_COLORS: Record<MemberRole, 'success' | 'warning' | 'error' | 'info'> = {
  owner: 'error',
  admin: 'warning',
  member: 'info',
  viewer: 'success',
};

const ROLE_LABELS: Record<MemberRole, string> = {
  owner: 'Owner',
  admin: 'Admin',
  member: 'Member',
  viewer: 'Viewer',
};

export function MemberCard({
  member,
  isOwner,
  canManageMembers,
  onChangeRole,
  onRemove,
  onViewPermissions,
}: MemberCardProps) {
  const isCurrentUserOwner = isOwner && member.role === 'owner';

  return (
    <div className="flex items-center justify-between rounded-lg border border-gray-200 bg-white p-4 hover:shadow-md transition-shadow">
      {/* Member Info */}
      <div className="flex items-center gap-3 flex-1">
        <Avatar
          initials={`${member.first_name[0]}${member.last_name[0]}`}
          size="medium"
          alt={`${member.first_name} ${member.last_name}`}
        />
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <h3 className="font-medium text-gray-900">
              {member.first_name} {member.last_name}
            </h3>
            <Badge variant={ROLE_COLORS[member.role]}>
              {ROLE_LABELS[member.role]}
            </Badge>
          </div>
          <p className="text-sm text-gray-600">{member.email}</p>
          <p className="text-xs text-gray-500">
            Joined {new Date(member.joined_at).toLocaleDateString()}
          </p>
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2 ml-4">
        {onViewPermissions && (
          <Button
            variant="ghost"
            size="small"
            onClick={onViewPermissions}
            aria-label={`View permissions for ${member.first_name} ${member.last_name}`}
          >
            Permissions
          </Button>
        )}

        {canManageMembers && !isCurrentUserOwner && (
          <>
            {onChangeRole && (
              <select
                value={member.role}
                onChange={(e) => onChangeRole(e.target.value as MemberRole)}
                className="rounded border border-gray-300 px-2 py-1 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                aria-label={`Change role for ${member.first_name} ${member.last_name}`}
                disabled={member.role === 'owner'}
              >
                <option value="viewer">Viewer</option>
                <option value="member">Member</option>
                <option value="admin">Admin</option>
              </select>
            )}

            {onRemove && (
              <Button
                variant="danger"
                size="small"
                onClick={onRemove}
                aria-label={`Remove ${member.first_name} ${member.last_name} from project`}
              >
                Remove
              </Button>
            )}
          </>
        )}

        {isCurrentUserOwner && (
          <span className="text-xs text-gray-500 font-medium">Project Owner</span>
        )}
      </div>
    </div>
  );
}
