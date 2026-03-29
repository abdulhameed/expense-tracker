import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemberPermissionsDisplay } from '../MemberPermissionsDisplay';
import { ProjectMember } from '@/types/api';

const mockMember: ProjectMember = {
  id: '123',
  user: '456',
  email: 'john@example.com',
  first_name: 'John',
  last_name: 'Doe',
  role: 'member',
  can_create_transactions: true,
  can_edit_transactions: true,
  can_delete_transactions: false,
  can_view_reports: true,
  can_invite_members: false,
  joined_at: '2026-03-01T10:00:00Z',
};

describe('MemberPermissionsDisplay', () => {
  it('does not render when member is null', () => {
    render(
      <MemberPermissionsDisplay
        member={null}
        isOpen={true}
        onClose={vi.fn()}
      />
    );

    expect(screen.queryByText(/Permissions/)).not.toBeInTheDocument();
  });

  it('renders member permissions when open', () => {
    render(
      <MemberPermissionsDisplay
        member={mockMember}
        isOpen={true}
        onClose={vi.fn()}
      />
    );

    expect(screen.getByText('John Doe - Permissions')).toBeInTheDocument();
    expect(screen.getByText('Role: MEMBER')).toBeInTheDocument();
  });

  it('shows granted permissions with checkmark', () => {
    render(
      <MemberPermissionsDisplay
        member={mockMember}
        isOpen={true}
        onClose={vi.fn()}
      />
    );

    expect(screen.getByText('Create Transactions')).toBeInTheDocument();
    expect(screen.getByText('Edit Transactions')).toBeInTheDocument();
    expect(screen.getByText('View Reports')).toBeInTheDocument();
  });

  it('shows denied permissions without checkmark', () => {
    render(
      <MemberPermissionsDisplay
        member={mockMember}
        isOpen={true}
        onClose={vi.fn()}
      />
    );

    expect(screen.getByText('Delete Transactions')).toBeInTheDocument();
    expect(screen.getByText('Invite Members')).toBeInTheDocument();
  });

  it('displays owner role description', () => {
    const ownerMember = { ...mockMember, role: 'owner' as const };

    render(
      <MemberPermissionsDisplay
        member={ownerMember}
        isOpen={true}
        onClose={vi.fn()}
      />
    );

    expect(screen.getByText('Role: OWNER')).toBeInTheDocument();
    expect(
      screen.getByText(/Full control of the project/)
    ).toBeInTheDocument();
  });

  it('displays viewer role description', () => {
    const viewerMember = { ...mockMember, role: 'viewer' as const };

    render(
      <MemberPermissionsDisplay
        member={viewerMember}
        isOpen={true}
        onClose={vi.fn()}
      />
    );

    expect(screen.getByText('Role: VIEWER')).toBeInTheDocument();
    expect(
      screen.getByText(/Can only view transactions and reports/)
    ).toBeInTheDocument();
  });

  it('displays member email and join date', () => {
    render(
      <MemberPermissionsDisplay
        member={mockMember}
        isOpen={true}
        onClose={vi.fn()}
      />
    );

    expect(screen.getByText(mockMember.email)).toBeInTheDocument();
    expect(screen.getByText(/Joined/)).toBeInTheDocument();
  });
});
