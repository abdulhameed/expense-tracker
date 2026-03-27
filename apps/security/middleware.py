"""
Security middleware for additional protection layers.
"""
import logging
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add security headers to all responses.
    """

    def process_response(self, request, response):
        # Content Security Policy
        response["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https:; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )

        # X-Content-Type-Options - Prevent MIME type sniffing
        response["X-Content-Type-Options"] = "nosniff"

        # X-Frame-Options - Prevent clickjacking
        response["X-Frame-Options"] = "DENY"

        # X-XSS-Protection - Enable XSS protection in browsers
        response["X-XSS-Protection"] = "1; mode=block"

        # Referrer-Policy - Control referrer information
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions-Policy - Control browser features
        response["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "accelerometer=()"
        )

        # Strict-Transport-Security - Enable HSTS (only in production)
        if not request.META.get("HTTP_X_FORWARDED_PROTO") == "https":
            if request.is_secure():
                response["Strict-Transport-Security"] = (
                    "max-age=31536000; includeSubDomains; preload"
                )

        return response


class RateLimitHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add rate limit information to response headers.
    """

    def process_response(self, request, response):
        # Add X-RateLimit headers if set by throttle classes
        if hasattr(request, "throttle_wait_seconds"):
            response["X-RateLimit-Retry-After"] = str(
                int(request.throttle_wait_seconds)
            )

        return response


class IPWhitelistMiddleware(MiddlewareMixin):
    """
    Middleware to restrict access by IP address (if configured).

    Set ALLOWED_IPS in settings to enable:
        ALLOWED_IPS = ['127.0.0.1', '192.168.1.0/24']
    """

    def __init__(self, get_response):
        self.get_response = get_response
        from django.conf import settings
        self.allowed_ips = getattr(settings, "ALLOWED_IPS", None)

    def __call__(self, request):
        if self.allowed_ips:
            client_ip = self.get_client_ip(request)
            if not self.is_ip_allowed(client_ip):
                logger.warning(f"Access denied for IP: {client_ip}")
                return HttpResponseForbidden("Access denied")

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        """Get client IP from request, considering proxies."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    def is_ip_allowed(self, ip):
        """Check if IP is in allowed list (supports CIDR notation)."""
        from ipaddress import ip_address, ip_network

        try:
            client_ip = ip_address(ip)
            for allowed in self.allowed_ips:
                try:
                    # Try as CIDR network first
                    if client_ip in ip_network(allowed, strict=False):
                        return True
                except ValueError:
                    # Try as exact IP
                    if str(client_ip) == allowed:
                        return True
        except ValueError:
            logger.warning(f"Invalid IP format: {ip}")
            return False

        return False
