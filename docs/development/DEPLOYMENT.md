# Deployment Guide

## Overview

This guide covers deploying the Expense Tracker API to production using Docker, Docker Compose, and cloud providers.

## Table of Contents

1. [Docker Deployment](#docker-deployment)
2. [Environment Configuration](#environment-configuration)
3. [Database Migrations](#database-migrations)
4. [Static Files & Media](#static-files--media)
5. [Reverse Proxy (Nginx)](#reverse-proxy-nginx)
6. [Health Checks](#health-checks)
7. [Monitoring & Logging](#monitoring--logging)
8. [Backup & Recovery](#backup--recovery)
9. [Scaling](#scaling)
10. [Troubleshooting](#troubleshooting)

---

## Docker Deployment

### Build Docker Image

```bash
# Build image for production
docker build -t expense-tracker-api:latest \
  --build-arg ENVIRONMENT=production \
  -f Dockerfile .

# Tag for registry
docker tag expense-tracker-api:latest \
  docker.io/username/expense-tracker-api:latest
```

### Multi-Stage Build

The Dockerfile uses a two-stage build process:

1. **Builder Stage**: Installs dependencies and builds virtual environment
2. **Runtime Stage**: Contains only necessary runtime dependencies

Benefits:
- Smaller final image size
- Faster deployments
- Better security (no build tools in production)

### Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild images
docker-compose up -d --build
```

### Docker Compose Services

1. **db** (PostgreSQL 16)
   - Database for application state
   - Persistent volume: `postgres_data`

2. **redis** (Redis 7)
   - Cache backend
   - Message broker for Celery
   - Persistent volume: `redis_data`

3. **web** (Django + Gunicorn)
   - Main application server
   - Port: 8000

4. **celery** (Celery Worker)
   - Asynchronous task processing
   - Concurrency: 4

5. **celery-beat** (Celery Beat)
   - Scheduled task scheduler
   - Manages periodic tasks

---

## Environment Configuration

### Environment Variables

Create `.env.production` file:

```bash
# Django
SECRET_KEY=your-secret-key-here (generate with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
DEBUG=False
ALLOWED_HOSTS=api.example.com,www.example.com
ENVIRONMENT=production

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=expense_tracker
DB_USER=expense_user
DB_PASSWORD=secure-password
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_URL=redis://:password@redis:6379/0
REDIS_PASSWORD=redis-password

# Email
DEFAULT_FROM_EMAIL=noreply@example.com
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=app-password
EMAIL_USE_TLS=True

# CORS
CORS_ALLOWED_ORIGINS=https://app.example.com,https://admin.example.com

# AWS S3 (optional)
USE_S3=True
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_STORAGE_BUCKET_NAME=expense-tracker-media
AWS_S3_REGION_NAME=us-east-1

# Sentry (error tracking)
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project

# API Keys
API_RATE_LIMIT_ENABLED=True
API_RATE_LIMIT_REQUESTS_PER_HOUR=100
```

### Secure Secrets

```bash
# Generate SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Generate secure password
openssl rand -base64 32
```

### Docker Secrets

For Swarm or Kubernetes:

```bash
# Create secret
echo "password" | docker secret create db_password -

# Use in service
docker service create \
  --secret db_password \
  -e DB_PASSWORD_FILE=/run/secrets/db_password \
  ...
```

---

## Database Migrations

### Running Migrations

```bash
# Via Docker Compose
docker-compose exec web python manage.py migrate

# Via Docker container
docker run --rm \
  --env-file .env.production \
  expense-tracker-api:latest \
  python manage.py migrate
```

### Migration Safety

```bash
# Check migrations before applying
docker-compose exec web python manage.py migrate --plan

# Show pending migrations
docker-compose exec web python manage.py showmigrations
```

### Backup Before Migration

```bash
# Dump database before migration
docker-compose exec db pg_dump -U expense_user expense_tracker > backup.sql

# Apply migrations
docker-compose exec web python manage.py migrate

# Rollback if needed
docker-compose exec db psql -U expense_user expense_tracker < backup.sql
```

### Zero-Downtime Deployments

```yaml
# docker-compose.yml strategy
services:
  web:
    # Run migrations in init container
    init: true
    entrypoint: |
      sh -c "python manage.py migrate --noinput && \
             python manage.py collectstatic --noinput && \
             gunicorn ..."
```

---

## Static Files & Media

### Collecting Static Files

```bash
# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# During build
RUN python manage.py collectstatic --noinput
```

### Storage Options

#### Local Storage
```python
# settings/production.py
STATIC_URL = '/static/'
STATIC_ROOT = '/app/staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = '/app/media'
```

#### AWS S3
```bash
pip install django-storages boto3

# In settings
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
```

### Docker Volume Mounting

```yaml
services:
  web:
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media

volumes:
  static_volume:
  media_volume:
```

### Nginx Serving

```nginx
location /static/ {
    alias /app/staticfiles/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}

location /media/ {
    alias /app/media/;
    expires 7d;
}
```

---

## Reverse Proxy (Nginx)

### Basic Setup

```bash
# Install Nginx
sudo apt-get install nginx

# Copy config
sudo cp config/nginx.conf /etc/nginx/sites-available/expense-tracker

# Enable site
sudo ln -s /etc/nginx/sites-available/expense-tracker /etc/nginx/sites-enabled/

# Test config
sudo nginx -t

# Start Nginx
sudo systemctl start nginx
```

### SSL/TLS with Let's Encrypt

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Generate certificate
sudo certbot certonly --nginx -d api.example.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### Performance Tuning

```nginx
# Gzip compression
gzip on;
gzip_types text/plain text/css application/json;
gzip_min_length 1000;

# Connection pooling
upstream django_app {
    keepalive 32;
    server web:8000;
}

# Caching
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m;
location /api/ {
    proxy_cache api_cache;
    proxy_cache_valid 200 5m;
}
```

---

## Health Checks

### Available Endpoints

```bash
# Simple health check (for load balancers)
curl http://localhost:8000/api/v1/health/

# Readiness check (Kubernetes)
curl http://localhost:8000/api/v1/readiness/

# Liveness check (Kubernetes)
curl http://localhost:8000/api/v1/liveness/

# Metrics
curl http://localhost:8000/api/v1/metrics/
```

### Response Examples

```json
// Health check
{
  "status": "healthy"
}

// Readiness check
{
  "status": "ready",
  "checks": {
    "database": true,
    "redis": true,
    "application": true
  }
}
```

### Kubernetes Configuration

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: expense-tracker-api
spec:
  template:
    spec:
      containers:
      - name: api
        image: expense-tracker-api:latest
        ports:
        - containerPort: 8000

        # Liveness probe
        livenessProbe:
          httpGet:
            path: /api/v1/liveness/
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10

        # Readiness probe
        readinessProbe:
          httpGet:
            path: /api/v1/readiness/
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
```

---

## Monitoring & Logging

### Application Logs

```bash
# View logs
docker-compose logs -f web

# Specific service
docker-compose logs -f celery

# Line limit
docker-compose logs --tail=100 web
```

### Centralized Logging

```bash
pip install python-json-logger

# Configure in settings
LOGGING = {
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter'
        }
    }
}
```

### Sentry Integration

```python
# settings/production.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,
    send_default_pii=False
)
```

### Prometheus Metrics

```bash
pip install django-prometheus

# In INSTALLED_APPS
'django_prometheus',

# Middleware
'django_prometheus.middleware.PrometheusBeforeMiddleware',
'django_prometheus.middleware.PrometheusAfterMiddleware',

# URL
path('metrics/', include('django_prometheus.urls')),
```

---

## Backup & Recovery

### Database Backups

```bash
# Backup database
docker-compose exec db pg_dump -U expense_user expense_tracker > backup_$(date +%Y%m%d_%H%M%S).sql

# Compressed backup
docker-compose exec db pg_dump -U expense_user expense_tracker | gzip > backup.sql.gz

# Automated daily backup
0 2 * * * docker-compose exec -T db pg_dump -U expense_user expense_tracker | gzip > /backups/backup_$(date +\%Y\%m\%d).sql.gz
```

### Backup Storage

```bash
# Local storage
mkdir -p /backups
chmod 700 /backups

# S3 backup
aws s3 sync /backups s3://my-bucket/backups/

# Automated S3 upload
0 3 * * * aws s3 cp /backups/backup_$(date +\%Y\%m\%d).sql.gz s3://my-bucket/backups/
```

### Database Restore

```bash
# Restore from backup
docker-compose exec db psql -U expense_user expense_tracker < backup.sql

# From compressed backup
gunzip < backup.sql.gz | docker-compose exec -T db psql -U expense_user expense_tracker
```

### Media Files Backup

```bash
# Backup media files
docker-compose exec web tar czf /tmp/media_backup.tar.gz /app/media/

# S3 backup
docker-compose exec web aws s3 sync /app/media/ s3://my-bucket/media/
```

---

## Scaling

### Horizontal Scaling

```yaml
# docker-compose.yml
services:
  web:
    deploy:
      replicas: 3
```

### Load Balancing

```nginx
upstream django_app {
    server web1:8000;
    server web2:8000;
    server web3:8000;

    # Load balancing algorithm
    least_conn;  # Least connections
}
```

### Kubernetes Scaling

```bash
kubectl scale deployment expense-tracker-api --replicas=3

# Auto-scaling
kubectl autoscale deployment expense-tracker-api --min=2 --max=10 --cpu-percent=80
```

### Celery Scaling

```bash
# Multiple workers
docker-compose up -d --scale celery=3

# Concurrency
celery -A config worker --concurrency=10 --prefetch-multiplier=1
```

---

## Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Change port in docker-compose
ports:
  - "8001:8000"
```

#### Database Connection Failed
```bash
# Check if database is running
docker-compose ps db

# Check logs
docker-compose logs db

# Verify credentials
docker-compose exec db psql -U expense_user -d expense_tracker
```

#### Out of Memory
```bash
# Check memory usage
docker stats

# Increase memory limit
docker run -m 2g ...

# Limit cache memory
CACHES = {
    'default': {
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}
```

#### Slow Queries
```bash
# Check slow query log
docker-compose exec web python manage.py dbshell
SELECT * FROM django_session;

# Enable query logging
DEBUG_QUERIES = True
```

### Debug Mode

```bash
# Temporary debug
docker-compose exec web \
  -e DEBUG=True \
  python manage.py shell

# View request/response
docker-compose logs -f web | grep "ERROR\|WARNING"
```

### Health Check Status

```bash
# Check all services
curl -s http://localhost:8000/api/v1/metrics/ | jq .

# Detailed check
curl -s http://localhost:8000/api/v1/readiness/ | jq .

# Manual database test
docker-compose exec db psql -U expense_user -c "SELECT version();"
```

---

## Production Checklist

### Before Deployment

- [ ] SECRET_KEY is strong and unique
- [ ] DEBUG = False
- [ ] ALLOWED_HOSTS configured
- [ ] Database credentials secured
- [ ] Redis password set
- [ ] SSL certificates obtained
- [ ] Backups configured and tested
- [ ] Monitoring setup (Sentry, Prometheus)
- [ ] Logging aggregation configured
- [ ] Health checks passing
- [ ] Load testing completed
- [ ] Documentation updated

### Post-Deployment

- [ ] Health checks monitored
- [ ] Error rates monitored
- [ ] Performance baseline established
- [ ] Backup verification
- [ ] User notification (if needed)
- [ ] Rollback procedure documented
- [ ] Team notified of deployment

---

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Django Production Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [12 Factor App](https://12factor.net/)

