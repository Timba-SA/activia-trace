# Comunicaciones - Worker de Despacho

## Escenario: Worker procesa mensajes Pendientes
**Dado** una Comunicacion en estado `Pendiente` (sin aprobación requerida)
**Cuando** el worker ejecuta su ciclo
**Entonces** transiciona a `Enviando`
**Y** luego a `Enviado` con `enviado_at` no nulo

## Escenario: Worker maneja error de envío
**Dado** una Comunicacion en estado `Pendiente`
**Y** el envío SMTP falla
**Cuando** el worker ejecuta su ciclo
**Entonces** transiciona a `Error`
**Y** `error_msg` contiene el mensaje de error

## Escenario: Worker ignora mensajes no Pendientes
**Dado** una Comunicacion en estado `Enviado`
**Cuando** el worker ejecuta su ciclo
**Entonces** no modifica ese mensaje

## Escenario: Worker ignora mensajes con aprobación pendiente
**Dado** una Comunicacion en estado `Pendiente` con `requiere_aprobacion = true`
**Cuando** el worker ejecuta su ciclo
**Entonces** no modifica ese mensaje (debe esperar aprobación)

## Escenario: Worker procesa múltiples mensajes en lote
**Dado** 5 Comunicaciones en estado `Pendiente`
**Cuando** el worker ejecuta un ciclo
**Entonces** las 5 transicionan a `Enviado`
