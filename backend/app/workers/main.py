"""Placeholder worker — loop no-op.

La tecnología real de la cola se define en ADR-003.
Este entrypoint es reemplazado cuando se implemente el módulo de comunicaciones.
"""
import asyncio
import logging

logger = logging.getLogger(__name__)


async def main() -> None:
    logger.info("worker started (placeholder — no-op)")
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())
