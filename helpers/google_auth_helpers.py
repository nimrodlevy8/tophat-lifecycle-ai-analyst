"""Google authentication helpers for Drive/Docs MCP operations.

Utility functions to check, validate, and troubleshoot Google Workspace MCP
authentication before attempting Drive uploads or Docs operations.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, Tuple


def get_token_path() -> Path:
    """Return the path to the Google Docs MCP token file."""
    return Path.home() / '.claude' / 'mcp-servers' / 'google-docs-mcp-server' / 'token.json'


def get_credentials_path() -> Path:
    """Return the path to the Google Docs MCP credentials file."""
    return Path.home() / '.claude' / 'mcp-servers' / 'google-docs-mcp-server' / 'credentials.json'


def check_auth_status() -> Dict[str, any]:
    """Check Google Workspace MCP authentication status.

    Returns:
        Dictionary with auth status details:
        - exists: bool - Whether token file exists
        - valid: bool - Whether token is valid (not expired)
        - expired: bool - Whether token is expired
        - hours_remaining: float - Hours until expiry (if valid)
        - has_refresh_token: bool - Whether refresh token is present
        - scopes: list - Configured scopes
        - missing_scopes: list - Required scopes that are missing
        - error: str - Error message if something went wrong
    """
    token_path = get_token_path()

    result = {
        'exists': False,
        'valid': False,
        'expired': False,
        'hours_remaining': 0,
        'has_refresh_token': False,
        'scopes': [],
        'missing_scopes': [],
        'error': None
    }

    if not token_path.exists():
        result['error'] = f"Token file not found at {token_path}"
        return result

    try:
        with open(token_path, 'r') as f:
            token = json.load(f)

        result['exists'] = True
        result['has_refresh_token'] = 'refresh_token' in token
        result['scopes'] = token.get('scopes', [])

        # Check required scopes
        required_scopes = [
            'https://www.googleapis.com/auth/documents',
            'https://www.googleapis.com/auth/drive.file'
        ]
        result['missing_scopes'] = [
            s for s in required_scopes if s not in result['scopes']
        ]

        # Check expiry
        if 'expiry' in token:
            expiry = datetime.fromisoformat(token['expiry'].replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)

            result['expired'] = expiry < now
            result['valid'] = not result['expired']

            if not result['expired']:
                hours = (expiry - now).total_seconds() / 3600
                result['hours_remaining'] = round(hours, 1)
        else:
            result['error'] = "Token file missing expiry timestamp"

        return result

    except json.JSONDecodeError as e:
        result['error'] = f"Token file is not valid JSON: {e}"
        return result
    except Exception as e:
        result['error'] = f"Error reading token: {e}"
        return result


def check_credentials_exist() -> Tuple[bool, Optional[str]]:
    """Check if OAuth2 credentials file exists.

    Returns:
        Tuple of (exists: bool, error_message: str or None)
    """
    creds_path = get_credentials_path()

    if not creds_path.exists():
        return False, f"credentials.json not found at {creds_path}"

    try:
        with open(creds_path, 'r') as f:
            creds = json.load(f)

        # Verify it has the right structure
        if 'installed' not in creds and 'web' not in creds:
            return False, "credentials.json missing 'installed' or 'web' section"

        return True, None

    except json.JSONDecodeError as e:
        return False, f"credentials.json is not valid JSON: {e}"
    except Exception as e:
        return False, f"Error reading credentials: {e}"


def format_auth_status(status: Dict[str, any]) -> str:
    """Format authentication status as human-readable string.

    Args:
        status: Output from check_auth_status()

    Returns:
        Formatted status message with color indicators
    """
    if status['error']:
        return f"✗ {status['error']}"

    if not status['exists']:
        return "✗ Token file not found. Run: authorize_google_docs()"

    lines = []

    if status['valid']:
        lines.append(f"✓ Authentication valid ({status['hours_remaining']} hours remaining)")
    elif status['expired']:
        if status['has_refresh_token']:
            lines.append("⚠ Token expired (will auto-refresh on next use)")
        else:
            lines.append("✗ Token expired and no refresh token. Run: authorize_google_docs()")

    if status['missing_scopes']:
        lines.append(f"✗ Missing scopes: {', '.join(status['missing_scopes'])}")
        lines.append("  → Re-authorize with full permissions")

    if not status['has_refresh_token']:
        lines.append("⚠ No refresh token (cannot auto-refresh when expired)")

    return "\n".join(lines) if lines else "✓ Authentication configured"


def should_reauthorize(status: Dict[str, any]) -> bool:
    """Determine if re-authorization is needed.

    Args:
        status: Output from check_auth_status()

    Returns:
        True if user should run authorize_google_docs()
    """
    if not status['exists']:
        return True

    if status['expired'] and not status['has_refresh_token']:
        return True

    if status['missing_scopes']:
        return True

    return False


def print_auth_diagnostics(verbose: bool = False) -> None:
    """Print comprehensive auth diagnostics to console.

    Args:
        verbose: If True, include token file paths and raw data
    """
    print("=" * 60)
    print("Google Workspace MCP - Authentication Status")
    print("=" * 60)
    print()

    # Check credentials
    creds_exist, creds_error = check_credentials_exist()
    print("Credentials (OAuth2 Client):")
    if creds_exist:
        print("  ✓ credentials.json found")
        if verbose:
            print(f"    Path: {get_credentials_path()}")
    else:
        print(f"  ✗ {creds_error}")
    print()

    # Check token
    status = check_auth_status()
    print("Token Status:")
    print("  " + format_auth_status(status).replace("\n", "\n  "))

    if verbose and status['exists']:
        print(f"\n  Token path: {get_token_path()}")
        print(f"  Scopes: {len(status['scopes'])}")
        for scope in status['scopes']:
            print(f"    - {scope}")

    print()
    print("=" * 60)

    # Recommendations
    if should_reauthorize(status):
        print("ACTION REQUIRED:")
        print("  Run: mcp__google-docs__authorize_google_docs()")
        print("  This will open a browser for Google sign-in")
    elif status['expired'] and status['has_refresh_token']:
        print("INFO:")
        print("  Token will auto-refresh on next Google API call")
    else:
        print("STATUS: Ready for Google Drive/Docs operations")

    print("=" * 60)


# Convenience function for quick inline checks
def ensure_auth_valid() -> None:
    """Check auth and raise exception if action is needed.

    Raises:
        RuntimeError: If authentication is invalid and manual action is required
    """
    status = check_auth_status()

    if should_reauthorize(status):
        raise RuntimeError(
            f"Google authentication required. {format_auth_status(status)}\n"
            "Run: mcp__google-docs__authorize_google_docs()"
        )

    if status['expired'] and status['has_refresh_token']:
        # This is okay - will auto-refresh
        print("⚠ Token expired but will auto-refresh on first API call")


if __name__ == '__main__':
    # Run diagnostics when executed directly
    import sys
    verbose = '--verbose' in sys.argv or '-v' in sys.argv
    print_auth_diagnostics(verbose=verbose)
