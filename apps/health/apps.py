"""
Health check application configuration.
"""
from django.apps import AppConfig


class HealthConfig(AppConfig):
    """Configuration for health check application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.health"
    verbose_name = "Health Checks"
