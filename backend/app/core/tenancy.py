"""Tenant resolution and isolation utilities.

Provides the tenant context used by dependencies and repositories
to scope all operations to the current tenant.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import TenantScopeError
from app.models.tenant import Tenant
from app.repositories.tenant import TenantRepository


async def resolve_tenant_from_slug(session: AsyncSession, slug: str) -> Tenant:
    """Resolve an active tenant by slug.

    Raises NotFoundError if no matching active tenant exists.
    """
    repo = TenantRepository(session)
    tenant = await repo.get_by_slug(slug)
    if not tenant.is_active:
        raise TenantScopeError(f"Tenant '{slug}' is not active")
    return tenant


async def resolve_tenant_from_code(session: AsyncSession, code: str) -> Tenant:
    """Resolve an active tenant by code."""
    repo = TenantRepository(session)
    tenant = await repo.get_by_code(code)
    if not tenant.is_active:
        raise TenantScopeError(f"Tenant with code '{code}' is not active")
    return tenant
