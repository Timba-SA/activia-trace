"""@audit_action decorator — register auditable actions on service methods."""

import functools
import logging
import uuid

logger = logging.getLogger(__name__)


def audit_action(code: str, extra_fields: list[str] | None = None):
    """Decorator that logs an audit entry after the decorated method succeeds.

    Resolves actor_id, tenant_id, ip, user_agent from the first AuditContext
    argument of the decorated method. Captures the return value to determine
    filas_afectadas.

    Audit errors are suppressed — they do NOT break the primary operation.
    Exceptions from the decorated method ARE propagated (no audit for failures).

    Usage:
        @audit_action("PADRON_CARGAR")
        async def importar_padron(self, ctx: AuditContext, ...):
            ...
            return {"filas_afectadas": 42}
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Resolve AuditContext from positional or keyword args
            audit_ctx = None
            audit_service = None
            for arg in args:
                if hasattr(arg, "actor_id") and hasattr(arg, "tenant_id"):
                    audit_ctx = arg
                    break
            if audit_ctx is None:
                for val in kwargs.values():
                    if hasattr(val, "actor_id") and hasattr(val, "tenant_id"):
                        audit_ctx = val
                        break

            # Resolve AuditService from kwargs or args
            if "audit_service" in kwargs:
                audit_service = kwargs["audit_service"]

            # Execute the decorated method
            result = await func(*args, **kwargs)

            # Log audit if we have context and service
            if audit_ctx is not None and audit_service is not None:
                try:
                    filas_afectadas = 0
                    if isinstance(result, dict) and "filas_afectadas" in result:
                        filas_afectadas = result["filas_afectadas"]
                    elif isinstance(result, int):
                        filas_afectadas = result

                    extra = {}
                    if extra_fields and isinstance(result, dict):
                        for field in extra_fields:
                            if field in result:
                                extra[field] = result[field]

                    detalle = extra if extra else None

                    await audit_service.log(
                        accion=code,
                        actor_id=audit_ctx.actor_id,
                        tenant_id=audit_ctx.tenant_id,
                        materia_id=getattr(audit_ctx, "materia_id", None),
                        impersonado_id=audit_ctx.impersonated_user_id,
                        filas_afectadas=filas_afectadas,
                        detalle=detalle,
                        ip=audit_ctx.ip,
                        user_agent=audit_ctx.user_agent,
                    )
                except Exception:
                    logger.exception("Audit logging failed (suppressed)")
            return result
        return wrapper
    return decorator
