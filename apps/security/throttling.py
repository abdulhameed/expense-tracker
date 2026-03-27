"""
Rate limiting and throttling configuration.
"""
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class UserAuthenticationThrottle(UserRateThrottle):
    """
    Throttle for authentication endpoints.

    Rate limits: 5 requests per minute for authenticated users
    """
    scope = "user_auth"
    rate = "5/min"


class UserGeneralThrottle(UserRateThrottle):
    """
    Throttle for general authenticated API endpoints.

    Rate limits: 100 requests per hour for authenticated users
    """
    scope = "user_general"
    rate = "100/hour"


class AnonGeneralThrottle(AnonRateThrottle):
    """
    Throttle for anonymous/public endpoints.

    Rate limits: 20 requests per hour for anonymous users
    """
    scope = "anon_general"
    rate = "20/hour"


class BurstThrottle(UserRateThrottle):
    """
    Strict throttle for burst prevention.

    Rate limits: 10 requests per minute for authenticated users
    """
    scope = "burst"
    rate = "10/minute"


class SustainedThrottle(UserRateThrottle):
    """
    Throttle for sustained operations.

    Rate limits: 1000 requests per day for authenticated users
    """
    scope = "sustained"
    rate = "1000/day"


# Throttle classes configuration for different endpoints
AUTHENTICATION_THROTTLES = ["apps.security.throttling.UserAuthenticationThrottle"]
GENERAL_THROTTLES = [
    "apps.security.throttling.UserGeneralThrottle",
    "apps.security.throttling.AnonGeneralThrottle",
]
STRICT_THROTTLES = [
    "apps.security.throttling.BurstThrottle",
]
NORMAL_THROTTLES = [
    "apps.security.throttling.UserGeneralThrottle",
    "apps.security.throttling.AnonGeneralThrottle",
]
