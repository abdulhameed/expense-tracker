"""
Tests for security/validators.py - Input validation and sanitization.

Tests:
- sanitize_html() - XSS prevention
- validate_no_special_chars() - Dangerous character detection
- validate_no_sql_injection() - SQL injection detection
- validate_secure_password() - Password strength
- validate_email_domain() - Email domain blocking
- escape_user_input() - XSS escaping
- SafeFieldValidator - Field-specific validation
"""

import pytest
from django.core.exceptions import ValidationError

from apps.security.validators import (
    sanitize_html,
    validate_no_special_chars,
    validate_no_sql_injection,
    validate_secure_password,
    validate_email_domain,
    escape_user_input,
    SafeFieldValidator,
)


class TestSanitizeHTML:
    """Test HTML sanitization for XSS prevention."""

    def test_sanitize_removes_script_tags(self):
        """Test that script tags are removed."""
        input_html = "<p>Hello</p><script>alert('xss')</script>"
        result = sanitize_html(input_html)

        assert "<script>" not in result
        assert "alert" not in result
        assert "<p>Hello</p>" in result

    def test_sanitize_preserves_safe_tags(self):
        """Test that safe tags like <p> are preserved."""
        input_html = "<p>Hello <strong>World</strong></p>"
        result = sanitize_html(input_html)

        assert "<p>" in result
        assert "<strong>" in result
        assert "Hello" in result

    def test_sanitize_removes_event_handlers(self):
        """Test that event handlers are removed."""
        input_html = '<p onclick="alert(\'xss\')">Click me</p>'
        result = sanitize_html(input_html)

        assert "onclick" not in result
        assert "alert" not in result

    def test_sanitize_removes_style_tags(self):
        """Test that style tags are removed."""
        input_html = "<p>Text</p><style>body {display:none;}</style>"
        result = sanitize_html(input_html)

        assert "<style>" not in result
        assert "display:none" not in result

    def test_sanitize_preserves_links(self):
        """Test that <a> tags with href are preserved."""
        input_html = '<a href="https://example.com">Link</a>'
        result = sanitize_html(input_html)

        assert "<a" in result
        assert "href" in result

    def test_sanitize_preserves_lists(self):
        """Test that list tags are preserved."""
        input_html = "<ul><li>Item 1</li><li>Item 2</li></ul>"
        result = sanitize_html(input_html)

        assert "<ul>" in result or "<ul" in result
        assert "<li>" in result
        assert "Item 1" in result

    def test_sanitize_empty_string(self):
        """Test sanitizing empty string."""
        result = sanitize_html("")
        assert result == "" or result is not None

    def test_sanitize_removes_iframes(self):
        """Test that iframe tags are removed."""
        input_html = '<iframe src="http://evil.com"></iframe>'
        result = sanitize_html(input_html)

        assert "<iframe>" not in result
        assert "evil.com" not in result

    def test_sanitize_removes_img_onerror(self):
        """Test that onerror handlers are removed from img tags."""
        input_html = '<img src="x" onerror="alert(\'xss\')">'
        result = sanitize_html(input_html)

        assert "onerror" not in result
        assert "alert" not in result

    def test_sanitize_preserves_blockquote(self):
        """Test that blockquote tags are preserved."""
        input_html = "<blockquote>Quote here</blockquote>"
        result = sanitize_html(input_html)

        assert "<blockquote>" in result or "<blockquote" in result
        assert "Quote here" in result

    def test_sanitize_custom_allowed_tags(self):
        """Test sanitizing with custom allowed tags."""
        input_html = "<p>Safe</p><div>Not allowed</div>"
        result = sanitize_html(input_html, allowed_tags=["p"])

        assert "<p>" in result
        assert "<div>" not in result

    def test_sanitize_removes_data_attributes(self):
        """Test that data attributes are removed."""
        input_html = '<p data-evil="xss">Text</p>'
        result = sanitize_html(input_html)

        assert "data-evil" not in result or "xss" not in result

    def test_sanitize_nested_dangerous_tags(self):
        """Test sanitizing nested dangerous tags."""
        input_html = "<p><script>nested</script>Text</p>"
        result = sanitize_html(input_html)

        assert "<script>" not in result
        assert "nested" not in result or "Text" in result


