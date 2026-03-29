import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import userEvent from '@testing-library/user-event';
import { Invitations } from '../Invitations';
import * as teamService from '@/services/team';

// Mock the services
vi.mock('@/services/team', () => ({
  teamService: {
    getPendingInvitations: vi.fn(),
    acceptInvitation: vi.fn(),
    declineInvitation: vi.fn(),
  },
}));

const mockInvitations = [
  {
    id: 'inv-1',
    project: 'proj-1',
    project_name: 'Marketing Project',
    email: 'user@example.com',
    role: 'member' as const,
    invited_by: 'owner-1',
    invited_by_email: 'owner@example.com',
    status: 'pending' as const,
    created_at: '2026-03-20T00:00:00Z',
    expires_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: 'inv-2',
    project: 'proj-2',
    project_name: 'Finance Project',
    email: 'user@example.com',
    role: 'admin' as const,
    invited_by: 'owner-2',
    invited_by_email: 'admin@example.com',
    status: 'pending' as const,
    created_at: '2026-03-25T00:00:00Z',
    expires_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
  },
];

describe('Invitations', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (teamService.getPendingInvitations as any).mockResolvedValue(
      mockInvitations
    );
  });

  const renderInvitations = () => {
    return render(
      <BrowserRouter>
        <Invitations />
      </BrowserRouter>
    );
  };

  it('displays page title', async () => {
    renderInvitations();

    await waitFor(() => {
      expect(screen.getByText('Project Invitations')).toBeInTheDocument();
    });
  });

  it('loads and displays pending invitations', async () => {
    renderInvitations();

    await waitFor(() => {
      expect(screen.getByText('Marketing Project')).toBeInTheDocument();
      expect(screen.getByText('Finance Project')).toBeInTheDocument();
    });
  });

  it('displays invitation count', async () => {
    renderInvitations();

    await waitFor(() => {
      expect(screen.getByText(/You have 2 pending invitations/)).toBeInTheDocument();
    });
  });

  it('displays inviter email', async () => {
    renderInvitations();

    await waitFor(() => {
      expect(screen.getByText(/owner@example.com/)).toBeInTheDocument();
      expect(screen.getByText(/admin@example.com/)).toBeInTheDocument();
    });
  });

  it('displays role badges', async () => {
    renderInvitations();

    await waitFor(() => {
      const roleBadges = screen.getAllByText('member');
      expect(roleBadges.length).toBeGreaterThan(0);
    });
  });

  it('displays empty state when no invitations', async () => {
    (teamService.getPendingInvitations as any).mockResolvedValue([]);

    renderInvitations();

    await waitFor(() => {
      expect(screen.getByText('No pending invitations')).toBeInTheDocument();
    });
  });

  it('calls acceptInvitation when accept button is clicked', async () => {
    const user = userEvent.setup();
    (teamService.acceptInvitation as any).mockResolvedValue({
      detail: 'Invitation accepted',
    });

    renderInvitations();

    await waitFor(() => {
      expect(screen.getByText('Marketing Project')).toBeInTheDocument();
    });

    const acceptButtons = screen.getAllByRole('button', { name: /accept/i });
    await user.click(acceptButtons[0]);

    // Click confirm in modal
    const confirmButton = screen.getByRole('button', { name: /Accept Invitation/i });
    await user.click(confirmButton);

    await waitFor(() => {
      expect(teamService.acceptInvitation).toHaveBeenCalledWith('inv-1');
    });
  });

  it('calls declineInvitation when decline button is clicked', async () => {
    const user = userEvent.setup();
    (teamService.declineInvitation as any).mockResolvedValue({
      detail: 'Invitation declined',
    });

    renderInvitations();

    await waitFor(() => {
      expect(screen.getByText('Marketing Project')).toBeInTheDocument();
    });

    const declineButtons = screen.getAllByRole('button', { name: /decline/i });
    await user.click(declineButtons[0]);

    await waitFor(() => {
      expect(teamService.declineInvitation).toHaveBeenCalledWith('inv-1');
    });
  });

  it('shows loading spinner initially', () => {
    (teamService.getPendingInvitations as any).mockImplementation(
      () => new Promise(() => {})
    );

    renderInvitations();

    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('shows error message when loading fails', async () => {
    (teamService.getPendingInvitations as any).mockRejectedValue(
      new Error('Failed to load invitations')
    );

    renderInvitations();

    await waitFor(() => {
      expect(screen.getByText(/Failed to load invitations/)).toBeInTheDocument();
    });
  });

  it('removes invitation from list after accepting', async () => {
    const user = userEvent.setup();
    (teamService.acceptInvitation as any).mockResolvedValue({
      detail: 'Invitation accepted',
    });

    renderInvitations();

    await waitFor(() => {
      expect(screen.getByText('Marketing Project')).toBeInTheDocument();
    });

    const acceptButtons = screen.getAllByRole('button', { name: /accept/i });
    await user.click(acceptButtons[0]);

    const confirmButton = screen.getByRole('button', { name: /Accept Invitation/i });
    await user.click(confirmButton);

    await waitFor(() => {
      expect(screen.queryByText('Marketing Project')).not.toBeInTheDocument();
    });
  });

  it('displays help information', async () => {
    renderInvitations();

    await waitFor(() => {
      expect(screen.getByText('About Project Invitations')).toBeInTheDocument();
      expect(screen.getByText(/Invitations expire after 7 days/)).toBeInTheDocument();
    });
  });

  it('marks expired invitations appropriately', async () => {
    const expiredInvitation = {
      ...mockInvitations[0],
      expires_at: new Date(Date.now() - 1000).toISOString(), // expired
    };

    (teamService.getPendingInvitations as any).mockResolvedValue([expiredInvitation]);

    renderInvitations();

    await waitFor(() => {
      expect(screen.getByText('Expired')).toBeInTheDocument();
    });
  });
});
