"""Credential sanitizer — strips secrets before any output.

Usage:
    from helpers.credential_sanitizer import sanitize
    safe_text = sanitize(text_with_credentials)

Also usable as CLI:
    echo "password=abc123" | python helpers/credential_sanitizer.py
    python helpers/credential_sanitizer.py --file config.yaml
    python helpers/credential_sanitizer.py "api_key=sk-12345"
"""

import re
import sys


PATTERNS = [
    # Key-value patterns (password=..., token: ..., etc.)
    (r'(password["\']?\s*[:=]\s*["\']?)([^"\'\}\s,;\n]+)', r'\1***'),
    (r'(passwd["\']?\s*[:=]\s*["\']?)([^"\'\}\s,;\n]+)', r'\1***'),
    (r'(api[_-]?key["\']?\s*[:=]\s*["\']?)([^"\'\}\s,;\n]+)', r'\1***'),
    (r'(api[_-]?secret["\']?\s*[:=]\s*["\']?)([^"\'\}\s,;\n]+)', r'\1***'),
    (r'(secret[_-]?key["\']?\s*[:=]\s*["\']?)([^"\'\}\s,;\n]+)', r'\1***'),
    (r'(access[_-]?key["\']?\s*[:=]\s*["\']?)([^"\'\}\s,;\n]+)', r'\1***'),
    (r'(access[_-]?token["\']?\s*[:=]\s*["\']?)([^"\'\}\s,;\n]+)', r'\1***'),
    (r'(auth[_-]?token["\']?\s*[:=]\s*["\']?)([^"\'\}\s,;\n]+)', r'\1***'),
    (r'(refresh[_-]?token["\']?\s*[:=]\s*["\']?)([^"\'\}\s,;\n]+)', r'\1***'),
    (r'(client[_-]?secret["\']?\s*[:=]\s*["\']?)([^"\'\}\s,;\n]+)', r'\1***'),
    (r'(client[_-]?id["\']?\s*[:=]\s*["\']?)([^"\'\}\s,;\n]+)', r'\1***'),
    (r'(private[_-]?key["\']?\s*[:=]\s*["\']?)([^"\'\}\s,;\n]+)', r'\1***'),
    (r'(token["\']?\s*[:=]\s*["\']?)([^"\'\}\s,;\n]{20,})', r'\1***'),

    # Bearer tokens in headers
    (r'(Authorization:\s*Bearer\s+)(\S+)', r'\1***'),
    (r'(Bearer\s+)([A-Za-z0-9._\-]{20,})', r'\1***'),

    # Google OAuth tokens (ya29.*, 1//...)
    (r'\bya29\.[A-Za-z0-9_\-]{20,}', '***OAUTH_TOKEN***'),
    (r'\b1//[A-Za-z0-9_\-]{20,}', '***REFRESH_TOKEN***'),

    # GCP service account private keys
    (r'-----BEGIN (RSA )?PRIVATE KEY-----[\s\S]*?-----END (RSA )?PRIVATE KEY-----',
     '***PRIVATE_KEY***'),

    # AWS-style keys
    (r'\b(AKIA[0-9A-Z]{16})\b', '***AWS_KEY***'),
    (r'\b([A-Za-z0-9/+=]{40})\b(?=.*secret)', '***AWS_SECRET***'),

    # Generic long hex/base64 tokens (40+ chars, likely secrets)
    (r'(secret|token|key|credential)["\']?\s*[:=]\s*["\']?([A-Za-z0-9+/=_\-]{40,})',
     r'\1=***REDACTED***'),

    # Connection strings with passwords
    (r'(://[^:]+:)([^@]+)(@)', r'\1***\3'),

    # JSON Web Tokens
    (r'\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\b',
     '***JWT***'),
]

COMPILED_PATTERNS = [(re.compile(p, re.IGNORECASE), r) for p, r in PATTERNS]


def sanitize(text: str) -> str:
    """Strip credentials and secrets from text before output.

    Applies regex patterns to redact passwords, tokens, API keys,
    private keys, JWTs, OAuth tokens, and connection string credentials.

    Args:
        text: Raw text that may contain credentials.

    Returns:
        Sanitized text with credentials replaced by *** markers.
    """
    if not text:
        return text

    result = text
    for pattern, replacement in COMPILED_PATTERNS:
        result = pattern.sub(replacement, result)

    return result


def sanitize_dict(d: dict) -> dict:
    """Sanitize all string values in a dictionary (recursive).

    Args:
        d: Dictionary that may contain credential values.

    Returns:
        New dictionary with all string values sanitized.
    """
    SENSITIVE_KEYS = {
        'password', 'passwd', 'secret', 'token', 'api_key', 'apikey',
        'api_secret', 'access_token', 'refresh_token', 'auth_token',
        'client_secret', 'private_key', 'credentials', 'connection_string',
    }

    result = {}
    for k, v in d.items():
        if isinstance(v, dict):
            result[k] = sanitize_dict(v)
        elif isinstance(v, list):
            result[k] = [sanitize_dict(i) if isinstance(i, dict)
                         else '***' if isinstance(i, str) and k.lower() in SENSITIVE_KEYS
                         else i for i in v]
        elif isinstance(v, str):
            if k.lower() in SENSITIVE_KEYS:
                result[k] = '***'
            else:
                result[k] = sanitize(v)
        else:
            result[k] = v

    return result


def is_likely_credential(text: str) -> bool:
    """Check if a string looks like it might be a credential/secret.

    Useful for pre-screening before deciding whether to display something.

    Args:
        text: String to check.

    Returns:
        True if the string matches credential-like patterns.
    """
    if not text or len(text) < 16:
        return False

    if text.startswith('ya29.') or text.startswith('1//'):
        return True
    if text.startswith('eyJ') and text.count('.') == 2:
        return True
    if text.startswith('AKIA') and len(text) == 20:
        return True
    if re.match(r'^[A-Za-z0-9+/=_\-]{40,}$', text):
        return True
    if '-----BEGIN' in text and 'PRIVATE KEY' in text:
        return True

    return False


if __name__ == '__main__':
    if len(sys.argv) == 1:
        # Read from stdin
        text = sys.stdin.read()
        print(sanitize(text), end='')
        sys.exit(0)

    if sys.argv[1] == '--file':
        with open(sys.argv[2], 'r', encoding='utf-8') as f:
            text = f.read()
        print(sanitize(text), end='')
        sys.exit(0)

    # Treat remaining args as text to sanitize
    text = ' '.join(sys.argv[1:])
    print(sanitize(text))
    sys.exit(0)
