import os

import pytest
from pydantic import ValidationError

from app.core.config import Settings


class TestSettings:
    def test_valid_env_succeeds(self):
        settings = Settings(
            _env_file=None,
            database_url="postgresql+asyncpg://user:pass@localhost/db",
            secret_key="this-is-a-32-char-secret-key-123456",
            encryption_key="this-is-a-32-char-encrypt-key!!!",
            access_token_expire_minutes=30,
        )
        assert settings.database_url == "postgresql+asyncpg://user:pass@localhost/db"
        assert settings.access_token_expire_minutes == 30

    def test_access_token_default_is_15(self):
        settings = Settings(
            _env_file=None,
            database_url="postgresql+asyncpg://user:pass@localhost/db",
            secret_key="this-is-a-32-char-secret-key-123456",
            encryption_key="this-is-a-32-char-encrypt-key!!!",
        )
        assert settings.access_token_expire_minutes == 15

    def test_missing_required_var_raises(self):
        saved = os.environ.pop("ENCRYPTION_KEY", None)
        try:
            with pytest.raises(ValidationError):
                Settings(
                    _env_file=None,
                    database_url="postgresql+asyncpg://user:pass@localhost/db",
                    secret_key="this-is-a-32-char-secret-key-123456",
                )
        finally:
            if saved is not None:
                os.environ["ENCRYPTION_KEY"] = saved

    def test_invalid_type_raises(self):
        with pytest.raises(ValidationError):
            Settings(
                _env_file=None,
                database_url="postgresql+asyncpg://user:pass@localhost/db",
                secret_key="this-is-a-32-char-secret-key-123456",
                encryption_key="this-is-a-32-char-encrypt-key!!!",
                access_token_expire_minutes="not-an-int",
            )

    def test_short_secret_key_raises(self):
        with pytest.raises(ValidationError):
            Settings(
                _env_file=None,
                database_url="postgresql+asyncpg://user:pass@localhost/db",
                secret_key="short",
                encryption_key="this-is-a-32-char-encrypt-key!!!",
            )

    def test_wrong_length_encryption_key_raises(self):
        with pytest.raises(ValidationError):
            Settings(
                _env_file=None,
                database_url="postgresql+asyncpg://user:pass@localhost/db",
                secret_key="this-is-a-32-char-secret-key-123456",
                encryption_key="too-short",
            )
