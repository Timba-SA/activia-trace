"""AuditContext dependency — extracts audit-relevant fields from request and JWT."""

import uuid

from fastapi import Depends, Request

from app.core.dependencies import get_current_user
from app.schemas.auth import CurrentUser


class AuditContext:
    """Holds audit metadata extracted from the current request and JWT.

    Normal session:
        actor_id = current_user.id
        impersonated_user_id = None

    Impersonation session:
        actor_id = impersonating_user_id (the real actor)
        impersonated_user_id = current_user.id (the target)
    """

    def __init__(
        self,
        actor_id: uuid.UUID,
        impersonated_user_id: uuid.UUID | None,
        ip: str | None,
        user_agent: str | None,
        tenant_id: uuid.UUID,
    ) -> None:
        self.actor_id = actor_id
        self.impersonated_user_id = impersonated_user_id
        self.ip = ip
        self.user_agent = user_agent
        self.tenant_id = tenant_id


async def get_audit_context(
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
) -> AuditContext:
    """Extract audit context from the request and JWT.

    Detects impersonation via JWT claims.
    """
    actor_id = current_user.id
    impersonated_user_id: uuid.UUID | None = None

    if hasattr(request.state, "impersonation") and request.state.impersonation:
        actor_id = uuid.UUID(request.state.impersonating_user_id)
        impersonated_user_id = current_user.id

    client_host = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    return AuditContext(
        actor_id=actor_id,
        impersonated_user_id=impersonated_user_id,
        ip=client_host,
        user_agent=user_agent,
        tenant_id=current_user.tenant_id,
    )
