# Try to import Celery app, but make it optional for local development
try:
    from .celery import app as celery_app  # noqa: F401
    __all__ = ("celery_app",)
except ImportError:
    # Celery not installed - running in local development mode
    __all__ = ()
