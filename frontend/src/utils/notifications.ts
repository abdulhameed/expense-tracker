// Simple notification system
export type NotificationType = 'success' | 'error' | 'info' | 'warning';

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  duration?: number;
  timestamp: number;
}

// Notification store (in production, use a state management library)
const notifications: Notification[] = [];
const listeners = new Set<(notifications: Notification[]) => void>();

export const notificationService = {
  /**
   * Subscribe to notification changes
   */
  subscribe(listener: (notifications: Notification[]) => void) {
    listeners.add(listener);
    return () => {
      listeners.delete(listener);
    };
  },

  /**
   * Notify all listeners
   */
  notify() {
    listeners.forEach(listener => listener([...notifications]));
  },

  /**
   * Add a notification
   */
  add(type: NotificationType, title: string, message: string, duration = 5000) {
    const id = Math.random().toString(36);
    const notification: Notification = {
      id,
      type,
      title,
      message,
      duration,
      timestamp: Date.now(),
    };

    notifications.push(notification);
    this.notify();

    // Auto-remove after duration
    if (duration > 0) {
      setTimeout(() => {
        this.remove(id);
      }, duration);
    }

    return id;
  },

  /**
   * Remove a notification
   */
  remove(id: string) {
    const index = notifications.findIndex(n => n.id === id);
    if (index !== -1) {
      notifications.splice(index, 1);
      this.notify();
    }
  },

  /**
   * Clear all notifications
   */
  clear() {
    notifications.length = 0;
    this.notify();
  },

  /**
   * Get all notifications
   */
  getAll() {
    return [...notifications];
  },

  /**
   * Show success notification
   */
  success(title: string, message: string, duration?: number) {
    return this.add('success', title, message, duration);
  },

  /**
   * Show error notification
   */
  error(title: string, message: string, duration?: number) {
    return this.add('error', title, message, duration);
  },

  /**
   * Show info notification
   */
  info(title: string, message: string, duration?: number) {
    return this.add('info', title, message, duration);
  },

  /**
   * Show warning notification
   */
  warning(title: string, message: string, duration?: number) {
    return this.add('warning', title, message, duration);
  },

  /**
   * Request browser notification (if permitted)
   */
  requestBrowserNotification(title: string, options: NotificationOptions = {}) {
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification(title, options);
    }
  },

  /**
   * Request permission for browser notifications
   */
  async requestPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
      const permission = await Notification.requestPermission();
      return permission === 'granted';
    }
    return Notification.permission === 'granted';
  },
};
