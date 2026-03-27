"""
Health check URL configuration.
"""
from django.urls import path
from . import views

app_name = "health"

urlpatterns = [
    # Basic health check (for load balancers)
    path("health/", views.health_check, name="health"),
    # Kubernetes readiness probe
    path("readiness/", views.readiness_check, name="readiness"),
    # Kubernetes liveness probe
    path("liveness/", views.liveness_check, name="liveness"),
    # Metrics endpoint
    path("metrics/", views.metrics, name="metrics"),
]
