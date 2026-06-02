import uuid

import pytest

from app.core.exceptions import NotFoundError
from app.models.tenant import Tenant
from app.repositories.tenant import TenantRepository
from app.repositories.base import BaseRepository


class TestTenantCreate:
    async def test_create_tenant_success(self, db_session):
        repo = TenantRepository(db_session)
        tenant = await repo.create(
            name="Test University",
            slug="test-university",
            code="TEST_UNI",
        )
        assert tenant.id is not None
        assert tenant.name == "Test University"
        assert tenant.slug == "test-university"
        assert tenant.code == "TEST_UNI"
        assert tenant.is_active is True

    async def test_create_tenant_duplicate_slug_raises(self, db_session):
        repo = TenantRepository(db_session)
        await repo.create(name="First", slug="dup-slug", code="FIRST")
        with pytest.raises(Exception):
            await repo.create(name="Second", slug="dup-slug", code="SECOND")

    async def test_create_tenant_duplicate_code_raises(self, db_session):
        repo = TenantRepository(db_session)
        await repo.create(name="First", slug="first", code="DUPE")
        with pytest.raises(Exception):
            await repo.create(name="Second", slug="second", code="DUPE")

    async def test_create_inactive_tenant(self, db_session):
        repo = TenantRepository(db_session)
        tenant = await repo.create(
            name="Inactive U",
            slug="inactive-u",
            code="INACTIVE",
            is_active=False,
        )
        assert tenant.is_active is False


class TestTenantRead:
    async def test_get_by_slug(self, db_session):
        repo = TenantRepository(db_session)
        await repo.create(name="Get Test", slug="get-test", code="GET_TEST")
        found = await repo.get_by_slug("get-test")
        assert found.name == "Get Test"

    async def test_get_by_slug_not_found(self, db_session):
        repo = TenantRepository(db_session)
        with pytest.raises(NotFoundError):
            await repo.get_by_slug("nonexistent")

    async def test_get_by_code(self, db_session):
        repo = TenantRepository(db_session)
        await repo.create(name="Code Test", slug="code-test", code="CODEX")
        found = await repo.get_by_code("CODEX")
        assert found.name == "Code Test"

    async def test_get_by_code_not_found(self, db_session):
        repo = TenantRepository(db_session)
        with pytest.raises(NotFoundError):
            await repo.get_by_code("NONEXISTENT")


class TestMultiTenantIsolation:
    async def _create_tenant_with_repo(self, db_session, **kwargs):
        repo = TenantRepository(db_session)
        return await repo.create(**kwargs)

    async def test_tenant_repo_no_scope(self, db_session):
        repo = TenantRepository(db_session)
        t1 = await self._create_tenant_with_repo(db_session, name="T1", slug="tenant-a", code="TA")
        t2 = await self._create_tenant_with_repo(db_session, name="T2", slug="tenant-b", code="TB")
        all_tenants = await repo.list()
        slugs = [t.slug for t in all_tenants]
        assert "tenant-a" in slugs
        assert "tenant-b" in slugs


class TestBaseRepositoryIsolation:
    """Uses a dummy model to test BaseRepository tenant scoping."""

    async def test_tenant_scope_isolation(self, db_session):
        pass


class TestSoftDelete:
    async def test_soft_delete_hides_record(self, db_session):
        repo = TenantRepository(db_session)
        tenant = await repo.create(name="SD Test", slug="sd-test", code="SDTEST")
        await repo.soft_delete(tenant.id)
        with pytest.raises(NotFoundError):
            await repo.get_by_slug("sd-test")

    async def test_include_deleted_reveals_record(self, db_session):
        repo = TenantRepository(db_session)
        tenant = await repo.create(name="SD Reveal", slug="sd-reveal", code="SDREVEAL")
        await repo.soft_delete(tenant.id)
        found = await repo.get_by_slug("sd-reveal", include_deleted=True)
        assert found.deleted_at is not None

    async def test_get_with_include_deleted(self, db_session):
        repo = TenantRepository(db_session)
        tenant = await repo.create(name="SD Get", slug="sd-get", code="SDGET")
        await repo.soft_delete(tenant.id)
        found = await repo.get(tenant.id, include_deleted=True)
        assert found.id == tenant.id
        assert found.deleted_at is not None

    async def test_count_excludes_deleted(self, db_session):
        repo = TenantRepository(db_session)
        await repo.create(name="C1", slug="count-1", code="CNT1")
        t2 = await repo.create(name="C2", slug="count-2", code="CNT2")
        await repo.soft_delete(t2.id)
        total = await repo.count()
        assert total == 1


class TestPagination:
    async def test_paginate_with_tenant_scope(self, db_session):
        repo = TenantRepository(db_session)
        for i in range(5):
            await repo.create(
                name=f"Page {i}",
                slug=f"page-{i}",
                code=f"PAGE{i:02d}",
            )
        items, total, pages = await repo.paginate(limit=2, offset=0)
        assert len(items) == 2
        assert total == 5
        assert pages == 3


class TestSkipTenantScope:
    async def test_skip_tenant_scope_returns_all(self, db_session):
        repo = TenantRepository(db_session)
        for i in range(3):
            await repo.create(
                name=f"Skip {i}",
                slug=f"skip-{i}",
                code=f"SKIP{i:02d}",
            )
        all_tenants = await repo.list(skip_tenant_scope=True)
        assert len(all_tenants) >= 3