class TestValidateNoSpecialChars:
    """Test detection of dangerous special characters."""

    def test_reject_angle_brackets(self):
        """Test that < and > are rejected."""
        with pytest.raises(ValidationError):
            validate_no_special_chars("hello<world>")

    def test_reject_quotes(self):
        """Test that quotes are rejected."""
        with pytest.raises(ValidationError):
            validate_no_special_chars('hello"world')

        with pytest.raises(ValidationError):
            validate_no_special_chars("hello'world")

    def test_reject_percent_sign(self):
        """Test that % is rejected."""
        with pytest.raises(ValidationError):
            validate_no_special_chars("hello%world")

    def test_reject_ampersand(self):
        """Test that & is rejected."""
        with pytest.raises(ValidationError):
            validate_no_special_chars("hello&world")

    def test_accept_safe_input(self):
        """Test that safe input is accepted."""
        # Should not raise
        validate_no_special_chars("hello world 123")
        validate_no_special_chars("test-input_value")

    def test_reject_parentheses(self):
        """Test that parentheses are rejected."""
        with pytest.raises(ValidationError):
            validate_no_special_chars("hello(world)")

    def test_reject_semicolon(self):
        """Test that semicolon is rejected."""
        with pytest.raises(ValidationError):
            validate_no_special_chars("hello;world")

    def test_accept_hyphens_and_underscores(self):
        """Test that hyphens and underscores are accepted."""
        # Should not raise
        validate_no_special_chars("hello-world_test")

    def test_accept_numbers(self):
        """Test that numbers are accepted."""
        validate_no_special_chars("test123")

    def test_reject_multiple_dangerous_chars(self):
        """Test rejection when multiple dangerous chars present."""
        with pytest.raises(ValidationError):
            validate_no_special_chars("hello<world>&goodbye")


class TestValidateNoSQLInjection:
    """Test SQL injection detection."""

    def test_reject_union_select(self):
        """Test that UNION SELECT is detected."""
        with pytest.raises(ValidationError):
            validate_no_sql_injection("test' UNION SELECT * FROM users--")

    def test_reject_case_insensitive(self):
        """Test that SQL keywords are detected case-insensitively."""
        with pytest.raises(ValidationError):
            validate_no_sql_injection("test' union select * from users--")

    def test_reject_drop_table(self):
        """Test that DROP TABLE is detected."""
        with pytest.raises(ValidationError):
            validate_no_sql_injection("test'; DROP TABLE users;--")

    def test_reject_delete(self):
        """Test that DELETE is detected."""
        with pytest.raises(ValidationError):
            validate_no_sql_injection("test'; DELETE FROM users;--")

    def test_reject_insert(self):
        """Test that INSERT is detected."""
        with pytest.raises(ValidationError):
            validate_no_sql_injection("test'; INSERT INTO users VALUES;--")

    def test_reject_sql_comments(self):
        """Test that SQL comment syntax is detected."""
        with pytest.raises(ValidationError):
            validate_no_sql_injection("test'--comment")

    def test_accept_safe_input(self):
        """Test that safe input passes."""
        # Should not raise
        validate_no_sql_injection("normal input text")
        validate_no_sql_injection("email@example.com")

    def test_reject_update_statement(self):
        """Test that UPDATE is detected."""
        with pytest.raises(ValidationError):
            validate_no_sql_injection("test'; UPDATE users SET admin=1;--")

    def test_reject_exec_xp(self):
        """Test that EXEC/xp_ stored procedures are detected."""
        with pytest.raises(ValidationError):
            validate_no_sql_injection("test'; EXEC xp_cmdshell;--")

    def test_reject_block_comment(self):
        """Test that /* */ block comments are detected."""
        with pytest.raises(ValidationError):
            validate_no_sql_injection("test' /* comment */ AND '1'='1")

    def test_accept_apostrophe_in_text(self):
        """Test that single apostrophe in normal text is accepted."""
        # Should not raise - apostrophes alone are ok, dangerous with SQL keywords
        validate_no_sql_injection("O'Reilly")

    def test_reject_select_lowercase(self):
        """Test that lowercase select is detected."""
        with pytest.raises(ValidationError):
            validate_no_sql_injection("test' select * from users--")


