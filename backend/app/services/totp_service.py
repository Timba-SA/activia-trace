import pyotp

from app.core.security import decrypt_value, encrypt_value


class TOTPService:
    def generate_secret(self) -> tuple[str, str]:
        secret = pyotp.random_base32()
        provisioning_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name="active-trace",
            issuer_name="active-trace",
        )
        encrypted = encrypt_value(secret)
        return secret, encrypted, provisioning_uri

    def verify_code(self, encrypted_secret: str, code: str) -> bool:
        secret = decrypt_value(encrypted_secret)
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)
