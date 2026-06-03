# C-12: Worker de Cola de Comunicaciones

## Propósito

Implementar el módulo de comunicaciones salientes (emails) del sistema, con cola asincrónica, preview obligatorio, aprobación configurable y worker de despacho.

## Problema

Actualmente no existe forma de enviar comunicaciones a los alumnos desde el sistema. El flujo central del PROFESOR (FL-02, paso 7) requiere:
1. Identificar alumnos atrasados.
2. Enviarles un recordatorio.
3. Hacer seguimiento del estado del envío.

Sin este módulo, el profesor no puede accionar sobre los alumnos detectados como atrasados en C-11.

## Alcance

### Incluye

- Modelo `Comunicacion` con ciclo de vida Pendiente → Enviando → Enviado/Error/Cancelado (E21, RN-15).
- Endpoint `POST /api/comunicaciones/preview` — renderiza asunto + cuerpo con variables de sustitución (RN-16).
- Endpoint `POST /api/comunicaciones/enviar` — encola mensajes masivos en Pendiente (F3.2, `comunicacion:enviar`).
- Endpoint `GET /api/comunicaciones/estado` — tracking de estado por materia/lote (F3.2).
- Endpoint `POST /api/comunicaciones/aprobar` y `POST /api/comunicaciones/cancelar` para aprobación (F3.3, RN-17).
- Worker asíncrono (`workers/comunicaciones.py`) que consume Pendientes, los transiciona y "envía" (mock de SMTP por ahora).
- Flag `aprobacion_requerida` en configuración del tenant (si true, envíos masivos requieren aprobación).
- Destinatario cifrado AES-256 en reposo.
- Migración Alembic `008_comunicacion`.
- Tests: máquina de estados, preview, aprobación, cancelación, worker.

### Excluye

- Integración real con SMTP/envío de emails (se mockea en el worker por ahora. Se integra con proveedor real en change posterior).
- Mensajería interna entre usuarios (F3.4) — es otro change.
- Tablón de avisos (F3.5) — otro change.
- Panel de auditoría de comunicaciones (F9.1) — depende de C-05.

## Dependencias

- **C-11** ✅ (atrasados y reportes — ya completado)
- **C-04** ✅ (RBAC — permisos `comunicacion:enviar` y `comunicacion:aprobar`)
- **C-10** ✅ (calificaciones — el preview usa datos de calificaciones para variables de sustitución)

## Reglas de Negocio Aplicadas

| Regla | Descripción |
|-------|-------------|
| RN-15 | Ciclo de vida Pendiente → Enviando → Enviado/Error/Cancelado |
| RN-16 | Preview obligatorio antes de envío |
| RN-17 | Aprobación administrativa configurable para envíos masivos |

## Recorrido del usuario (PROFESOR)

1. PROFESOR ve alumnos atrasados (C-11) → decide comunicarse.
2. Selecciona destinatarios y activa la plantilla de recordatorio.
3. Sistema genera preview → PROFESOR confirma.
4. Mensajes entran a cola Pendiente.
5. _(Si aplica)_ COORDINADOR aprueba el lote.
6. Worker consume → Enviando → Enviado/Error.
7. PROFESOR consulta estado en panel.
