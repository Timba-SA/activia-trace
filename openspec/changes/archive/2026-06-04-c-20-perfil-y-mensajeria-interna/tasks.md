## 1. Migration — Tabla mensaje

- [x] 1.1 Crear migration 016 con tabla `mensaje` (UUID PK, tenant_id FK, remitente_id FK, destinatario_id FK, hilo_id UUID, asunto text, cuerpo text, leido bool default false, created_at datetime)
- [x] 1.2 Ejecutar migration y verificar schema en BD

## 2. Modelo Mensaje

- [x] 2.1 Crear `models/mensaje.py` con clase `Mensaje`, herencia de `Base`, columnas y FK a `Tenant` y `Usuario`
- [x] 2.2 Registrar modelo en `models/__init__.py`

## 3. Repository Mensaje

- [x] 3.1 Crear `repositories/mensaje.py` con `MensajeRepository(BaseRepository[Mensaje])` y métodos: `list_by_destinatario`, `get_by_id_and_destinatario`, `create`, `list_by_hilo`, `marcar_leido`

## 4. Schemas Perfil y Mensajería

- [x] 4.1 Crear `schemas/mensaje.py` con `MensajeOut`, `MensajeCreate`, `MensajeResponder`
- [x] 4.2 Crear o extender schema `PerfilOut` y `PerfilUpdate` en `schemas/usuario.py` (sin campo `cuil` en update, con `extra='forbid'`)

## 5. Services

- [x] 5.1 Crear `services/perfil.py` con `get_perfil()` y `update_perfil()` — este último descifra campos PII, aplica cambios, vuelve a cifrar
- [x] 5.2 Crear `services/mensajeria.py` con: `list_inbox()`, `get_mensaje()`, `enviar_mensaje()`, `responder_mensaje()`

## 6. Routers

- [x] 6.1 Crear `api/v1/routers/perfil.py` con `GET /api/perfil` y `PATCH /api/perfil`, usando `require_auth` y `get_current_user`
- [x] 6.2 Crear `api/v1/routers/inbox.py` con `GET /api/inbox`, `GET /api/inbox/{id}`, `POST /api/inbox`, `POST /api/inbox/{id}/responder`
- [x] 6.3 Registrar ambos routers en `main.py`

## 7. Tests

- [x] 7.1 Tests para perfil: obtener perfil propio, editar campos, rechazar CUIL, rechazar no autenticado
- [x] 7.2 Tests para mensajería: enviar mensaje, listar inbox, leer mensaje (marca leído), responder en hilo, validar destinatario inexistente, validar auto-mensajería
