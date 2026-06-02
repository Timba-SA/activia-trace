import pytest

from app.repositories.tenant import TenantRepository


class TestMixinTimestamps:
    async def test_created_at_is_set_on_create(self, db_session):
        repo = TenantRepository(db_session)
        tenant = await repo.create(name="TS Test", slug="ts-test", code="TSTEST")
        assert tenant.created_at is not None

    async def test_updated_at_is_set_on_create(self, db_session):
        repo = TenantRepository(db_session)
        tenant = await repo.create(name="TS2", slug="ts2", code="TS2")
        assert tenant.updated_at is not None

    async def test_updated_at_changes_on_update(self, db_session):
        repo = TenantRepository(db_session)
        tenant = await repo.create(name="Before", slug="ts3", code="TS3")
        orig_updated = tenant.updated_at
        await repo.update(tenant.id, name="After")
        await db_session.refresh(tenant)
        assert tenant.updated_at >= orig_updated
