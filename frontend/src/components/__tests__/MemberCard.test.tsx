import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemberCard } from '../MemberCard';
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

describe('MemberCard', () => {
  it('renders member information', () => {
    render(
      <MemberCard
        member={mockMember}
        isOwner={false}
        canManageMembers={false}
      />
    );

    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('john@example.com')).toBeInTheDocument();
  });

  it('displays member role badge', () => {
    render(
      <MemberCard
        member={mockMember}
        isOwner={false}
        canManageMembers={false}
      />
    );

    expect(screen.getByText('Member')).toBeInTheDocument();
  });

  it('shows action buttons when canManageMembers is true', async () => {
    const onChangeRole = vi.fn();
    const onRemove = vi.fn();

    render(
      <MemberCard
        member={mockMember}
        isOwner={true}
        canManageMembers={true}
        onChangeRole={onChangeRole}
        onRemove={onRemove}
      />
    );

    const removeButton = screen.getByRole('button', { name: /remove/i });
    expect(removeButton).toBeInTheDocument();
  });

  it('calls onRemove when remove button is clicked', async () => {
    const user = userEvent.setup();
    const onRemove = vi.fn();

    render(
      <MemberCard
        member={mockMember}
        isOwner={true}
        canManageMembers={true}
        onRemove={onRemove}
      />
    );

    const removeButton = screen.getByRole('button', { name: /remove/i });
    await user.click(removeButton);

    expect(onRemove).toHaveBeenCalled();
  });

  it('shows owner indicator for project owner', () => {
    const ownerMember = { ...mockMember, role: 'owner' as const };

    render(
      <MemberCard
        member={ownerMember}
        isOwner={true}
        canManageMembers={true}
      />
    );

    expect(screen.getByText('Project Owner')).toBeInTheDocument();
  });

  it('displays permissions button when onViewPermissions is provided', async () => {
    const user = userEvent.setup();
    const onViewPermissions = vi.fn();

    render(
      <MemberCard
        member={mockMember}
        isOwner={false}
        canManageMembers={false}
        onViewPermissions={onViewPermissions}
      />
    );

    const permissionsButton = screen.getByRole('button', { name: /permissions/i });
    await user.click(permissionsButton);

    expect(onViewPermissions).toHaveBeenCalled();
  });
});
