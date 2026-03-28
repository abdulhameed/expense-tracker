import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Badge } from '../Badge';

describe('Badge Component', () => {
  it('renders badge with text', () => {
    render(<Badge>Success</Badge>);
    expect(screen.getByText('Success')).toBeInTheDocument();
  });

  it('renders success variant', () => {
    const { container } = render(
      <Badge variant="success">Success</Badge>
    );
    const badge = container.firstChild;
    expect(badge).toHaveClass('bg-success-100');
    expect(badge).toHaveClass('text-success-800');
  });

  it('renders warning variant', () => {
    const { container } = render(
      <Badge variant="warning">Warning</Badge>
    );
    const badge = container.firstChild;
    expect(badge).toHaveClass('bg-warning-100');
  });

  it('renders error variant', () => {
    const { container } = render(
      <Badge variant="error">Error</Badge>
    );
    const badge = container.firstChild;
    expect(badge).toHaveClass('bg-error-100');
  });

  it('renders info variant by default', () => {
    const { container } = render(
      <Badge variant="info">Info</Badge>
    );
    const badge = container.firstChild;
    expect(badge).toHaveClass('bg-primary-100');
  });

  it('renders with icon', () => {
    render(
      <Badge icon={<span data-testid="icon">✓</span>}>
        Done
      </Badge>
    );
    expect(screen.getByTestId('icon')).toBeInTheDocument();
  });

  it('renders remove button when onRemove is provided', () => {
    render(
      <Badge onRemove={vi.fn()}>
        Removable
      </Badge>
    );
    const button = screen.getByLabelText('Remove badge');
    expect(button).toBeInTheDocument();
  });

  it('calls onRemove when remove button is clicked', async () => {
    const user = userEvent.setup();
    const handleRemove = vi.fn();
    render(
      <Badge onRemove={handleRemove}>
        Removable
      </Badge>
    );

    const button = screen.getByLabelText('Remove badge');
    await user.click(button);
    expect(handleRemove).toHaveBeenCalledOnce();
  });

  it('does not render remove button when onRemove is not provided', () => {
    render(<Badge>Static</Badge>);
    expect(screen.queryByLabelText('Remove badge')).not.toBeInTheDocument();
  });

  it('applies inline-flex styling', () => {
    const { container } = render(<Badge>Badge</Badge>);
    const badge = container.firstChild;
    expect(badge).toHaveClass('inline-flex');
  });

  it('renders with proper spacing', () => {
    const { container } = render(<Badge>Badge</Badge>);
    const badge = container.firstChild;
    expect(badge).toHaveClass('px-3');
    expect(badge).toHaveClass('py-1');
  });
});