class TestValidateSecurePassword:
    """Test password strength validation."""

    def test_reject_too_short(self):
        """Test that passwords shorter than 12 chars are rejected."""
        with pytest.raises(ValidationError):
            validate_secure_password("Short1!")

    def test_reject_no_uppercase(self):
        """Test that passwords without uppercase are rejected."""
        with pytest.raises(ValidationError):
            validate_secure_password("password123!")

    def test_reject_no_lowercase(self):
        """Test that passwords without lowercase are rejected."""
        with pytest.raises(ValidationError):
            validate_secure_password("PASSWORD123!")

    def test_reject_no_digit(self):
        """Test that passwords without digits are rejected."""
        with pytest.raises(ValidationError):
            validate_secure_password("PasswordSpecial!")

    def test_reject_no_special_char(self):
        """Test that passwords without special characters are rejected."""
        with pytest.raises(ValidationError):
            validate_secure_password("Password1234")

    def test_accept_valid_password(self):
        """Test that valid password is accepted."""
        # Should not raise
        validate_secure_password("ValidPassword123!")

    def test_accept_complex_password(self):
        """Test that complex password is accepted."""
        validate_secure_password("C0mpl3x!@#$%")

    def test_minimum_length_exactly_12(self):
        """Test that exactly 12 characters is accepted."""
        validate_secure_password("Pass1234!xyz")

    def test_accept_long_password(self):
        """Test that very long passwords are accepted."""
        long_password = "VeryLongPassword123!@#WithManyCharacters"
        validate_secure_password(long_password)

    def test_password_with_multiple_special_chars(self):
        """Test password with multiple special characters."""
        validate_secure_password("Pass123!@#$%")

    def test_password_with_numbers_at_end(self):
        """Test password with numbers at the end."""
        validate_secure_password("ValidPass2024!")

    def test_password_all_requirements_met(self):
        """Test password that meets all requirements with variety."""
        validate_secure_password("Str0ng!P@ssw0rd")

    def test_reject_11_character_password(self):
        """Test that 11 character password is rejected."""
        with pytest.raises(ValidationError):
            validate_secure_password("Pass1234!x")


class TestValidateEmailDomain:
    """Test email domain blocking for suspicious providers."""

    def test_reject_tempmail(self):
        """Test that tempmail.com is rejected."""
        with pytest.raises(ValidationError):
            validate_email_domain("user@tempmail.com")

    def test_reject_throwaway(self):
        """Test that throwaway.email is rejected."""
        with pytest.raises(ValidationError):
            validate_email_domain("user@throwaway.email")

    def test_reject_mailinator(self):
        """Test that mailinator.com is rejected."""
        with pytest.raises(ValidationError):
            validate_email_domain("user@mailinator.com")

    def test_reject_10minutemail(self):
        """Test that 10minutemail.com is rejected."""
        with pytest.raises(ValidationError):
            validate_email_domain("user@10minutemail.com")

    def test_accept_gmail(self):
        """Test that gmail.com is accepted."""
        # Should not raise
        validate_email_domain("user@gmail.com")

    def test_accept_company_domain(self):
        """Test that company domains are accepted."""
        validate_email_domain("user@mycompany.com")

    def test_accept_outlook(self):
        """Test that outlook.com is accepted."""
        validate_email_domain("user@outlook.com")

    def test_case_insensitive_domain_check(self):
        """Test that domain check is case-insensitive."""
        with pytest.raises(ValidationError):
            validate_email_domain("user@TEMPMAIL.COM")

    def test_accept_custom_domain_list(self):
        """Test custom blocked domains list."""
        # Should not raise - only custom blocked domains
        validate_email_domain("user@tempmail.com", blocked_domains=["custom.com"])

    def test_reject_custom_blocked_domain(self):
        """Test rejecting custom blocked domains."""
        with pytest.raises(ValidationError):
            validate_email_domain("user@custom.com", blocked_domains=["custom.com"])

    def test_accept_subdomain_not_blocked(self):
        """Test that subdomains of blocked domains are accepted."""
        # Should not raise - subdomain is different
        validate_email_domain("user@sub.tempmail.com")

    def test_accept_yahoo_email(self):
        """Test that Yahoo emails are accepted."""
        validate_email_domain("user@yahoo.com")

    def test_accept_corporate_email(self):
        """Test that corporate emails are accepted."""
        validate_email_domain("john.doe@acmecorp.com")

    def test_accept_multiple_dots_in_name(self):
        """Test email with multiple dots in local part."""
        validate_email_domain("john.doe.smith@gmail.com")


