"""Worker de comunicaciones — consume mensajes Pendiente y los envía (mock SMTP)."""

import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.repositories.comunicacion_repository import ComunicacionRepository
from app.core.crypto import decrypt

logger = logging.getLogger(__name__)


def _send_email(destinatario: str, asunto: str, cuerpo: str) -> bool:
    """Mock SMTP sender.

    En un change posterior se reemplaza por integración real con SMTP.
    Por ahora, loguea el envío y retorna True.
    """
    logger.info(
        "[MOCK SMTP] To: %s | Subject: %s | Body: %s",
        destinatario, asunto, cuerpo[:100],
    )
    return True


async def procesar_lote(limit: int = 50, engine: AsyncEngine | None = None) -> None:
    """Single worker cycle: fetch pending messages and process them.

    This is a separate async function so tests can call it directly
    without running the infinite loop.

    Args:
        limit: Max messages to process per cycle.
        engine: Optional engine to reuse (for testing). When None, a new
            engine is created and disposed.
    """
    settings = get_settings()
    should_dispose = engine is None
    if engine is None:
        engine = create_async_engine(settings.database_url, echo=False)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async with factory() as session:
        # We need tenant_id context. The worker processes messages
        # across all tenants by scanning with skip_tenant_scope.
        from app.models.comunicacion import Comunicacion
        from sqlalchemy import select

        stmt = (
            select(Comunicacion)
            .where(
                Comunicacion.estado == "Pendiente",
                Comunicacion.requiere_aprobacion.is_(False),
                Comunicacion.deleted_at.is_(None),
            )
            .limit(limit)
        )
        result = await session.execute(stmt)
        pendientes = result.scalars().all()

        for msg in pendientes:
            repo = ComunicacionRepository(session, msg.tenant_id)

            # Mark as Enviando
            await repo.update_estado(msg.id, "Enviando")
            await session.flush()

            try:
                # Decrypt destination email
                destinatario_email = decrypt(msg.destinatario)
                _send_email(destinatario_email, msg.asunto, msg.cuerpo)

                # Mark as Enviado
                await repo.update_estado(
                    msg.id,
                    "Enviado",
                    enviado_at=datetime.now(timezone.utc),
                )
            except Exception as exc:
                logger.exception("Error sending message %s", msg.id)
                await repo.update_estado(
                    msg.id,
                    "Error",
                    error_msg=str(exc),
                )

            await session.flush()

        await session.commit()

    if should_dispose:
        await engine.dispose()


async def run_worker() -> None:
    """Infinite polling loop — runs in the worker container."""
    logger.info("comunicaciones worker started (polling every 10s)")
    while True:
        try:
            await procesar_lote()
        except Exception:
            logger.exception("Unhandled error in worker cycle")
        await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(run_worker())
