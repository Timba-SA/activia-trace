# Comunicaciones - Envío y Preview

## Escenario: Preview de comunicación
**Dado** un PROFESOR autenticado con permiso `comunicacion:enviar`
**Y** una materia con alumnos cargados
**Cuando** envía `POST /api/comunicaciones/preview` con asunto_template y cuerpo_template
**Entonces** recibe un preview con el asunto y cuerpo renderizados para el primer alumno
**Y** las variables `{alumno}`, `{materia}`, `{legajo}` se reemplazan por los valores reales

## Escenario: Preview sin datos retorna error
**Dado** un PROFESOR autenticado
**Cuando** envía `POST /api/comunicaciones/preview` con una materia sin alumnos
**Entonces** recibe error 422 "No hay destinatarios para esta materia"

## Escenario: Envío masivo sin aprobación
**Dado** un tenant donde `aprobacion_comunicaciones = false`
**Y** un PROFESOR autenticado con permiso `comunicacion:enviar`
**Cuando** envía `POST /api/comunicaciones/enviar` con destinatarios válidos
**Entonces** se crean N registros en `Comunicacion` con estado `Pendiente`
**Y** el response indica `"estado": "encolado"` con un `lote_id`

## Escenario: Envío masivo con aprobación
**Dado** un tenant donde `aprobacion_comunicaciones = true`
**Cuando** un PROFESOR envía `POST /api/comunicaciones/enviar`
**Entonces** se crean N registros con estado `Pendiente` y `requiere_aprobacion = true`
**Y** el response indica `"estado": "aprobacion_pendiente"`

## Escenario: Tracking de estado
**Dado** un lote de comunicaciones enviado
**Cuando** se consulta `GET /api/comunicaciones/estado?lote_id=X`
**Entonces** retorna resumen: total, pendientes, enviados, errores, cancelados

## Escenario: Sin permiso retorna 403
**Dado** un usuario sin permiso `comunicacion:enviar`
**Cuando** accede a cualquier endpoint de comunicaciones
**Entonces** recibe 403 Forbidden
