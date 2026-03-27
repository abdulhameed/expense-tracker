"""
Utility functions for activity logging.
"""


def get_client_ip(request):
    """
    Extract client IP address from request.

    Handles X-Forwarded-For header for proxied requests.
    """
    if not request:
        return None

    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        # X-Forwarded-For can contain multiple IPs, get the first one
        return x_forwarded_for.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR")


def get_user_agent(request):
    """Extract user agent from request."""
    if not request:
        return ""

    return request.META.get("HTTP_USER_AGENT", "")
