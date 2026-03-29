import { useEffect, useState } from 'react';
import { MainLayout } from '@/components/MainLayout';
import { Button } from '@/components/Button';
import { Modal } from '@/components/Modal';
import { Spinner } from '@/components/Spinner';
import { Alert } from '@/components/Alert';
import { Badge } from '@/components/Badge';
import { teamService } from '@/services/team';
import { Invitation } from '@/types/api';
import { CheckCircleIcon, ClockIcon } from '@heroicons/react/24/outline';

export function Invitations() {
  const [invitations, setInvitations] = useState<Invitation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [selectedInvitation, setSelectedInvitation] = useState<Invitation | null>(null);

  // Load invitations
  useEffect(() => {
    const loadInvitations = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await teamService.getPendingInvitations();
        setInvitations(data);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : 'Failed to load invitations'
        );
      } finally {
        setLoading(false);
      }
    };

    loadInvitations();
  }, []);

  const handleAccept = async (invitation: Invitation) => {
    try {
      await teamService.acceptInvitation(invitation.id);
      setInvitations((prev) =>
        prev.filter((inv) => inv.id !== invitation.id)
      );
      setSelectedInvitation(null);
      setSuccessMessage(`You have joined the "${invitation.project_name}" project!`);
      setTimeout(() => setSuccessMessage(null), 5000);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Failed to accept invitation'
      );
    }
  };

  const handleDecline = async (invitation: Invitation) => {
    try {
      await teamService.declineInvitation(invitation.id);
      setInvitations((prev) =>
        prev.filter((inv) => inv.id !== invitation.id)
      );
      setSelectedInvitation(null);
      setSuccessMessage('Invitation declined');
      setTimeout(() => setSuccessMessage(null), 5000);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Failed to decline invitation'
      );
    }
  };

  const isExpired = (expires_at: string) => {
    return new Date(expires_at) < new Date();
  };

  const getRoleBadgeColor = (role: string): 'success' | 'warning' | 'error' | 'info' => {
    switch (role) {
      case 'owner':
        return 'error';
      case 'admin':
        return 'warning';
      case 'member':
        return 'info';
      case 'viewer':
        return 'success';
      default:
        return 'info';
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

  return (
    <MainLayout>
      <div className="space-y-6 pb-8 max-w-4xl">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Project Invitations</h1>
          <p className="text-gray-600 mt-1">
            {invitations.length === 0
              ? 'You have no pending invitations'
              : `You have ${invitations.length} pending ${invitations.length === 1 ? 'invitation' : 'invitations'}`}
          </p>
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

        {/* Invitations List */}
        {invitations.length === 0 ? (
          <div className="rounded-lg border border-dashed border-gray-300 bg-gray-50 p-12 text-center">
            <CheckCircleIcon className="h-12 w-12 text-gray-400 mx-auto mb-3" aria-hidden="true" />
            <h3 className="text-lg font-medium text-gray-900 mb-1">No pending invitations</h3>
            <p className="text-gray-600">
              When someone invites you to a project, it will appear here
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {invitations.map((invitation) => {
              const expired = isExpired(invitation.expires_at);

              return (
                <div
                  key={invitation.id}
                  className="flex items-center justify-between rounded-lg border border-gray-200 bg-white p-4 hover:shadow-md transition-shadow"
                >
                  {/* Invitation Info */}
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-medium text-gray-900">
                        {invitation.project_name}
                      </h3>
                      <Badge variant={getRoleBadgeColor(invitation.role)}>
                        {invitation.role}
                      </Badge>
                      {expired && (
                        <Badge variant="error">Expired</Badge>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 mb-1">
                      Invited by <strong>{invitation.invited_by_email}</strong>
                    </p>
                    <p className="text-xs text-gray-500 flex items-center gap-1">
                      <ClockIcon className="h-3 w-3" aria-hidden="true" />
                      Expires {new Date(invitation.expires_at).toLocaleDateString()}
                    </p>
                  </div>

                  {/* Actions */}
                  {expired ? (
                    <div className="text-sm text-gray-500 font-medium">Expired</div>
                  ) : (
                    <div className="flex gap-2 ml-4">
                      <Button
                        variant="primary"
                        size="small"
                        onClick={() => {
                          setSelectedInvitation(invitation);
                          // Accept immediately
                          handleAccept(invitation);
                        }}
                      >
                        Accept
                      </Button>
                      <Button
                        variant="ghost"
                        size="small"
                        onClick={() => {
                          setSelectedInvitation(invitation);
                          // Decline immediately
                          handleDecline(invitation);
                        }}
                      >
                        Decline
                      </Button>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}

        {/* Help Section */}
        <div className="rounded-lg bg-blue-50 border border-blue-200 p-4">
          <h3 className="font-medium text-blue-900 mb-2">About Project Invitations</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Invitations expire after 7 days</li>
            <li>• You can only accept an invitation once</li>
            <li>• Once declined, you can ask the project owner to send a new invitation</li>
            <li>• Your role in the project is determined when you accept the invitation</li>
          </ul>
        </div>
      </div>

      {/* Accept Confirmation Modal */}
      {selectedInvitation && (
        <Modal
          isOpen={!!selectedInvitation}
          onClose={() => setSelectedInvitation(null)}
          title="Accept Invitation"
        >
          <div className="space-y-4">
            <div className="bg-blue-50 rounded p-4 border border-blue-200">
              <p className="text-blue-900">
                You are being invited to join <strong>{selectedInvitation.project_name}</strong> as a <strong>{selectedInvitation.role}</strong>.
              </p>
            </div>
            <p className="text-gray-700">
              Once you accept, you will have access to all project transactions and can collaborate with other team members.
            </p>

            <div className="flex gap-3 justify-end pt-4 border-t border-gray-200">
              <Button
                variant="ghost"
                onClick={() => setSelectedInvitation(null)}
              >
                Not Now
              </Button>
              <Button
                variant="primary"
                onClick={() => {
                  if (selectedInvitation) {
                    handleAccept(selectedInvitation);
                  }
                }}
              >
                Accept Invitation
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </MainLayout>
  );
}
