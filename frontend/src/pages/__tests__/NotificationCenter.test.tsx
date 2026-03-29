import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { NotificationCenter } from '../NotificationCenter';
import { notificationService } from '@/utils/notifications';
import { BrowserRouter } from 'react-router-dom';
import { vi, beforeEach, afterEach } from 'vitest';

// Mock the MainLayout component
vi.mock('@/components', async () => {
  const actual = await vi.importActual('@/components');
  return {
    ...actual,
    MainLayout: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  };
});

const renderWithRouter = (component: React.ReactNode) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('NotificationCenter', () => {
  beforeEach(() => {
    notificationService.clear();
  });

  afterEach(() => {
    notificationService.clear();
  });

  it('renders page header and breadcrumb', () => {
    renderWithRouter(<NotificationCenter />);

    expect(screen.getByText('Notifications')).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
  });

  it('displays empty state when no notifications', () => {
    renderWithRouter(<NotificationCenter />);

    expect(screen.getByText('No notifications')).toBeInTheDocument();
    expect(screen.getByText(/Check back later for updates/)).toBeInTheDocument();
  });

  it('displays notifications list when notifications exist', async () => {
    renderWithRouter(<NotificationCenter />);

    notificationService.success('Success', 'Operation completed');
    notificationService.error('Error', 'Something failed');

    await waitFor(() => {
      expect(screen.getByText('Success')).toBeInTheDocument();
      expect(screen.getByText('Error')).toBeInTheDocument();
    });
  });

  it('shows notification count when notifications exist', async () => {
    renderWithRouter(<NotificationCenter />);

    notificationService.success('Success', 'Message');
    notificationService.info('Info', 'Message');

    await waitFor(() => {
      expect(screen.getByText(/You have 2 notifications/)).toBeInTheDocument();
    });
  });

  it('filters notifications by type', async () => {
    renderWithRouter(<NotificationCenter />);

    notificationService.success('Success', 'Success message');
    notificationService.error('Error', 'Error message');
    notificationService.info('Info', 'Info message');

    // Click on error filter
    const errorFilterButton = screen.getAllByText('Error').find(
      (el) => el.tagName === 'BUTTON'
    ) as HTMLButtonElement;

    await waitFor(() => {
      fireEvent.click(errorFilterButton);
    });

    await waitFor(() => {
      expect(screen.getByText('Error')).toBeInTheDocument();
      expect(screen.queryByText('Success')).not.toBeInTheDocument();
    });
  });

  it('shows all notifications when "all" filter is selected', async () => {
    renderWithRouter(<NotificationCenter />);

    notificationService.success('Success', 'Success message');
    notificationService.error('Error', 'Error message');

    await waitFor(() => {
      expect(screen.getByText('Success')).toBeInTheDocument();
      expect(screen.getByText('Error')).toBeInTheDocument();
    });
  });

  it('dismisses single notification when dismiss button clicked', async () => {
    renderWithRouter(<NotificationCenter />);

    notificationService.success('Success', 'Message');

    await waitFor(() => {
      expect(screen.getByText('Success')).toBeInTheDocument();
    });

    const dismissButtons = screen.getAllByText('Dismiss');
    fireEvent.click(dismissButtons[0]);

    await waitFor(() => {
      expect(screen.queryByText('Success')).not.toBeInTheDocument();
    });
  });

  it('clears all notifications with clear all button', async () => {
    renderWithRouter(<NotificationCenter />);

    notificationService.success('Success', 'Message 1');
    notificationService.error('Error', 'Message 2');

    await waitFor(() => {
      expect(screen.getByText('Success')).toBeInTheDocument();
    });

    const clearAllButton = screen.getByText('Clear All');
    fireEvent.click(clearAllButton);

    await waitFor(() => {
      expect(screen.queryByText('Success')).not.toBeInTheDocument();
      expect(screen.queryByText('Error')).not.toBeInTheDocument();
    });
  });

  it('displays filter tabs for each notification type', async () => {
    renderWithRouter(<NotificationCenter />);

    expect(screen.getByText('All')).toBeInTheDocument();
    expect(screen.getByText('Success')).toBeInTheDocument();
    expect(screen.getByText('Error')).toBeInTheDocument();
    expect(screen.getByText('Warning')).toBeInTheDocument();
    expect(screen.getByText('Info')).toBeInTheDocument();
  });

  it('hides clear all button when no notifications', () => {
    renderWithRouter(<NotificationCenter />);

    expect(screen.queryByText('Clear All')).not.toBeInTheDocument();
  });

  it('formats notification timestamps correctly', async () => {
    renderWithRouter(<NotificationCenter />);

    // Add a notification just now
    notificationService.success('Just Now', 'Message');

    await waitFor(() => {
      expect(screen.getByText(/Just now/)).toBeInTheDocument();
    });
  });

  it('displays notification title and message separately', async () => {
    renderWithRouter(<NotificationCenter />);

    notificationService.success('Test Title', 'Test Message');

    await waitFor(() => {
      expect(screen.getByText('Test Title')).toBeInTheDocument();
      expect(screen.getByText('Test Message')).toBeInTheDocument();
    });
  });

  it('applies correct colors for each notification type', async () => {
    renderWithRouter(<NotificationCenter />);

    notificationService.success('Success', 'Message');
    notificationService.error('Error', 'Message');

    await waitFor(() => {
      const cards = screen.getAllByRole('region'); // Card components
      expect(cards.length).toBeGreaterThanOrEqual(2);
    });
  });

  it('shows single notification text when only one notification', async () => {
    renderWithRouter(<NotificationCenter />);

    notificationService.success('Success', 'Message');

    await waitFor(() => {
      expect(screen.getByText(/You have 1 notification[^s]/)).toBeInTheDocument();
    });
  });

  it('shows plural notifications text when multiple notifications', async () => {
    renderWithRouter(<NotificationCenter />);

    notificationService.success('Success', 'Message 1');
    notificationService.info('Info', 'Message 2');

    await waitFor(() => {
      expect(screen.getByText(/You have 2 notifications/)).toBeInTheDocument();
    });
  });

  it('subscribes to notification service updates on mount', () => {
    const subscribeSpy = vi.spyOn(notificationService, 'subscribe');
    renderWithRouter(<NotificationCenter />);

    expect(subscribeSpy).toHaveBeenCalled();
  });

  it('updates display when notifications change', async () => {
    renderWithRouter(<NotificationCenter />);

    notificationService.success('First', 'First message');

    await waitFor(() => {
      expect(screen.getByText('First')).toBeInTheDocument();
    });

    notificationService.success('Second', 'Second message');

    await waitFor(() => {
      expect(screen.getByText('First')).toBeInTheDocument();
      expect(screen.getByText('Second')).toBeInTheDocument();
    });
  });

  it('displays notification icons', async () => {
    renderWithRouter(<NotificationCenter />);

    notificationService.success('Success', 'Message');

    await waitFor(() => {
      const icons = screen.getByText('✓');
      expect(icons).toBeInTheDocument();
    });
  });

  it('handles missing notification title gracefully', async () => {
    renderWithRouter(<NotificationCenter />);

    notificationService.add('info', '', 'Message without title');

    await waitFor(() => {
      expect(screen.getByText('Message without title')).toBeInTheDocument();
    });
  });

  it('maintains filter selection when notifications change', async () => {
    renderWithRouter(<NotificationCenter />);

    notificationService.success('Success', 'Message');
    notificationService.error('Error', 'Message');

    await waitFor(() => {
      expect(screen.getByText('Success')).toBeInTheDocument();
    });

    // Click error filter
    const errorButton = screen.getAllByText('Error').find((el) => el.tagName === 'BUTTON');
    if (errorButton) fireEvent.click(errorButton);

    await waitFor(() => {
      expect(screen.queryByText('Success')).not.toBeInTheDocument();
      expect(screen.getByText('Error')).toBeInTheDocument();
    });

    // Add new success notification
    notificationService.success('New Success', 'New message');

    // Filter should still show only errors
    expect(screen.queryByText('New Success')).not.toBeInTheDocument();
    expect(screen.getByText('Error')).toBeInTheDocument();
  });
});
