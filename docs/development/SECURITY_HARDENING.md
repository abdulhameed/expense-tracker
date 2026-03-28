# Security Hardening Guide

## Overview

This guide covers the security hardening measures implemented in the Expense Tracker API to protect against common web application vulnerabilities.

## Table of Contents

1. [Rate Limiting & Throttling](#rate-limiting--throttling)
2. [Input Validation & Sanitization](#input-validation--sanitization)
3. [Authentication Hardening](#authentication-hardening)
4. [CSRF Protection](#csrf-protection)
5. [Security Headers](#security-headers)
6. [CORS Configuration](#cors-configuration)
7. [SQL Injection Prevention](#sql-injection-prevention)
8. [XSS Protection](#xss-protection)
9. [Secrets Management](#secrets-management)
10. [Compliance Checklist](#compliance-checklist)

---

## Rate Limiting & Throttling

### Overview

Rate limiting prevents abuse by restricting the number of API requests per time period.

### Configuration

```python
# config/settings/base.py
DEFAULT_THROTTLE_CLASSES = (
    "apps.security.throttling.UserGeneralThrottle",
    "apps.security.throttling.AnonGeneralThrottle",
)

DEFAULT_THROTTLE_RATES = {
    "user_auth": "5/min",          # Auth endpoints: 5 requests/minute
    "user_general": "100/hour",    # General: 100 requests/hour for auth users
    "anon_general": "20/hour",     # Anonymous: 20 requests/hour
    "burst": "10/minute",          # Burst prevention: 10 requests/minute
    "sustained": "1000/day",       # Daily limit: 1000 requests/day
}
```

### Throttle Classes

#### UserGeneralThrottle
- Rate: 100 requests per hour
- For: Authenticated users
- Scope: `user_general`

#### AnonGeneralThrottle
- Rate: 20 requests per hour
- For: Anonymous/unauthenticated users
- Scope: `anon_general`

#### BurstThrottle
- Rate: 10 requests per minute
- For: Strict burst prevention
- Use: Apply to sensitive endpoints

#### SustainedThrottle
- Rate: 1000 requests per day
- For: Daily usage limits
- Use: Apply to resource-intensive endpoints

### Usage in Views

```python
from rest_framework.decorators import api_view, throttle_classes
from apps.security.throttling import BurstThrottle

@api_view(['POST'])
@throttle_classes([BurstThrottle])
def sensitive_endpoint(request):
    """Endpoint with strict rate limiting."""
    return Response({'status': 'ok'})
```

### Response Headers

When throttled, responses include rate limit information:

```
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Retry-After: 3600
```

---

## Input Validation & Sanitization

### Overview

Validates and sanitizes all user inputs to prevent injection attacks.

### HTML Sanitization

```python
from apps.security.validators import sanitize_html

# Safe HTML escaping
user_input = "<p>Hello</p><script>alert('xss')</script>"
clean_html = sanitize_html(user_input)
# Result: "<p>Hello</p>" (script tag removed)

# Custom allowed tags
clean_html = sanitize_html(user_input, allowed_tags=['p', 'a', 'em'])
```

### Special Characters Validation

```python
from apps.security.validators import validate_no_special_chars
from django.core.exceptions import ValidationError

try:
    validate_no_special_chars("hello<world")  # Raises ValidationError
except ValidationError as e:
    print(f"Invalid: {e}")

# Valid input
validate_no_special_chars("hello_world")  # OK
```

### SQL Injection Prevention

```python
from apps.security.validators import validate_no_sql_injection

# Detects SQL keywords and patterns
try:
    validate_no_sql_injection("test'; DROP TABLE users;--")
except ValidationError:
    print("SQL injection pattern detected")

# Safe input
validate_no_sql_injection("normal user input")  # OK
```

### Safe Field Validators

```python
from apps.security.validators import SafeFieldValidator

# Username validation
SafeFieldValidator.validate_username("john_doe")  # OK
SafeFieldValidator.validate_username("user@domain")  # Raises ValidationError

# Filename validation
SafeFieldValidator.validate_filename("document.pdf")  # OK
SafeFieldValidator.validate_filename("../../../etc/passwd")  # Raises ValidationError

# URL path validation
SafeFieldValidator.validate_url_path("api/v1/users")  # OK
SafeFieldValidator.validate_url_path("/admin")  # Raises ValidationError

# Search query validation
SafeFieldValidator.validate_search_query("project 2026")  # OK
SafeFieldValidator.validate_search_query("<script>alert</script>")  # Raises ValidationError
```

### User Input Escaping

```python
from apps.security.validators import escape_user_input

user_input = "<script>alert('xss')</script>"
escaped = escape_user_input(user_input)
# Result: "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;"
```

---

## Authentication Hardening

### JWT Configuration

```python
# Enhanced JWT settings
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),  # Short-lived tokens
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,  # Rotate on each refresh
    "BLACKLIST_AFTER_ROTATION": True,  # Blacklist old tokens
    "UPDATE_LAST_LOGIN": True,  # Track last login
}
```

### Brute Force Protection

```python
from apps.security.authentication import FailedLoginAttempts

# Record failed attempt
FailedLoginAttempts.record_failed_attempt("username")

# Check if account locked
if FailedLoginAttempts.is_account_locked("username"):
    # Deny login

# Get remaining attempts
remaining = FailedLoginAttempts.get_remaining_attempts("username")

# Reset attempts (on successful login)
FailedLoginAttempts.reset_failed_attempts("username")
```

### Password Reset Security

```python
from apps.security.authentication import PasswordReset

# Generate secure token
reset_token = PasswordReset.generate_reset_token()

# Hash for storage
token_hash = PasswordReset.hash_reset_token(reset_token)

# Validate token
is_valid = PasswordReset.validate_reset_token(stored_hash, provided_token)
```

### Secure Password Validation

```python
from apps.security.validators import validate_secure_password

# Requirements:
# - Minimum 12 characters
# - At least one uppercase letter
# - At least one lowercase letter
# - At least one digit
# - At least one special character

try:
    validate_secure_password("MyPassword123!")  # OK
except ValidationError as e:
    print(f"Password too weak: {e}")
```

---

## CSRF Protection

### Configuration

```python
# config/settings/base.py
CSRF_COOKIE_SECURE = True         # HTTPS only
CSRF_COOKIE_HTTPONLY = True       # No JavaScript access
CSRF_COOKIE_SAMESITE = "Strict"   # Strict same-site
```

### Custom Header Name

```python
# CSRF token via custom header
# Header: X-CSRFToken: <token>

# Django automatically handles CSRF for:
# - POST, PUT, PATCH, DELETE requests
# - If CSRF_HEADER_NAME is configured
```

### Trusted Origins

```python
# Only these origins can make CSRF-protected requests
CSRF_TRUSTED_ORIGINS = [
    "https://expensetracker.com",
    "https://*.expensetracker.com",
]
```

---

## Security Headers

### Implemented Headers

1. **Content-Security-Policy (CSP)**
   - Prevents inline script execution
   - Restricts resource loading origins
   - Blocks frame embedding

2. **X-Content-Type-Options**
   - Prevents MIME type sniffing
   - Value: `nosniff`

3. **X-Frame-Options**
   - Prevents clickjacking attacks
   - Value: `DENY` (no framing)

4. **X-XSS-Protection**
   - Browser XSS protection
   - Value: `1; mode=block`

5. **Referrer-Policy**
   - Controls referrer information
   - Value: `strict-origin-when-cross-origin`

6. **Permissions-Policy**
   - Restricts browser features
   - Disables: geolocation, microphone, camera, payment, etc.

### Middleware Implementation

```python
# apps/security/middleware.py
class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Automatically adds security headers to all responses.
    """
    def process_response(self, request, response):
        # Add CSP, X-Frame-Options, etc.
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        # ... more headers
        return response
```

---

## CORS Configuration

### Configuration

```python
# config/settings/base.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://app.example.com",
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "x-csrftoken",
    "x-requested-with",
    "x-api-key",
]
CORS_MAX_AGE = 86400  # 24 hours
```

### Environment Configuration

```bash
# .env
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://app.example.com
```

### Security Best Practices

1. **Whitelist Origins Only**
   - Never use `*` in production
   - Be specific with allowed origins

2. **Avoid Wildcards**
   - Don't use broad patterns like `https://*.example.com`
   - List specific subdomains

3. **Set Appropriate Max-Age**
   - 86400 seconds = 24 hours
   - Reduces preflight requests safely

4. **Review Allowed Headers**
   - Only include necessary headers
   - Prevents header-based attacks

---

## SQL Injection Prevention

### Django ORM Protection

Django ORM automatically prevents SQL injection through parameterized queries:

```python
# Safe - using ORM
users = User.objects.filter(email=user_input)

# Unsafe - string concatenation (NEVER DO THIS)
query = f"SELECT * FROM users WHERE email = '{user_input}'"
```

### Additional Validation

```python
from apps.security.validators import validate_no_sql_injection

# Validate user input before database operations
validate_no_sql_injection(user_search_query)

# Then use with ORM safely
results = Model.objects.filter(field__icontains=user_search_query)
```

### Query Validation

- All database queries use parameterized queries
- ORM prevents string concatenation
- Input validation adds additional layer

---

## XSS Protection

### Automatic Escaping

Django templates automatically escape variables:

```django
<!-- Safe - {{ user_input }} is escaped -->
<p>{{ user_input }}</p>

<!-- Unsafe - Don't use this -->
<p>{{ user_input | safe }}</p>
```

### API Response Handling

```python
from apps.security.validators import sanitize_html, escape_user_input

# Sanitize user content
user_notes = sanitize_html(request.data.get('notes'))

# Or escape for display
escaped_content = escape_user_input(user_input)
```

### Content Security Policy

Restricts where scripts can be loaded from:

```python
SECURE_CONTENT_SECURITY_POLICY = {
    "default-src": ("'self'",),
    "script-src": ("'self'",),  # Only same-origin scripts
    "style-src": ("'self'", "'unsafe-inline'"),  # Inline styles allowed
    "img-src": ("'self'", "data:", "https:"),
}
```

---

## Secrets Management

### Environment Variables

All sensitive configuration stored in `.env`:

```bash
# .env (never commit to version control)
SECRET_KEY=your-secret-key-here
DB_PASSWORD=secure-password
REDIS_URL=redis://localhost:6379
EMAIL_PASSWORD=email-password
```

### Secure Secret Storage

```python
# config/settings/base.py
SECRET_KEY = config("SECRET_KEY")  # From environment
DB_PASSWORD = config("DB_PASSWORD")  # From environment
ALLOWED_HOSTS = config("ALLOWED_HOSTS")  # From environment
```

### .env File Security

```bash
# .gitignore
.env
.env.local
*.key
secrets/
```

### Production Secrets

Use environment-specific management:
- AWS Secrets Manager
- HashiCorp Vault
- Azure Key Vault
- Environment variables (containerized)

### Database Credentials

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST"),
        "PORT": config("DB_PORT"),
    }
}
```

---

## Session Security

### Configuration

```python
# config/settings/base.py
SESSION_COOKIE_SECURE = True          # HTTPS only
SESSION_COOKIE_HTTPONLY = True        # No JavaScript access
SESSION_COOKIE_SAMESITE = "Strict"    # CSRF protection
SESSION_COOKIE_AGE = 3600             # 1 hour timeout
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Expire on close
```

### Session Timeout

```python
# Session expires after 1 hour of inactivity
SESSION_COOKIE_AGE = 3600

# Session expires when browser closes
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
```

### Secure Session Handling

```python
from apps.security.authentication import SessionSecurity

# Get recommended session settings
settings = SessionSecurity.get_session_settings()
```

---

## File Upload Security

### Configuration

```python
# config/settings/base.py
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB

ALLOWED_DOCUMENT_TYPES = [
    "image/jpeg",
    "image/png",
    "image/webp",
    "application/pdf",
    "text/csv",
]
```

### Validation

```python
# Filename validation
SafeFieldValidator.validate_filename(uploaded_filename)

# Content type validation
if file.content_type not in ALLOWED_DOCUMENT_TYPES:
    raise ValidationError("File type not allowed")
```

---

## API Key Security

### Secure Token Authentication

```python
from apps.security.authentication import SecureTokenAuthentication

# Enhanced security checks:
# - Validates token format (alphanumeric, 40 chars)
# - Prevents token injection attacks
# - Rotates tokens regularly
```

### Custom Header

```python
# Usage
Authorization: ApiKey <40-character-token>
```

---

## Logging & Monitoring

### Security Logging

```python
# Logs security-relevant events:
# - Authentication failures
# - Authorization violations
# - Rate limit exceeded
# - Suspicious patterns
```

### Log Locations

```
logs/security.log      # Security warnings and errors
logs/auth.log         # Authentication events
```

### Monitoring Tips

```python
# Monitor failed login attempts
from apps.security.authentication import FailedLoginAttempts
logger.warning(f"Failed login for {username}")

# Monitor rate limit violations
logger.warning(f"Rate limit exceeded for {user_id}")

# Monitor validation failures
logger.warning(f"SQL injection pattern detected: {input}")
```

---

## Deployment Security Checklist

### Before Production

- [ ] SECRET_KEY configured with strong random value
- [ ] DEBUG = False
- [ ] ALLOWED_HOSTS properly configured
- [ ] Database credentials in environment variables
- [ ] HTTPS enabled
- [ ] CSRF_TRUSTED_ORIGINS properly set
- [ ] CORS_ALLOWED_ORIGINS whitelist configured
- [ ] Email credentials secured
- [ ] Redis password set
- [ ] File upload directory writable only by application

### HTTPS/SSL

- [ ] Valid SSL certificate installed
- [ ] HSTS enabled (Strict-Transport-Security header)
- [ ] SESSION_COOKIE_SECURE = True
- [ ] CSRF_COOKIE_SECURE = True
- [ ] SECURE_SSL_REDIRECT = True (in production)

### Database Security

- [ ] Strong database password
- [ ] Database user has minimal required permissions
- [ ] Connection pooling enabled
- [ ] Query timeout configured
- [ ] Automatic backups enabled

### API Security

- [ ] Rate limiting enforced
- [ ] Authentication required for all endpoints
- [ ] Input validation on all endpoints
- [ ] Output encoding on all responses
- [ ] API keys rotated regularly

### Secrets

- [ ] No secrets committed to version control
- [ ] Environment variables for all secrets
- [ ] Secrets rotated periodically
- [ ] Audit trail for secret access

### Monitoring

- [ ] Security logs collected
- [ ] Failed login attempts monitored
- [ ] Rate limit violations monitored
- [ ] Error rates monitored
- [ ] Suspicious patterns detected

---

## Security Testing

### Unit Tests

Run security tests with pytest:

```bash
pytest apps/security/tests/test_security.py -v
```

### Test Coverage

- Input validation tests
- SQL injection prevention tests
- XSS protection tests
- CSRF protection tests
- Rate limiting tests
- Authentication tests
- Authorization tests

### Manual Testing

```bash
# Test rate limiting
for i in {1..150}; do
    curl -H "Authorization: Bearer $TOKEN" https://api.example.com/api/v1/transactions/
done

# Test input validation
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"notes": "<script>alert(1)</script>"}' \
  https://api.example.com/api/v1/transactions/

# Test CSRF protection (should fail without token)
curl -X POST \
  -d "data=value" \
  https://api.example.com/api/v1/transactions/
```

---

## Common Vulnerabilities & Mitigations

| Vulnerability | Mitigation |
|---|---|
| SQL Injection | Django ORM + input validation |
| XSS (Cross-Site Scripting) | CSP + template escaping + sanitization |
| CSRF (Cross-Site Request Forgery) | CSRF tokens + SameSite cookies |
| Brute Force Attacks | Rate limiting + account lockout |
| DDoS Attacks | Rate limiting + WAF + load balancing |
| Insecure Direct Object Reference | Object-level permissions |
| Sensitive Data Exposure | HTTPS + secure cookies + encryption |
| Broken Authentication | JWT + rate limiting + session security |
| Insufficient Logging | Security logging + monitoring |
| Using Components with Known Vulnerabilities | Regular updates + dependency scanning |

---

## External Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Django Security Documentation](https://docs.djangoproject.com/en/stable/topics/security/)
- [Django REST Framework Security](https://www.django-rest-framework.org/api-guide/authentication/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [SANS Top 25](https://www.sans.org/top25-software-errors/)

---

## Support

For security issues or questions:
- Report security vulnerabilities privately
- Check Django security releases
- Review OWASP guidelines
- Consult Django REST Framework docs

