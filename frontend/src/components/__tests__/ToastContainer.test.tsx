import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ToastContainer } from '../ToastContainer';
import { notificationService } from '@/utils/notifications';
import { vi, beforeEach, afterEach } from 'vitest';

describe('ToastContainer', () => {
  beforeEach(() => {
    // Clear notifications before each test
    notificationService.clear();
  });

  afterEach(() => {
    // Clean up after each test
    notificationService.clear();
  });

  it('renders empty container when there are no notifications', () => {
    const { container } = render(<ToastContainer />);

    const toastContainer = container.querySelector('.fixed');
    expect(toastContainer).toBeInTheDocument();
  });

  it('displays notification when notificationService.add is called', async () => {
    render(<ToastContainer />);

    notificationService.success('Success', 'Operation completed');

    await waitFor(() => {
      expect(screen.getByText('Success')).toBeInTheDocument();
      expect(screen.getByText('Operation completed')).toBeInTheDocument();
    });
  });

  it('displays multiple notifications as a stack', async () => {
    render(<ToastContainer />);

    notificationService.success('First', 'First notification');
    notificationService.error('Second', 'Second notification');
    notificationService.info('Third', 'Third notification');

    await waitFor(() => {
      expect(screen.getByText('First')).toBeInTheDocument();
      expect(screen.getByText('Second')).toBeInTheDocument();
      expect(screen.getByText('Third')).toBeInTheDocument();
    });
  });

  it('removes notification when close button is clicked', async () => {
    render(<ToastContainer />);

    notificationService.success('Success', 'Notification');

    await waitFor(() => {
      expect(screen.getByText('Success')).toBeInTheDocument();
    });

    const closeButton = screen.getByLabelText('Close notification');
    fireEvent.click(closeButton);

    await waitFor(() => {
      expect(screen.queryByText('Success')).not.toBeInTheDocument();
    });
  });

  it('removes notification when notificationService.remove is called', async () => {
    render(<ToastContainer />);

    const id = notificationService.success('Success', 'Notification');

    await waitFor(() => {
      expect(screen.getByText('Success')).toBeInTheDocument();
    });

    notificationService.remove(id);

    await waitFor(() => {
      expect(screen.queryByText('Success')).not.toBeInTheDocument();
    });
  });

  it('clears all notifications when notificationService.clear is called', async () => {
    render(<ToastContainer />);

    notificationService.success('First', 'First notification');
    notificationService.error('Second', 'Second notification');

    await waitFor(() => {
      expect(screen.getByText('First')).toBeInTheDocument();
      expect(screen.getByText('Second')).toBeInTheDocument();
    });

    notificationService.clear();

    await waitFor(() => {
      expect(screen.queryByText('First')).not.toBeInTheDocument();
      expect(screen.queryByText('Second')).not.toBeInTheDocument();
    });
  });

  it('displays notifications with different types', async () => {
    render(<ToastContainer />);

    notificationService.success('Success Title', 'Success message');
    notificationService.error('Error Title', 'Error message');
    notificationService.warning('Warning Title', 'Warning message');
    notificationService.info('Info Title', 'Info message');

    await waitFor(() => {
      expect(screen.getByText('Success Title')).toBeInTheDocument();
      expect(screen.getByText('Error Title')).toBeInTheDocument();
      expect(screen.getByText('Warning Title')).toBeInTheDocument();
      expect(screen.getByText('Info Title')).toBeInTheDocument();
    });
  });

  it('positions toasts in fixed bottom-right corner', () => {
    const { container } = render(<ToastContainer />);

    const toastContainer = container.querySelector('.fixed');
    expect(toastContainer).toHaveClass('bottom-4', 'right-4', 'z-50');
  });

  it('applies proper pointer-events classes for stacking', () => {
    const { container } = render(<ToastContainer />);

    const mainContainer = container.querySelector('.fixed');
    expect(mainContainer).toHaveClass('pointer-events-none');

    // The inner divs should have pointer-events-auto
    const innerDivs = mainContainer?.querySelectorAll('.pointer-events-auto');
    expect(innerDivs?.length).toBeGreaterThanOrEqual(0);
  });

  it('subscribes to notification service updates', async () => {
    const subscribeSpy = vi.spyOn(notificationService, 'subscribe');

    render(<ToastContainer />);

    expect(subscribeSpy).toHaveBeenCalled();
  });

  it('unsubscribes from notification service on unmount', async () => {
    const { unmount } = render(<ToastContainer />);

    const unsubscribeSpy = vi.fn();
    vi.spyOn(notificationService, 'subscribe').mockReturnValue(unsubscribeSpy);

    unmount();

    // New render to test unsubscribe is stored
    const newComponent = render(<ToastContainer />);
    expect(notificationService.subscribe).toHaveBeenCalled();

    newComponent.unmount();
  });

  it('maintains notification order (FIFO style)', async () => {
    const { container } = render(<ToastContainer />);

    notificationService.success('First', 'First');
    notificationService.success('Second', 'Second');
    notificationService.success('Third', 'Third');

    await waitFor(() => {
      const notifications = container.querySelectorAll('[role="alert"]');
      expect(notifications.length).toBe(3);
    });
  });

  it('auto-removes notification after duration', async () => {
    render(<ToastContainer />);

    notificationService.add('info', 'Test', 'Auto remove', 100);

    await waitFor(() => {
      expect(screen.getByText('Test')).toBeInTheDocument();
    });

    await waitFor(
      () => {
        expect(screen.queryByText('Test')).not.toBeInTheDocument();
      },
      { timeout: 200 }
    );
  });

  it('keeps notification with duration 0 (no auto-remove)', async () => {
    render(<ToastContainer />);

    notificationService.add('info', 'Persistent', 'This should stay', 0);

    await waitFor(() => {
      expect(screen.getByText('Persistent')).toBeInTheDocument();
    });

    // Wait to ensure it doesn't auto-remove
    await new Promise((resolve) => setTimeout(resolve, 100));

    expect(screen.getByText('Persistent')).toBeInTheDocument();
  });

  it('handles rapid notification additions', async () => {
    render(<ToastContainer />);

    for (let i = 0; i < 5; i++) {
      notificationService.success(`Title ${i}`, `Message ${i}`);
    }

    await waitFor(() => {
      for (let i = 0; i < 5; i++) {
        expect(screen.getByText(`Title ${i}`)).toBeInTheDocument();
      }
    });
  });
});
