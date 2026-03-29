import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { MainLayout } from '@/components/MainLayout';
import { MemberCard } from '@/components/MemberCard';
import { InviteMemberModal } from '@/components/InviteMemberModal';
import { MemberPermissionsDisplay } from '@/components/MemberPermissionsDisplay';
import { Button } from '@/components/Button';
import { Modal } from '@/components/Modal';
import { Spinner } from '@/components/Spinner';
import { Alert } from '@/components/Alert';
import { teamService } from '@/services/team';
import { useAuthStore } from '@/store/authStore';
import { ProjectMember, MemberRole, Project } from '@/types/api';
import { UserGroupIcon } from '@heroicons/react/24/outline';

export function TeamMembers() {
  const { projectId } = useParams<{ projectId: string }>();
  const { user } = useAuthStore();

  const [project, setProject] = useState<Project | null>(null);
  const [members, setMembers] = useState<ProjectMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Modals
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [showPermissionsModal, setShowPermissionsModal] = useState(false);
  const [showRemoveConfirm, setShowRemoveConfirm] = useState<string | null>(null);
  const [selectedMember, setSelectedMember] = useState<ProjectMember | null>(null);

  // Current user's membership
  const [userMembership, setUserMembership] = useState<ProjectMember | null>(null);

  // Load project and members
  useEffect(() => {
    if (!projectId) return;

    const loadData = async () => {
      setLoading(true);
      setError(null);

      try {
        // Load project
        const projectData = await teamService.getProject(projectId);
        setProject(projectData);

        // Load members
        const membersList = await teamService.getProjectMembers(projectId);
        setMembers(membersList);

        // Find current user's membership
        const userMember = membersList.find((m) => m.email === user?.email);
        setUserMembership(userMember || null);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : 'Failed to load team members'
        );
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [projectId, user?.email]);

  const canManageMembers = userMembership && (
    userMembership.role === 'owner' ||
    userMembership.role === 'admin' ||
    userMembership.can_invite_members
  );

  const handleInvite = async (email: string, role: MemberRole) => {
    if (!projectId) return;

    try {
      await teamService.inviteMember(projectId, { email, role });
      setShowInviteModal(false);
      setSuccessMessage(`Invitation sent to ${email}`);
      setTimeout(() => setSuccessMessage(null), 5000);
    } catch (err) {
      throw err;
    }
  };

  const handleChangeRole = async (memberId: string, newRole: MemberRole) => {
    if (!projectId || !userMembership) return;

    // Check permission
    if (!canManageMembers) {
      setError('You do not have permission to manage team members');
      return;
    }

    const memberToUpdate = members.find((m) => m.id === memberId);
    if (!memberToUpdate || memberToUpdate.role === 'owner') {
      setError('Cannot change the owner\'s role');
      return;
    }

    try {
      const updated = await teamService.updateProjectMember(projectId, memberId, {
        role: newRole,
      });

      setMembers((prev) =>
        prev.map((m) => (m.id === memberId ? updated : m))
      );

      setSuccessMessage(`Role updated to ${newRole}`);
      setTimeout(() => setSuccessMessage(null), 5000);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Failed to update member role'
      );
    }
  };

  const handleRemove = async (memberId: string) => {
    if (!projectId || !userMembership) return;

    // Check permission
    if (!canManageMembers) {
      setError('You do not have permission to manage team members');
      return;
    }

    const memberToRemove = members.find((m) => m.id === memberId);
    if (!memberToRemove || memberToRemove.role === 'owner') {
      setError('Cannot remove the project owner');
      return;
    }

    try {
      await teamService.removeProjectMember(projectId, memberId);
      setMembers((prev) => prev.filter((m) => m.id !== memberId));
      setShowRemoveConfirm(null);
      setSuccessMessage('Member removed from project');
      setTimeout(() => setSuccessMessage(null), 5000);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Failed to remove member'
      );
    }
  };

  if (loading) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center min-h-screen">
          <Spinner size="large" />
        </div>
      </MainLayout>
    );
  }

  if (!project) {
    return (
      <MainLayout>
        <div className="space-y-4">
          <h1 className="text-3xl font-bold text-gray-900">Team Members</h1>
          <Alert variant="error">Project not found</Alert>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="space-y-6 pb-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <UserGroupIcon className="h-8 w-8 text-blue-600" aria-hidden="true" />
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Team Members</h1>
              <p className="text-gray-600">{project.name}</p>
            </div>
          </div>

          {canManageMembers && (
            <Button
              variant="primary"
              onClick={() => setShowInviteModal(true)}
            >
              Invite Member
            </Button>
          )}
        </div>

        {/* Alerts */}
        {error && (
          <Alert
            variant="error"
            onClose={() => setError(null)}
          >
            {error}
          </Alert>
        )}

        {successMessage && (
          <Alert
            variant="success"
            onClose={() => setSuccessMessage(null)}
          >
            {successMessage}
          </Alert>
        )}

        {/* Members List */}
        {members.length === 0 ? (
          <div className="rounded-lg border border-dashed border-gray-300 bg-gray-50 p-8 text-center">
            <UserGroupIcon className="h-12 w-12 text-gray-400 mx-auto mb-3" aria-hidden="true" />
            <h3 className="text-lg font-medium text-gray-900 mb-1">No members yet</h3>
            <p className="text-gray-600">
              {canManageMembers
                ? 'Invite team members to collaborate on this project'
                : 'You are the only member of this project'}
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {members.map((member) => (
              <MemberCard
                key={member.id}
                member={member}
                isOwner={userMembership?.role === 'owner'}
                canManageMembers={!!canManageMembers && member.role !== 'owner'}
                onViewPermissions={() => {
                  setSelectedMember(member);
                  setShowPermissionsModal(true);
                }}
                onChangeRole={(newRole) => handleChangeRole(member.id, newRole)}
                onRemove={() => {
                  setSelectedMember(member);
                  setShowRemoveConfirm(member.id);
                }}
              />
            ))}
          </div>
        )}

        {/* Info Section */}
        <div className="rounded-lg bg-blue-50 border border-blue-200 p-4">
          <h3 className="font-medium text-blue-900 mb-2">Team Roles</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li><strong>Owner:</strong> Full control of the project</li>
            <li><strong>Admin:</strong> Can manage team and transactions</li>
            <li><strong>Member:</strong> Can create and edit transactions</li>
            <li><strong>Viewer:</strong> Can only view transactions and reports</li>
          </ul>
        </div>
      </div>

      {/* Invite Modal */}
      <InviteMemberModal
        isOpen={showInviteModal}
        projectName={project.name}
        onClose={() => setShowInviteModal(false)}
        onInvite={handleInvite}
      />

      {/* Permissions Modal */}
      <MemberPermissionsDisplay
        member={selectedMember}
        isOpen={showPermissionsModal}
        onClose={() => {
          setShowPermissionsModal(false);
          setSelectedMember(null);
        }}
      />

      {/* Remove Confirmation Modal */}
      {showRemoveConfirm && selectedMember && (
        <Modal
          isOpen={!!showRemoveConfirm}
          onClose={() => {
            setShowRemoveConfirm(null);
            setSelectedMember(null);
          }}
          title="Remove Team Member"
        >
          <div className="space-y-4">
            <p className="text-gray-700">
              Are you sure you want to remove <strong>{selectedMember.first_name} {selectedMember.last_name}</strong> from this project?
            </p>
            <p className="text-sm text-gray-600">
              They will no longer have access to this project and its transactions.
            </p>

            <div className="flex gap-3 justify-end pt-4 border-t border-gray-200">
              <Button
                variant="ghost"
                onClick={() => {
                  setShowRemoveConfirm(null);
                  setSelectedMember(null);
                }}
              >
                Cancel
              </Button>
              <Button
                variant="danger"
                onClick={() => handleRemove(showRemoveConfirm)}
              >
                Remove Member
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </MainLayout>
  );
}
