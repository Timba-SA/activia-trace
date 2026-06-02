import uuid

import os

import pytest

os.environ.setdefault("SECRET_KEY", "abcd1234abcd1234abcd1234abcd1234")
os.environ.setdefault("ENCRYPTION_KEY", "abcd1234abcd1234abcd1234abcd1234")

from app.core.config import get_settings
from app.core.exceptions import EncryptionError
from app.core.security import (
    create_access_token,
    create_temp_token,
    decode_token,
    decrypt_value,
    encrypt_value,
    generate_refresh_token,
    hash_password,
    verify_password,
)


class TestArgon2id:
    def test_hash_and_verify(self):
        password = "secure-password-123"
        hashed = hash_password(password)
        assert hashed != password
        assert verify_password(password, hashed) is True

    def test_wrong_password_fails(self):
        hashed = hash_password("real-password")
        assert verify_password("wrong-password", hashed) is False

    def test_same_password_different_hashes(self):
        password = "same-password"
        h1 = hash_password(password)
        h2 = hash_password(password)
        assert h1 != h2


class TestJWT:
    def test_create_and_decode_access_token(self):
        user_id = uuid.uuid4()
        tenant_id = uuid.uuid4()
        token = create_access_token(
            user_data={
                "sub": str(user_id),
                "tenant_id": str(tenant_id),
                "roles": ["admin"],
            }
        )
        payload = decode_token(token)
        assert payload["sub"] == str(user_id)
        assert payload["tenant_id"] == str(tenant_id)
        assert payload["roles"] == ["admin"]
        assert "exp" in payload
        assert "iat" in payload

    def test_temp_token_has_pending_2fa(self):
        user_id = uuid.uuid4()
        tenant_id = uuid.uuid4()
        token = create_temp_token(user_id, tenant_id)
        payload = decode_token(token)
        assert payload["sub"] == str(user_id)
        assert payload["tenant_id"] == str(tenant_id)
        assert payload["pending_2fa"] is True

    def test_invalid_token_raises(self):
        with pytest.raises(Exception):
            decode_token("invalid-token")

    def test_expired_token_raises(self):
        user_id = uuid.uuid4()
        tenant_id = uuid.uuid4()
        token = create_access_token(
            user_data={
                "sub": str(user_id),
                "tenant_id": str(tenant_id),
                "roles": [],
            },
            expire_minutes=-1,
        )
        with pytest.raises(Exception):
            decode_token(token)


class TestRefreshToken:
    def test_generate_returns_raw_and_hash(self):
        raw, hash_val = generate_refresh_token()
        assert len(raw) == 64
        assert len(hash_val) == 64
        assert raw != hash_val

    def test_generate_unique_tokens(self):
        raw1, _ = generate_refresh_token()
        raw2, _ = generate_refresh_token()
        assert raw1 != raw2


class TestAES256GCM:
    def test_round_trip(self):
        plaintext = "hello-world-123"
        encrypted = encrypt_value(plaintext)
        decrypted = decrypt_value(encrypted)
        assert decrypted == plaintext

    def test_same_plaintext_different_ciphertext(self):
        plaintext = "same-data"
        encrypted_1 = encrypt_value(plaintext)
        encrypted_2 = encrypt_value(plaintext)
        assert encrypted_1 != encrypted_2

    def test_empty_string(self):
        plaintext = ""
        encrypted = encrypt_value(plaintext)
        decrypted = decrypt_value(encrypted)
        assert decrypted == ""

    def test_decrypt_with_wrong_key_raises_error(self):
        plaintext = "secret-data"
        encrypted = encrypt_value(plaintext)
        orig_key = os.environ["ENCRYPTION_KEY"]
        get_settings.cache_clear()
        os.environ["ENCRYPTION_KEY"] = "yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"
        try:
            with pytest.raises(EncryptionError):
                decrypt_value(encrypted)
        finally:
            os.environ["ENCRYPTION_KEY"] = orig_key
            get_settings.cache_clear()

    def test_invalid_base64_raises_error(self):
        with pytest.raises(EncryptionError):
            decrypt_value("not-valid-base64!!!")
