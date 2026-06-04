## 1. Modelo y migración

- [x] 1.1 Crear modelo `Comunicacion` con BaseModelMixin, campos según E21 + `lote_id`, `requiere_aprobacion`, `error_msg`, `enviado_at`.
- [x] 1.2 Crear migración Alembic `008_comunicacion.py`: tabla + permisos `comunicacion:enviar` y `comunicacion:aprobar`.
- [x] 1.3 Agregar `Comunicacion` al `__init__.py` de models.

## 2. Cifrado y utilidades

- [x] 2.1 Implementar/verificar utilidad de cifrado AES-256 para `destinatario`.
- [x] 2.2 Implementar función de descifrado para uso en worker.

## 3. Repositorio de comunicaciones

- [x] 3.1 Implementar `ComunicacionRepository.bulk_create` (create por lote).
- [x] 3.2 Implementar `get_estado(lote_id)` con resumen de conteos por estado.
- [x] 3.3 Implementar `get_pendientes(limit=50)` para worker (excluye requiere_aprobacion=true).
- [x] 3.4 Implementar `get_pendientes_aprobacion(lote_id)` para aprobador.
- [x] 3.5 Implementar `update_estado(id, estado, enviado_at, error_msg)`.
- [x] 3.6 Implementar `aprobar_lote(lote_id)` y `cancelar_lote(lote_id)`.

## 4. Service de comunicaciones

- [x] 4.1 Implementar `ComunicacionService.preview(materia_id, cohorte_id, destinatarios, templates)` — renderiza plantillas con datos del alumno.
- [x] 4.2 Implementar `enviar(materia_id, cohorte_id, destinatarios, asunto, cuerpo)` — encola según flag de tenant.
- [x] 4.3 Implementar `get_estado(lote_id)` — delega al repo.
- [x] 4.4 Implementar `aprobar_lote(lote_id)` y `cancelar_lote(lote_id)` — valida permisos de aprobación.
- [x] 4.5 Resolver `aprobacion_requerida` desde configuración del tenant.

## 5. Worker de despacho

- [x] 5.1 Implementar `workers/comunicaciones_worker.py` con bucle asyncio de polling.
- [x] 5.2 Implementar mock `EmailSender` que loguea envíos.
- [x] 5.3 Worker ignora mensajes con `requiere_aprobacion = true`.
- [x] 5.4 Worker registra errores sin detener el bucle.

## 6. API / Routers

- [x] 6.1 Endpoint `POST /api/comunicaciones/preview` con `require_permission("comunicacion:enviar")`.
- [x] 6.2 Endpoint `POST /api/comunicaciones/enviar` con `require_permission("comunicacion:enviar")`.
- [x] 6.3 Endpoint `GET /api/comunicaciones/estado` con `require_permission("comunicacion:enviar")`.
- [x] 6.4 Endpoint `POST /api/comunicaciones/lote/{lote_id}/aprobar` con `require_permission("comunicacion:aprobar")`.
- [x] 6.5 Endpoint `POST /api/comunicaciones/lote/{lote_id}/cancelar` con `require_permission("comunicacion:aprobar")`.
- [x] 6.6 Registrar router en `app/main.py`.

## 7. Pruebas (Strict TDD)

- [x] 7.1 Tests de template rendering (variables, unknown, empty).
- [x] 7.2 Tests de preview con y sin destinatarios.
- [x] 7.3 Tests de envío sin aprobación (encola → worker procesa).
- [x] 7.4 Tests de envío con aprobación (encola → aprobar → worker procesa).
- [x] 7.5 Tests de cancelación de lote.
- [x] 7.6 Tests de worker (lote exitoso, ignora aprobacion, mock send).
- [x] 7.7 Tests de permisos (403 sin `comunicacion:enviar` o `comunicacion:aprobar`).
- [x] 7.8 Tests de cifrado/descifrado de destinatario.
