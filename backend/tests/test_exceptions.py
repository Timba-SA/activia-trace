from app.core.exceptions import AppError, EncryptionError, NotFoundError, TenantScopeError


class TestExceptions:
    def test_app_error_is_base(self):
        assert issubclass(NotFoundError, AppError)
        assert issubclass(EncryptionError, AppError)
        assert issubclass(TenantScopeError, AppError)

    def test_app_error_is_exception(self):
        assert issubclass(AppError, Exception)

    def test_not_found_error_message(self):
        exc = NotFoundError("Resource not found")
        assert str(exc) == "Resource not found"

    def test_encryption_error_message(self):
        exc = EncryptionError("Encryption failed")
        assert str(exc) == "Encryption failed"

    def test_tenant_scope_error_message(self):
        exc = TenantScopeError("No tenant")
        assert str(exc) == "No tenant"
