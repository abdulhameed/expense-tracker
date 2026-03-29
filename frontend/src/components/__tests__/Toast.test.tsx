import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Toast } from '../Toast';
import { Notification } from '@/utils/notifications';

describe('Toast', () => {
  const mockNotification: Notification = {
    id: 'test-1',
    type: 'success',
    title: 'Success!',
    message: 'Operation completed successfully',
    duration: 5000,
    timestamp: Date.now(),
  };

  it('renders notification with title and message', () => {
    const mockOnClose = vi.fn();
    render(<Toast notification={mockNotification} onClose={mockOnClose} />);

    expect(screen.getByText('Success!')).toBeInTheDocument();
    expect(screen.getByText('Operation completed successfully')).toBeInTheDocument();
  });

  it('renders different notification types with correct styling', () => {
    const mockOnClose = vi.fn();
    const errorNotification: Notification = {
      ...mockNotification,
      id: 'error-1',
      type: 'error',
      title: 'Error',
      message: 'Something went wrong',
    };

    const { container } = render(<Toast notification={errorNotification} onClose={mockOnClose} />);
    const toastDiv = container.querySelector('[role="alert"]');

    expect(toastDiv).toHaveClass('bg-error-600');
  });

  it('calls onClose when close button is clicked', async () => {
    const mockOnClose = vi.fn();
    render(<Toast notification={mockNotification} onClose={mockOnClose} />);

    const closeButton = screen.getByLabelText('Close notification');
    fireEvent.click(closeButton);

    expect(mockOnClose).toHaveBeenCalledWith('test-1');
  });

  it('auto-closes after duration expires', async () => {
    const mockOnClose = vi.fn();
    const notification: Notification = {
      ...mockNotification,
      duration: 100,
    };

    const { container } = render(<Toast notification={notification} onClose={mockOnClose} />);

    // Initially should be visible
    expect(container.querySelector('[role="alert"]')).toBeInTheDocument();

    // After duration, onClose should be called
    await waitFor(
      () => {
        expect(mockOnClose).toHaveBeenCalledWith('test-1');
      },
      { timeout: 200 }
    );
  });

  it('does not auto-close when duration is 0 or not set', async () => {
    const mockOnClose = vi.fn();
    const notification: Notification = {
      ...mockNotification,
      duration: 0,
    };

    render(<Toast notification={notification} onClose={mockOnClose} />);

    await waitFor(
      () => {
        expect(mockOnClose).not.toHaveBeenCalled();
      },
      { timeout: 100 }
    );
  });

  it('renders notification without title when title is empty', () => {
    const mockOnClose = vi.fn();
    const notification: Notification = {
      ...mockNotification,
      title: '',
    };

    render(<Toast notification={notification} onClose={mockOnClose} />);

    expect(screen.getByText('Operation completed successfully')).toBeInTheDocument();
  });

  it('displays correct icon for each notification type', () => {
    const mockOnClose = vi.fn();
    const types: Notification['type'][] = ['success', 'error', 'warning', 'info'];

    types.forEach((type) => {
      const { container } = render(
        <Toast
          notification={{
            ...mockNotification,
            id: `${type}-icon`,
            type,
          }}
          onClose={mockOnClose}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();
    });
  });

  it('has proper accessibility attributes', () => {
    const mockOnClose = vi.fn();
    const { container } = render(<Toast notification={mockNotification} onClose={mockOnClose} />);

    const toastDiv = container.querySelector('[role="alert"]');
    expect(toastDiv).toBeInTheDocument();

    const closeButton = screen.getByLabelText('Close notification');
    expect(closeButton).toBeInTheDocument();
  });

  it('applies animation classes for entry animation', () => {
    const mockOnClose = vi.fn();
    const { container } = render(<Toast notification={mockNotification} onClose={mockOnClose} />);

    const toastDiv = container.querySelector('[role="alert"]');
    expect(toastDiv).toHaveClass('animate-in', 'fade-in', 'slide-in-from-right-2');
  });
});
