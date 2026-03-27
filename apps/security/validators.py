"""
Custom validators for input validation and sanitization.
"""
import re
from typing import Any
from django.core.exceptions import ValidationError
from django.utils.html import escape
from bleach import clean as bleach_clean


def sanitize_html(value: str, allowed_tags: list = None) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.

    Args:
        value: HTML string to sanitize
        allowed_tags: List of allowed HTML tags (default: common safe tags)

    Returns:
        Sanitized HTML string
    """
    if allowed_tags is None:
        allowed_tags = [
            "p",
            "br",
            "strong",
            "em",
            "u",
            "a",
            "ul",
            "ol",
            "li",
            "blockquote",
        ]

    allowed_attributes = {"a": ["href", "title"]}
    return bleach_clean(value, tags=allowed_tags, attributes=allowed_attributes)


def validate_no_special_chars(value: str):
    """
    Validate that value doesn't contain dangerous special characters.

    Args:
        value: String to validate

    Raises:
        ValidationError: If dangerous characters are found
    """
    dangerous_chars = r'[<>\"\'%;()&+]'
    if re.search(dangerous_chars, value):
        raise ValidationError("String contains dangerous special characters")


def validate_no_sql_injection(value: str):
    """
    Validate that value doesn't contain SQL injection patterns.

    Args:
        value: String to validate

    Raises:
        ValidationError: If SQL injection patterns are detected
    """
    sql_keywords = [
        r"\b(UNION|SELECT|DROP|DELETE|INSERT|UPDATE|EXEC|EXECUTE)\b",
        r"(;|-{2}|/\*|\*/|xp_|sp_)",
    ]

    for pattern in sql_keywords:
        if re.search(pattern, value, re.IGNORECASE):
            raise ValidationError("SQL injection pattern detected")


def validate_secure_password(value: str):
    """
    Validate password strength.

    Requirements:
    - Minimum 12 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character

    Args:
        value: Password to validate

    Raises:
        ValidationError: If password doesn't meet requirements
    """
    if len(value) < 12:
        raise ValidationError("Password must be at least 12 characters long")

    if not re.search(r"[A-Z]", value):
        raise ValidationError("Password must contain at least one uppercase letter")

    if not re.search(r"[a-z]", value):
        raise ValidationError("Password must contain at least one lowercase letter")

    if not re.search(r"\d", value):
        raise ValidationError("Password must contain at least one digit")

    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};:'\",.<>?/\\|`~]", value):
        raise ValidationError("Password must contain at least one special character")


def validate_email_domain(value: str, blocked_domains: list = None):
    """
    Validate email domain against blocked list.

    Args:
        value: Email address to validate
        blocked_domains: List of blocked domains (e.g., ['tempmail.com'])

    Raises:
        ValidationError: If email domain is blocked
    """
    if blocked_domains is None:
        blocked_domains = [
            "tempmail.com",
            "throwaway.email",
            "mailinator.com",
            "10minutemail.com",
        ]

    domain = value.split("@")[1].lower()
    if domain in blocked_domains:
        raise ValidationError(f"Email domain '{domain}' is not allowed")


def escape_user_input(value: Any) -> str:
    """
    Escape user input to prevent XSS attacks.

    Args:
        value: Value to escape

    Returns:
        Escaped string
    """
    return escape(str(value))


class SafeFieldValidator:
    """
    Validator class for common field types with security checks.
    """

    @staticmethod
    def validate_username(value: str):
        """Validate username format."""
        if not re.match(r"^[a-zA-Z0-9_.-]+$", value):
            raise ValidationError(
                "Username can only contain letters, numbers, underscores, dots, and hyphens"
            )
        if len(value) < 3:
            raise ValidationError("Username must be at least 3 characters long")
        if len(value) > 30:
            raise ValidationError("Username must be at most 30 characters long")

    @staticmethod
    def validate_filename(value: str):
        """Validate filename to prevent directory traversal."""
        if ".." in value or "/" in value or "\\" in value:
            raise ValidationError("Invalid filename - path traversal detected")
        if len(value) > 255:
            raise ValidationError("Filename is too long")

    @staticmethod
    def validate_url_path(value: str):
        """Validate URL path."""
        if ".." in value or value.startswith("/"):
            raise ValidationError("Invalid URL path - directory traversal detected")

    @staticmethod
    def validate_search_query(value: str):
        """Validate search query input."""
        if len(value) > 1000:
            raise ValidationError("Search query is too long")
        if re.search(r"[<>\"'%;()&]", value):
            raise ValidationError("Search query contains invalid characters")
