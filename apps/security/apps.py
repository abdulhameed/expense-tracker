"""
Security application configuration.
"""
from django.apps import AppConfig


class SecurityConfig(AppConfig):
    """Configuration for security application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.security"
    verbose_name = "Security"

    def ready(self):
        """Initialize security app."""
        # Security utilities are ready
        pass