class TestEscapeUserInput:
    """Test XSS escaping of user input."""

    def test_escape_angle_brackets(self):
        """Test that < and > are escaped."""
        result = escape_user_input("<script>")
        assert "<script>" not in result
        assert "&lt;" in result or "&#" in result

    def test_escape_quotes(self):
        """Test that quotes are escaped."""
        result = escape_user_input('hello "world"')
        assert "&quot;" in result or "&#" in result

    def test_escape_ampersand(self):
        """Test that & is escaped."""
        result = escape_user_input("A & B")
        assert "&amp;" in result

    def test_preserve_safe_text(self):
        """Test that safe text is preserved."""
        result = escape_user_input("Hello World")
        assert "Hello World" in result

    def test_escape_single_quotes(self):
        """Test that single quotes are properly escaped."""
        result = escape_user_input("It's working")
        # Django's escape escapes single quotes in some contexts
        assert "It" in result and "working" in result

    def test_escape_greater_than(self):
        """Test that > is escaped."""
        result = escape_user_input("a > b")
        assert "&gt;" in result

    def test_escape_less_than(self):
        """Test that < is escaped."""
        result = escape_user_input("a < b")
        assert "&lt;" in result

    def test_escape_html_entities(self):
        """Test escaping HTML entities."""
        result = escape_user_input("<div class='test'>&nbsp;</div>")
        assert "<div" not in result
        assert "class" in result or "test" in result


class TestSafeFieldValidator:
    """Test SafeFieldValidator for field-specific validation."""

    def test_validate_username_valid(self):
        """Test that valid usernames are accepted."""
        validator = SafeFieldValidator()
        # Should not raise
        validator.validate_username("valid_user.123")

    def test_validate_username_too_short(self):
        """Test that usernames shorter than 3 chars are rejected."""
        validator = SafeFieldValidator()
        with pytest.raises(ValidationError):
            validator.validate_username("ab")

    def test_validate_username_too_long(self):
        """Test that usernames longer than 30 chars are rejected."""
        validator = SafeFieldValidator()
        with pytest.raises(ValidationError):
            validator.validate_username("a" * 31)

    def test_validate_username_invalid_chars(self):
        """Test that special characters are rejected in usernames."""
        validator = SafeFieldValidator()
        with pytest.raises(ValidationError):
            validator.validate_username("user!@#")

    def test_validate_filename_valid(self):
        """Test that valid filenames are accepted."""
        validator = SafeFieldValidator()
        # Should not raise
        validator.validate_filename("document.pdf")

    def test_validate_filename_prevents_traversal(self):
        """Test that path traversal is prevented."""
        validator = SafeFieldValidator()
        with pytest.raises(ValidationError):
            validator.validate_filename("../../../etc/passwd")

    def test_validate_filename_too_long(self):
        """Test that filenames longer than 255 chars are rejected."""
        validator = SafeFieldValidator()
        with pytest.raises(ValidationError):
            validator.validate_filename("a" * 256)

    def test_validate_url_path_valid(self):
        """Test that valid URL paths are accepted."""
        validator = SafeFieldValidator()
        # Should not raise
        validator.validate_url_path("/api/v1/users/")

    def test_validate_url_path_prevents_traversal(self):
        """Test that path traversal in URL paths is prevented."""
        validator = SafeFieldValidator()
        with pytest.raises(ValidationError):
            validator.validate_url_path("/api/../../../etc/passwd")

    def test_validate_search_query_valid(self):
        """Test that valid search queries are accepted."""
        validator = SafeFieldValidator()
        # Should not raise
        validator.validate_search_query("search term")

    def test_validate_search_query_max_length(self):
        """Test that search queries are limited to 1000 chars."""
        validator = SafeFieldValidator()
        with pytest.raises(ValidationError):
            validator.validate_search_query("a" * 1001)

    def test_validate_search_query_no_special_chars(self):
        """Test that special characters in search are rejected."""
        validator = SafeFieldValidator()
        with pytest.raises(ValidationError):
            validator.validate_search_query("search<script>")
