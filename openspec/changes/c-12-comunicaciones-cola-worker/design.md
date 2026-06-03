# C-12: Comunicaciones - Diseño Técnico

## Arquitectura

### Capas

```
POST /api/comunicaciones/enviar
  → Router (valida permiso `comunicacion:enviar`)
    → Service (orquesta preview/encolado)
      → Repository (persiste Comunicacion como Pendiente)
      → TenantConfig (lee flag aprobacion_requerida)

Worker asíncrono (bucle independiente)
  → Repository (consulta Pendientes)
    → Envia email (mock SMTP)
      → Repository (actualiza a Enviado/Error)
```

### Flujo de datos

#### Envío sin aprobación
```
POST /preview → renderiza preview → confirma → POST /enviar
  → INSERT Comunicacion (estado=Pendiente)
  → Worker loop: SELECT * WHERE estado=Pendiente
    → UPDATE estado=Enviando
    → send_email()
    → UPDATE estado=Enviado|Error
```

#### Envío con aprobación
```
POST /enviar → INSERT Comunicacion (estado=Pendiente, requiere_aprobacion=true)
  → (se queda en Pendiente hasta aprobación)
POST /aprobar → UPDATE estado=Enviando (worker lo toma)
POST /cancelar → UPDATE estado=Cancelado
```

## Modelo de Datos

### Comunicacion

```python
class Comunicacion(Base, BaseModelMixin):
    __tablename__ = "comunicacion"

    enviado_por_id = Column(UUID, ForeignKey("usuario.id"), nullable=False, index=True)
    materia_id = Column(UUID, ForeignKey("materia.id"), nullable=False, index=True)
    cohorte_id = Column(UUID, ForeignKey("cohorte.id"), nullable=True)
    lote_id = Column(UUID, nullable=False, index=True)  # agrupa envíos masivos
    destinatario = Column(String(255), nullable=False)    # email cifrado
    asunto = Column(String(255), nullable=False)
    cuerpo = Column(Text, nullable=False)
    estado = Column(String(20), nullable=False, default="Pendiente")  # Pendiente|Enviando|Enviado|Error|Cancelado
    requiere_aprobacion = Column(Boolean, nullable=False, default=False)
    error_msg = Column(Text, nullable=True)
    enviado_at = Column(DateTime(timezone=True), nullable=True)
```

### TenantConfig (extensión)

Agregar a la configuración del tenant:

```python
class TenantConfig:
    aprobacion_comunicaciones_requerida: bool = False
    # ... otras configs existentes
```

## API Endpoints

### `POST /api/comunicaciones/preview`
- **Permiso**: `comunicacion:enviar`
- **Input**:
  ```json
  {
    "materia_id": "uuid",
    "cohorte_id": "uuid",
    "destinatarios": ["uuid_entrada_padron", ...],
    "asunto_template": "Recordatorio: {alumno} - {materia}",
    "cuerpo_template": "Hola {alumno}, tienes actividades pendientes..."
  }
  ```
- **Output**: preview del mensaje (primer destinatario como muestra)

### `POST /api/comunicaciones/enviar`
- **Permiso**: `comunicacion:enviar`
- **Input**: igual que preview + confirmación
- **Output**: `{ "lote_id": "uuid", "total": 5, "estado": "aprobacion_pendiente"|"encolado" }`

### `GET /api/comunicaciones/estado`
- **Permiso**: `comunicacion:enviar`
- **Query**: `materia_id`, `cohorte_id`, `lote_id` (opcional)
- **Output**: resumen de estados por lote

### `POST /api/comunicaciones/lote/{lote_id}/aprobar`
- **Permiso**: `comunicacion:aprobar`
- **Output**: `{ "lote_id": "...", "total_aprobados": N }`

### `POST /api/comunicaciones/lote/{lote_id}/cancelar`
- **Permiso**: `comunicacion:aprobar`
- **Output**: `{ "lote_id": "...", "total_cancelados": N }`

## Worker

### Ciclo de vida
```python
async def run_worker():
    while True:
        pendientes = await repo.get_pendientes(limit=50)
        for msg in pendientes:
            await repo.update_estado(msg.id, "Enviando")
            try:
                await send_email(msg.destinatario, msg.asunto, msg.cuerpo)
                await repo.update_estado(msg.id, "Enviado", enviado_at=now())
            except Exception as e:
                await repo.update_estado(msg.id, "Error", error_msg=str(e))
        await asyncio.sleep(10)  # polling interval
```

### Mock SMTP
- Por ahora, el worker loguea el envío en lugar de enviar realmente.
- Estructura preparada para inyectar un `EmailSender` real después.
- Usar `aiosmtplib` cuando se integre con SMTP real.

## Cifrado

- El campo `destinatario` se cifra con AES-256 usando la misma utilidad que cifra otros PII en el sistema.
- Se descifra solo al momento del envío (en el worker).
- Ver `app/core/crypto.py` (asumiendo que existe del foundation-setup).

## Variables de sustitución en plantillas

| Variable | Reemplazo |
|----------|-----------|
| `{alumno}` | Nombre completo del alumno |
| `{materia}` | Nombre de la materia |
| `{legajo}` | Legajo del alumno |

Se implementan con un simple `str.replace()` en el service antes de persistir.

## Migración

Archivo: `alembic/versions/008_comunicacion.py`
- Crea tabla `comunicacion`.
- Agrega permiso `comunicacion:enviar` y `comunicacion:aprobar` a los roles correspondientes.
- Agrega columna `aprobacion_comunicaciones` a configuración del tenant (si existe tabla de config).

## Tests

| Test | Descripción |
|------|-------------|
| Máquina de estados | Transiciones válidas e inválidas de Comunicacion |
| Preview | Renderiza plantilla con datos del alumno |
| Envío sin aprobación | Encola y queda Pendiente → worker lo procesa |
| Envío con aprobación | Queda Pendiente → aprobar → Enviando → worker |
| Cancelación | Pendiente → Cancelado |
| Worker | Procesa lote de 5 mensajes, todos a Enviado |
| Worker con error | Mensaje pasa a Error |
| Permisos | 403 si falta `comunicacion:enviar` o `comunicacion:aprobar` |
| Cifrado | Destinatario cifrado en reposo, descifrado al enviar |
