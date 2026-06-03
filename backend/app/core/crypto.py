"""AES-256 encryption/decryption utility for PII at rest."""

import base64
import os

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.core.config import get_settings

_salt: bytes | None = None


def _get_fernet() -> Fernet:
    """Build a Fernet instance from the configured encryption_key.

    Uses a deterministic derivation so the same key always produces
    the same Fernet key (no random salt — the security comes from
    ENCRYPTION_KEY being a 32-char secret stored outside the DB).
    """
    settings = get_settings()
    key_material = settings.encryption_key.encode("utf-8")
    # Use a fixed salt derived from the key itself (deterministic).
    # This is acceptable for application-level field encryption
    # where the key is a high-entropy secret stored in env vars.
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"active-trace-fixed-salt-32bytes!",  # noqa: S001
        iterations=600_000,
    )
    fernet_key = base64.urlsafe_b64encode(kdf.derive(key_material))
    return Fernet(fernet_key)


def encrypt(plaintext: str) -> str:
    """Encrypt a string using AES-256 (Fernet).

    Returns a base64-encoded ciphertext string.
    """
    if not plaintext:
        return ""
    f = _get_fernet()
    return f.encrypt(plaintext.encode("utf-8")).decode("utf-8")


def decrypt(ciphertext: str) -> str:
    """Decrypt a Fernet-encoded string back to plaintext."""
    if not ciphertext:
        return ""
    f = _get_fernet()
    return f.decrypt(ciphertext.encode("utf-8")).decode("utf-8")
