## Why

Los usuarios autenticados no pueden editar su propio perfil ni comunicarse entre sí dentro de la plataforma. Esto obliga a usar canales externos (email, WhatsApp) para consultas simples entre docentes, coordinadores y nexo. La bandeja de mensajes interna reduce la fricción, mantiene la trazabilidad y evita流失 de comunicación fuera del sistema.

## What Changes

- **Nuevo endpoint `GET /api/perfil`** — cualquier usuario autenticado obtiene su perfil completo
- **Nuevo endpoint `PATCH /api/perfil`** — edición de campos editables (nombre, apellidos, datos bancarios, regional, email, legajo_profesional). CUIL es solo lectura y se rechaza explícitamente.
- **Nuevo endpoint `GET /api/inbox`** — lista mensajes recibidos, ordenados por fecha descendente
- **Nuevo endpoint `GET /api/inbox/{id}`** — lee un mensaje y lo marca como leído
- **Nuevo endpoint `POST /api/inbox`** — envía un mensaje a otro usuario
- **Nuevo endpoint `POST /api/inbox/{id}/responder`** — responde dentro del mismo hilo
- **Nueva tabla `mensaje`** (migration 016) con los campos: id, tenant_id, remitente_id, destinatario_id, hilo_id, asunto, cuerpo, leido, created_at
- Reusa `POST /api/auth/logout` de C-03 — sin cambios

## Capabilities

### New Capabilities
- `perfil`: Edición de perfil propio para cualquier usuario autenticado. Campos editables definidos por rol; CUIL es solo lectura.
- `mensajeria-interna`: Bandeja de mensajes internos entre usuarios registrados, con hilos, lectura y respuesta.

### Modified Capabilities
<!-- No existing spec changes needed -->

## Impact

- **Backend**: Nuevo router `api/v1/routers/perfil.py` + `api/v1/routers/inbox.py`. Nuevo servicio `services/perfil.py` + `services/mensajeria.py`. Nuevo repositorio `repositories/mensaje.py`. Nuevo schema `schemas/mensaje.py` + extensiones en `schemas/usuario.py`. Migration 016.
- **Modelo nuevo**: `models/mensaje.py` con `Mensaje` model.
- **Modelo existente**: `Usuario` ya existe (C-07), no se modifica — solo se exponen endpoints.
- **PII**: Los campos PII (email, CUIL, CBU, alias_cbu) se cifran con AES-256 existente. CUIL es readonly en PATCH.
- **Permisos**: Ninguno nuevo — perfil propio es datos propios; inbox son mensajes propios. Governance BAJO.
