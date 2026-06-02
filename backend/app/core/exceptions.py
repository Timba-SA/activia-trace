class AppError(Exception):
    """Base exception for all application-level errors."""


class NotFoundError(AppError):
    """Raised when a requested resource is not found (404)."""


class EncryptionError(AppError):
    """Raised when encryption or decryption fails."""


class TenantScopeError(AppError):
    """Raised when a tenant-scoped operation lacks a valid tenant context."""
