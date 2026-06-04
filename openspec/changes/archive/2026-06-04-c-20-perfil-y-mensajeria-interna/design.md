## Context

C-07 ya implementó el modelo `Usuario` con cifrado AES-256 para PII (email, dni, cuil, cbu, alias_cbu). No existe actualmente un endpoint para que el usuario edite sus propios datos, ni un sistema de mensajería interna. C-03 ya provee `POST /api/auth/logout`.

La multi-tenancy row-level está implementada via `BaseRepository` con filtro automático por `tenant_id`. La identidad se obtiene del JWT verificado (regla dura 8).

## Goals / Non-Goals

**Goals:**
- Exponer perfil propio vía GET/PATCH en `/api/perfil`
- CUIL readonly en PATCH — rechazar con 422 si se intenta modificar
- Sistema de mensajería interna con hilos entre usuarios registrados
- Marcación de leído al leer un mensaje
- Migration 016 para tabla `mensaje`

**Non-Goals:**
- No se modifican permisos RBAC — es datos propios
- No se agrega buscador de mensajes
- No hay notificaciones push/email al recibir mensaje
- No hay borrado de mensajes (soft delete no aplica — es mensajería, no entidad de negocio)

## Decisions

| Decisión | Opción elegida | Alternativas | Razón |
|----------|---------------|--------------|-------|
| **hilo_id generación** | UUID generado por el backend en el primer mensaje | Que el cliente envíe el hilo_id | Evita colisiones y hilos maliciosos |
| **Responder en hilo** | Nuevo endpoint dedicado `POST /api/inbox/{id}/responder` | Query param `?responder_a=id` | REST semántico, más claro en OpenAPI |
| **Leído automático** | Se marca `leido=True` al hacer GET del mensaje individual | Marcación explícita vía PATCH | Modelo inbox clásico — al abrir se marca como leído |
| **Orden de inbox** | `created_at DESC` siempre | Paginación ascendente | El mensaje más reciente primero (estándar de bandeja de entrada) |
| **Perfil PII write** | El service descifra al leer, cifra al escribir | Cifrar/descifrar en el schema | La capa de servicio mantiene la responsabilidad del cifrado (consistente con C-07) |
| **Validación CUIL en PATCH** | Rechazo explícito con 422 y mensaje | Ignorar silenciosamente | Feedback claro al usuario evita confusión |

## Risks / Trade-offs

- **[Mensajes sin borrado]** Los mensajes acumulados no se eliminan. Para MVP es aceptable; si escala, agregar archivado lógico por usuario.
- **[Cifrado en perfil PATCH]** El service debe leer el usuario actual, descifrar campos PII, aplicar cambios, cifrar de nuevo y guardar. Es más pesado que un update directo, pero necesario para consistencia del cifrado.
- **[Sin notificaciones]** El usuario no sabe que recibió un mensaje hasta que revisa la bandeja. Se puede integrar con el worker de comunicaciones (C-10) en una iteración futura.
