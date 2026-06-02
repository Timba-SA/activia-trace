"""Security primitives: AES-256-GCM, Argon2id, JWT, refresh tokens."""

import base64
import hashlib
import os
import uuid

from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from jose import JWTError, jwt

from app.core.config import get_settings
from app.core.exceptions import EncryptionError

_NONCE_LENGTH = 12
_argon2_hasher = PasswordHasher()


def _get_aes_key() -> bytes:
    return get_settings().encryption_key.encode("utf-8")


def encrypt_value(plaintext: str) -> str:
    """Encrypt a plaintext string with AES-256-GCM.

    Returns base64-encoded (nonce + ciphertext + tag).
    Each call produces a distinct ciphertext due to random nonce.
    """
    key = _get_aes_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(_NONCE_LENGTH)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    return base64.b64encode(nonce + ciphertext).decode("utf-8")


def decrypt_value(ciphertext_b64: str) -> str:
    """Decrypt a base64-encoded AES-256-GCM ciphertext string.

    Raises EncryptionError if the tag is invalid or data is malformed.
    """
    key = _get_aes_key()
    aesgcm = AESGCM(key)
    try:
        raw = base64.b64decode(ciphertext_b64)
    except (base64.binascii.Error, ValueError) as exc:
        raise EncryptionError("Invalid base64-encoded ciphertext") from exc
    if len(raw) < _NONCE_LENGTH:
        raise EncryptionError("Ciphertext too short")
    nonce = raw[:_NONCE_LENGTH]
    ciphertext = raw[_NONCE_LENGTH:]
    try:
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    except Exception as exc:
        raise EncryptionError("Decryption failed — invalid key or tampered data") from exc
    return plaintext.decode("utf-8")


def hash_password(password: str) -> str:
    return _argon2_hasher.hash(password)


def verify_password(password: str, hash: str) -> bool:
    try:
        return _argon2_hasher.verify(hash, password)
    except Exception:
        return False


def create_access_token(
    user_data: dict, expire_minutes: int | None = None
) -> str:
    settings = get_settings()
    to_encode = user_data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expire_minutes or settings.access_token_expire_minutes
    )
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(to_encode, settings.secret_key, algorithm="HS256")


def create_temp_token(user_id: uuid.UUID, tenant_id: uuid.UUID) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(minutes=5)
    payload = {
        "sub": str(user_id),
        "tenant_id": str(tenant_id),
        "pending_2fa": True,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def decode_token(token: str) -> dict:
    settings = get_settings()
    try:
        return jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    except JWTError as exc:
        raise ValueError("Invalid or expired token") from exc


def generate_refresh_token() -> tuple[str, str]:
    raw = os.urandom(32).hex()
    hash_val = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return raw, hash_val
