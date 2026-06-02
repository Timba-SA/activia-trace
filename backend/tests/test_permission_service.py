"""Unit tests for PermissionService and has_permission utility."""

from app.services.permission_service import has_permission


class TestHasPermission:
    def test_single_role_permission_found(self):
        permissions = {"usuarios:list", "usuarios:create"}
        assert has_permission(permissions, "usuarios:list") is True

    def test_union_of_roles_permission_found(self):
        permissions = {"usuarios:list", "usuarios:create", "roles:gestionar"}
        assert has_permission(permissions, "roles:gestionar") is True

    def test_missing_permission_returns_false(self):
        permissions = {"usuarios:list", "usuarios:create"}
        assert has_permission(permissions, "roles:gestionar") is False

    def test_empty_permissions_returns_false(self):
        permissions: set[str] = set()
        assert has_permission(permissions, "usuarios:list") is False

    def test_case_sensitive_match(self):
        permissions = {"Usuarios:List", "usuarios:list"}
        assert has_permission(permissions, "usuarios:list") is True
        assert has_permission(permissions, "Usuarios:List") is True
        assert has_permission(permissions, "USUARIOS:LIST") is False
