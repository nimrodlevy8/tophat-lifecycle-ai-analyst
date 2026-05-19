"""Security validator — enforces Scopely domain boundaries.

Usage:
    from helpers.security_validator import validate_scopely_email, validate_no_external_urls
    validate_scopely_email("user@scopely.com")  # OK
    validate_scopely_email("user@gmail.com")    # raises SecurityError

Also usable as CLI:
    python helpers/security_validator.py --email user@scopely.com
    python helpers/security_validator.py --url https://drive.google.com/...
"""

import re
import sys
from urllib.parse import urlparse


class SecurityError(Exception):
    pass


ALLOWED_DOMAINS = [
    'scopely.com',
]

ALLOWED_URL_HOSTS = [
    'drive.google.com',
    'docs.google.com',
    'slides.google.com',
    'sheets.google.com',
    'googleapis.com',
    'storage.googleapis.com',
    'bigquery.googleapis.com',
    'cloud.google.com',
    'accounts.google.com',
    'oauth2.googleapis.com',
    'scopely.atlassian.net',
    'hex.tech',
    'app.hex.tech',
    'learn.hex.tech',
]


def validate_scopely_email(email: str) -> str:
    """Validate that an email belongs to the scopely.com domain.

    Args:
        email: Email address to validate.

    Returns:
        The original email if validation passes.

    Raises:
        SecurityError: If the email is not @scopely.com.
    """
    if not email or not isinstance(email, str):
        raise SecurityError("Email is required and must be a string.")

    email_lower = email.strip().lower()

    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email_lower):
        raise SecurityError(f"Invalid email format: {email}")

    if not any(email_lower.endswith(f'@{domain}') for domain in ALLOWED_DOMAINS):
        raise SecurityError(
            f"Only @scopely.com emails allowed. Got: {email}. "
            f"Authentication and API calls must use Scopely domain accounts only."
        )

    return email


def validate_auth_email(email: str, context: str = "") -> str:
    """Validate email used for authentication/API calls is @scopely.com.

    Stricter than validate_scopely_email — also rejects empty/None.

    Args:
        email: Email used for authentication.
        context: Description of where this email is being used (for error messages).

    Returns:
        The validated email.

    Raises:
        SecurityError: If the email is not @scopely.com or is missing.
    """
    if not email:
        raise SecurityError(
            f"Authentication email is required{f' for {context}' if context else ''}. "
            f"Must be an @scopely.com address."
        )
    return validate_scopely_email(email)


def validate_no_external_urls(url: str) -> str:
    """Validate that a URL points to an allowed destination (Scopely services only).

    Args:
        url: URL to validate.

    Returns:
        The original URL if validation passes.

    Raises:
        SecurityError: If the URL points to a non-allowed host.
    """
    if not url or not isinstance(url, str):
        raise SecurityError("URL is required and must be a string.")

    parsed = urlparse(url)
    host = parsed.hostname

    if not host:
        raise SecurityError(f"Cannot parse host from URL: {url}")

    if any(host == allowed or host.endswith(f'.{allowed}') for allowed in ALLOWED_URL_HOSTS):
        return url

    raise SecurityError(
        f"URL host not in allowlist: {host}. "
        f"Data must stay within Scopely boundaries. "
        f"Allowed: {', '.join(ALLOWED_URL_HOSTS)}"
    )


def validate_mcp_email_param(tool_input: dict) -> str | None:
    """Extract and validate email from MCP tool input parameters.

    Checks common parameter names used by Google Workspace and Atlassian MCP tools.

    Args:
        tool_input: The tool_input dict from hook stdin JSON.

    Returns:
        The validated email, or None if no email parameter found.

    Raises:
        SecurityError: If a non-scopely email is found.
    """
    email_keys = [
        'user_google_email',
        'email',
        'emailAddress',
        'user_email',
        'account',
    ]

    for key in email_keys:
        email = tool_input.get(key)
        if email:
            return validate_scopely_email(email)

    return None


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python security_validator.py --email <address>")
        print("       python security_validator.py --url <url>")
        sys.exit(1)

    flag = sys.argv[1]
    value = sys.argv[2]

    try:
        if flag == '--email':
            validate_scopely_email(value)
            print(f"OK: {value} is a valid Scopely email.")
        elif flag == '--url':
            validate_no_external_urls(value)
            print(f"OK: {value} is an allowed URL.")
        else:
            print(f"Unknown flag: {flag}", file=sys.stderr)
            sys.exit(1)
        sys.exit(0)
    except SecurityError as e:
        print(f"BLOCKED: {e}", file=sys.stderr)
        sys.exit(1)
