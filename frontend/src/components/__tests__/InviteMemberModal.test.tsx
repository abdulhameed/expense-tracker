import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { InviteMemberModal } from '../InviteMemberModal';

describe('InviteMemberModal', () => {
  it('renders when isOpen is true', () => {
    render(
      <InviteMemberModal
        isOpen={true}
        projectName="Test Project"
        onClose={vi.fn()}
        onInvite={vi.fn()}
      />
    );

    expect(screen.getByText('Invite Team Member')).toBeInTheDocument();
    expect(screen.getByText(/Test Project/)).toBeInTheDocument();
  });

  it('does not render when isOpen is false', () => {
    render(
      <InviteMemberModal
        isOpen={false}
        projectName="Test Project"
        onClose={vi.fn()}
        onInvite={vi.fn()}
      />
    );

    expect(screen.queryByText('Invite Team Member')).not.toBeInTheDocument();
  });

  it('calls onInvite with email and role', async () => {
    const user = userEvent.setup();
    const onInvite = vi.fn().mockResolvedValue(undefined);
    const onClose = vi.fn();

    render(
      <InviteMemberModal
        isOpen={true}
        projectName="Test Project"
        onClose={onClose}
        onInvite={onInvite}
      />
    );

    const emailInput = screen.getByPlaceholderText('member@example.com');
    await user.type(emailInput, 'test@example.com');

    const submitButton = screen.getByRole('button', { name: /send invitation/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(onInvite).toHaveBeenCalledWith('test@example.com', 'member');
      expect(onClose).toHaveBeenCalled();
    });
  });

  it('shows validation error for invalid email', async () => {
    const user = userEvent.setup();
    const onInvite = vi.fn();

    render(
      <InviteMemberModal
        isOpen={true}
        projectName="Test Project"
        onClose={vi.fn()}
        onInvite={onInvite}
      />
    );

    const emailInput = screen.getByPlaceholderText('member@example.com');
    await user.type(emailInput, 'invalid-email');

    const submitButton = screen.getByRole('button', { name: /send invitation/i });
    await user.click(submitButton);

    expect(screen.getByText('Please enter a valid email address')).toBeInTheDocument();
    expect(onInvite).not.toHaveBeenCalled();
  });

  it('shows error when email is empty', async () => {
    const user = userEvent.setup();
    const onInvite = vi.fn();

    render(
      <InviteMemberModal
        isOpen={true}
        projectName="Test Project"
        onClose={vi.fn()}
        onInvite={onInvite}
      />
    );

    const submitButton = screen.getByRole('button', { name: /send invitation/i });
    await user.click(submitButton);

    expect(screen.getByText('Email is required')).toBeInTheDocument();
    expect(onInvite).not.toHaveBeenCalled();
  });

  it('changes role when select is changed', async () => {
    const user = userEvent.setup();
    const onInvite = vi.fn().mockResolvedValue(undefined);

    render(
      <InviteMemberModal
        isOpen={true}
        projectName="Test Project"
        onClose={vi.fn()}
        onInvite={onInvite}
      />
    );

    const roleSelect = screen.getByLabelText('Member role');
    await user.selectOptions(roleSelect, 'admin');

    const emailInput = screen.getByPlaceholderText('member@example.com');
    await user.type(emailInput, 'test@example.com');

    const submitButton = screen.getByRole('button', { name: /send invitation/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(onInvite).toHaveBeenCalledWith('test@example.com', 'admin');
    });
  });

  it('calls onClose when cancel button is clicked', async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();

    render(
      <InviteMemberModal
        isOpen={true}
        projectName="Test Project"
        onClose={onClose}
        onInvite={vi.fn()}
      />
    );

    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    await user.click(cancelButton);

    expect(onClose).toHaveBeenCalled();
  });

  it('displays submit error when provided', () => {
    render(
      <InviteMemberModal
        isOpen={true}
        projectName="Test Project"
        onClose={vi.fn()}
        onInvite={vi.fn()}
        error="This email is already a member"
      />
    );

    expect(screen.getByText('This email is already a member')).toBeInTheDocument();
  });

  it('disables form when isLoading is true', () => {
    render(
      <InviteMemberModal
        isOpen={true}
        projectName="Test Project"
        onClose={vi.fn()}
        onInvite={vi.fn()}
        isLoading={true}
      />
    );

    const emailInput = screen.getByPlaceholderText('member@example.com');
    const submitButton = screen.getByRole('button', { name: /send invitation/i });

    expect(emailInput).toBeDisabled();
    expect(submitButton).toBeDisabled();
  });
});
