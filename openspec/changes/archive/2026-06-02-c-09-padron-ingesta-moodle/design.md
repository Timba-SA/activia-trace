## Context

El padrón es la base de todo el módulo académico: calificaciones, comunicación, análisis de atrasados. El modelo E6 de la KB especifica versionado explícito: cada carga crea una nueva versión, y solo una versión puede estar activa por (materia, cohorte). La integración con Moodle WS permitirá sincronización automática nocturna y on-demand.

## Goals / Non-Goals

**Goals:**
- Modelo versionado de padrón (VersionPadron + EntradaPadron)
- Importación manual xlsx/csv con preview → confirmación → commit
- Cliente Moodle WS para sync de usuarios/actividades
- Permiso `padron:cargar` asignado a ADMIN y COORDINADOR
- Tenant isolation en todas las entidades
- Strict TDD en toda la implementación

**Non-Goals:**
- Sincronización nocturna programada (se hará en change posterior)
- Interfaz frontend (API-first; frontend en change separado)
- Importación de calificaciones desde Moodle (C-10)

## Decisions

1. **VersionPadron como batch**: no se almacena el archivo, solo los datos parseados. Cada carga es una versión independiente.
2. **EntradaPadron con usuario_id nullable**: permite cargar alumnos que aún no tienen cuenta en el sistema (según KB E6).
3. **Preview como respuesta JSON**: el frontend recibe los datos parseados para mostrar, y confirma con POST que incluye un hash del preview para detectar cambios entre preview y confirm.
4. **Moodle WS client**: clase async HTTP en `integrations/moodle_ws.py` con retry exponencial y timeout.
5. **Permiso `padron:cargar`**: agregado a ADMIN + COORDINADOR tanto en migration 006 como en seed script.

## Risks / Trade-offs

- [Preview stale] Si el usuario hace preview y tarda en confirmar, los datos podrían ser distintos → mitigado con hash de preview en confirmación
- [Moodle WS no disponible] La integración moodle WS requiere configuración; si falla, el fallback manual (subida de archivo) siempre está disponible
