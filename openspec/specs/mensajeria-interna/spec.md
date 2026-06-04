## ADDED Requirements

### Requirement: Usuario autenticado puede listar su bandeja de entrada
El sistema SHALL exponer `GET /api/inbox` que retorne los mensajes recibidos por el usuario autenticado, ordenados por `created_at` descendente. Cada mensaje SHALL incluir: id, remitente (nombre+apellido), asunto, cuerpo, leido, created_at.

#### Scenario: Listar inbox exitosamente
- **WHEN** un usuario autenticado envía `GET /api/inbox`
- **THEN** el sistema responde 200 con un array de mensajes ordenados por fecha descendente

#### Scenario: Inbox vacío
- **WHEN** un usuario autenticado sin mensajes envía `GET /api/inbox`
- **THEN** el sistema responde 200 con un array vacío

### Requirement: Usuario autenticado puede leer un mensaje específico
El sistema SHALL exponer `GET /api/inbox/{id}` que retorne un mensaje individual. Al acceder, el sistema SHALL marcar automáticamente `leido = True` si el destinatario es el usuario autenticado.

#### Scenario: Leer mensaje propio exitosamente
- **WHEN** un usuario autenticado envía `GET /api/inbox/{id}` donde {id} es un mensaje dirigido a él
- **THEN** el sistema responde 200 con el mensaje completo, y `leido` pasa a `true`

#### Scenario: Leer mensaje de otro usuario
- **WHEN** un usuario autenticado envía `GET /api/inbox/{id}` donde {id} es un mensaje NO dirigido a él
- **THEN** el sistema responde 404 (el mensaje no existe para ese usuario)

### Requirement: Usuario autenticado puede enviar un mensaje
El sistema SHALL exponer `POST /api/inbox` que cree un nuevo hilo de mensajes. El body SHALL incluir `destinatario_id`, `asunto` y `cuerpo`. El sistema SHALL generar un nuevo `hilo_id` UUID automáticamente. El remitente SHALL ser el usuario autenticado.

#### Scenario: Enviar mensaje exitosamente
- **WHEN** un usuario autenticado envía `POST /api/inbox` con `{"destinatario_id": "<uuid>", "asunto": "Consulta", "cuerpo": "Hola"}`
- **THEN** el sistema responde 201 con el mensaje creado, incluyendo un `hilo_id` generado

#### Scenario: Enviar mensaje a usuario inexistente
- **WHEN** un usuario autenticado envía `POST /api/inbox` con un `destinatario_id` que no existe
- **THEN** el sistema responde 404

#### Scenario: Enviar mensaje a sí mismo
- **WHEN** un usuario autenticado envía `POST /api/inbox` con `destinatario_id` igual a su propio id
- **THEN** el sistema responde 422 (no se permite auto-mensajería)

### Requirement: Usuario autenticado puede responder en un hilo
El sistema SHALL exponer `POST /api/inbox/{id}/responder` que cree un mensaje en el mismo `hilo_id` que el mensaje referenciado. El destinatario SHALL ser el remitente original del mensaje referenciado. El body SHALL incluir `cuerpo`. El asunto SHALL heredarse del mensaje original.

#### Scenario: Responder en hilo exitosamente
- **WHEN** un usuario autenticado envía `POST /api/inbox/{id}/responder` con `{"cuerpo": "Gracias por tu mensaje"}`
- **THEN** el sistema responde 201 con el nuevo mensaje, usando el mismo `hilo_id` que el mensaje original, y el destinatario es el remitente original

#### Scenario: Responder a mensaje no propio
- **WHEN** un usuario autenticado envía `POST /api/inbox/{id}/responder` donde {id} es un mensaje del que NO es destinatario
- **THEN** el sistema responde 404

### Requirement: Existe migration 016 para tabla mensaje
El sistema SHALL incluir una migración Alembic que cree la tabla `mensaje` con los campos definidos y FK a `tenant` y `usuario`.

#### Scenario: Tabla mensaje creada con schema correcto
- **WHEN** se ejecuta la migración 016
- **THEN** la tabla `mensaje` existe con columnas: id (UUID PK), tenant_id (FK), remitente_id (FK), destinatario_id (FK), hilo_id (UUID), asunto (text), cuerpo (text), leido (bool default false), created_at (datetime)
