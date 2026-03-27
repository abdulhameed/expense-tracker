"""
Gunicorn configuration for production deployment.

Usage:
    gunicorn -c config/gunicorn.py config.wsgi:application
"""
import multiprocessing
import os

# Server socket
bind = os.getenv("GUNICORN_BIND", "0.0.0.0:8000")
backlog = 2048
max_requests = 1000
max_requests_jitter = 100
timeout = 60
graceful_timeout = 30
keepalive = 2

# Worker processes
workers = int(os.getenv("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
worker_class = "sync"
worker_connections = 1000
threads = 1

# Logging
accesslog = "-"  # Log to stdout
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
errorlog = "-"  # Log to stderr
loglevel = "info"
capture_output = True

# Process naming
proc_name = "expense-tracker"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (configure these with environment variables if needed)
keyfile = os.getenv("GUNICORN_KEYFILE", None)
certfile = os.getenv("GUNICORN_CERTFILE", None)
ssl_version = "TLSv1_2"
cert_reqs = 2
ca_certs = None
suppress_ragged_eof = True
do_handshake_on_connect = True
ciphers = "TLSv1.2"

# Application
preload_app = True
default_proc_name = "expense-tracker"

# Server hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    print(f"Gunicorn server starting with {workers} workers")

def when_ready(server):
    """Called just after the server is started."""
    print("Gunicorn server is ready. Spawning workers")

def on_exit(server):
    """Called just before exiting Gunicorn."""
    print("Gunicorn server has stopped")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    pass

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    # Initialize worker-specific resources here
    pass

def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    pass

def worker_int(worker):
    """Called when a worker receives the INT signal."""
    worker.log.info("Worker received INT or QUIT signal")

def worker_abort(worker):
    """Called when a worker receives the SIGABRT signal."""
    worker.log.info("Worker received SIGABRT signal")

def child_exit(server, worker):
    """Called just after a worker has been exited."""
    pass

def server_int(server):
    """Called when a INT signal is received by Gunicorn."""
    pass

def changed(files):
    """Called when a code change is detected."""
    pass

# Performance tuning
raw_env = [
    "DJANGO_SETTINGS_MODULE=config.settings.production",
]
