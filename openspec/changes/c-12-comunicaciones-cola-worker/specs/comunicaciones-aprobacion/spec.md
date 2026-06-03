# Comunicaciones - Aprobación de Envíos Masivos

## Escenario: Aprobar lote completo
**Dado** un lote de comunicaciones en estado `Pendiente` con `requiere_aprobacion = true`
**Y** un COORDINADOR autenticado con permiso `comunicacion:aprobar`
**Cuando** envía `POST /api/comunicaciones/lote/{lote_id}/aprobar`
**Entonces** todos los mensajes del lote pasan a `Enviando`
**Y** el worker los procesa normalmente

## Escenario: Cancelar lote completo
**Dado** un lote de comunicaciones en estado `Pendiente` con `requiere_aprobacion = true`
**Y** un COORDINADOR autenticado con permiso `comunicacion:aprobar`
**Cuando** envía `POST /api/comunicaciones/lote/{lote_id}/cancelar`
**Entonces** todos los mensajes del lote pasan a `Cancelado`
**Y** el worker ignora esos mensajes

## Escenario: Aprobar sin permiso retorna 403
**Dado** un usuario sin permiso `comunicacion:aprobar`
**Cuando** intenta aprobar un lote
**Entonces** recibe 403 Forbidden

## Escenario: Cancelar sin permiso retorna 403
**Dado** un usuario sin permiso `comunicacion:aprobar`
**Cuando** intenta cancelar un lote
**Entonces** recibe 403 Forbidden

## Escenario: Aprobar lote inexistente
**Dado** un COORDINADOR con permiso `comunicacion:aprobar`
**Cuando** aprueba un lote_id que no existe
**Entonces** recibe 404 Not Found
