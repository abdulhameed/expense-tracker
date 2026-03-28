import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Alert } from '../Alert';

describe('Alert Component', () => {
  it('renders success variant', () => {
    const { container } = render(
      <Alert variant="success">Success message</Alert>
    );
    expect(screen.getByText('Success message')).toBeInTheDocument();
    const alert = container.firstChild;
    expect(alert).toHaveClass('bg-success-50');
  });

  it('renders warning variant', () => {
    const { container } = render(
      <Alert variant="warning">Warning message</Alert>
    );
    expect(screen.getByText('Warning message')).toBeInTheDocument();
    const alert = container.firstChild;
    expect(alert).toHaveClass('bg-warning-50');
  });

  it('renders error variant', () => {
    const { container } = render(
      <Alert variant="error">Error message</Alert>
    );
    expect(screen.getByText('Error message')).toBeInTheDocument();
    const alert = container.firstChild;
    expect(alert).toHaveClass('bg-error-50');
  });

  it('renders info variant by default', () => {
    const { container } = render(
      <Alert variant="info">Info message</Alert>
    );
    expect(screen.getByText('Info message')).toBeInTheDocument();
    const alert = container.firstChild;
    expect(alert).toHaveClass('bg-primary-50');
  });

  it('renders title when provided', () => {
    render(
      <Alert variant="success" title="Success!">
        Operation completed successfully
      </Alert>
    );
    expect(screen.getByText('Success!')).toBeInTheDocument();
    expect(screen.getByText('Operation completed successfully')).toBeInTheDocument();
  });

  it('renders close button when closeable is true', () => {
    render(
      <Alert variant="info" closeable>
        Alert message
      </Alert>
    );
    expect(screen.getByLabelText('Close notification')).toBeInTheDocument();
  });

  it('hides close button when closeable is false', () => {
    render(
      <Alert variant="info" closeable={false}>
        Alert message
      </Alert>
    );
    expect(screen.queryByLabelText('Close notification')).not.toBeInTheDocument();
  });

  it('hides alert when close button is clicked', async () => {
    const user = userEvent.setup();
    render(
      <Alert variant="info" closeable>
        Alert message
      </Alert>
    );

    const closeButton = screen.getByLabelText('Close notification');
    await user.click(closeButton);
    expect(screen.queryByText('Alert message')).not.toBeInTheDocument();
  });

  it('calls onClose callback when closed', async () => {
    const user = userEvent.setup();
    const handleClose = vi.fn();
    render(
      <Alert variant="info" closeable onClose={handleClose}>
        Alert message
      </Alert>
    );

    const closeButton = screen.getByLabelText('Close notification');
    await user.click(closeButton);
    expect(handleClose).toHaveBeenCalledOnce();
  });

  it('renders with proper ARIA role', () => {
    render(
      <Alert variant="info">
        Important message
      </Alert>
    );
    expect(screen.getByRole('alert')).toBeInTheDocument();
  });

  it('renders icon for each variant', () => {
    const { container: successContainer } = render(
      <Alert variant="success">Success</Alert>
    );
    expect(successContainer.querySelector('svg')).toBeInTheDocument();

    const { container: errorContainer } = render(
      <Alert variant="error">Error</Alert>
    );
    expect(errorContainer.querySelector('svg')).toBeInTheDocument();
  });
});
