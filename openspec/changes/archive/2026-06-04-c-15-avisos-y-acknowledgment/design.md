## Context

Módulo de avisos del sistema para active-trace. Permite a COORDINADOR/ADMIN publicar avisos segmentados por audiencia y con acuse de recibo obligatorio. Todos los usuarios visualizan avisos según su rol, materia y cohorte. Construye sobre C-06 (estructura-academica) para las FK a Materia y Cohorte, y sobre C-07 (usuarios-y-asignaciones) para la FK a Usuario en los acuses.

## Goals / Non-Goals

**Goals:**
- CRUD completo de avisos con permiso `avisos:publicar` (COORDINADOR, ADMIN)
- Visualización filtrada de avisos activos para el usuario autenticado según su audiencia
- Confirmación de lectura (ack) cuando el aviso requiere acuse
- Estadísticas derivadas de confirmaciones (sin denormalizar)
- Soft delete en ambas tablas

**Non-Goals:**
- No incluye notificaciones push/email al publicarse un aviso (se integra con C-12 comunicaciones)
- No incluye frontend — solo API REST
- No incluye programación de publicación diferida (inicio_en define cuándo se muestra)

## Decisions

### D1 — Auditoría de avisos vía alcance enum (no modelo polimórfico)
En lugar de un diseño con `target_type` + `target_id` polimórfico, se usa un enum `AlcanceAviso` (Global, PorMateria, PorCohorte, PorRol) con columnas nullable `materia_id` y `cohorte_id`. Esto simplifica las queries de filtrado, evita joins genéricos y es más legible en el modelo. El `rol_destino` también es nullable — cuando es null, el aviso aplica a todos los roles dentro del alcance definido.

### D2 — Filtrado de mis-avisos vía service con lógica de alcance
El service `avisos` implementa `listar_mis_avisos(usuario_id)` que construye dinámicamente el WHERE combinando:
- Alcance Global → siempre visible
- Alcance PorRol → coincide con algún rol del usuario
- Alcance PorMateria → el usuario está en esa materia
- Alcance PorCohorte → el usuario pertenece a esa cohorte
- Además filtra por ventana de vigencia (inicio_en <= now <= fin_en) y activo = true
- Ordena por orden ASC, luego por created_at DESC

Esto mantiene la lógica de negocio en el service sin contaminar el repository.

### D3 — Acknowledgment como registro separado (no denormalizado)
`AcknowledgmentAviso` almacena la confirmación explícita del usuario. Los contadores se derivan con `COUNT(*)` agrupado por `aviso_id`. No se almacenan campos de "visto" implícito (como última visualización) — solo el ack explícito cuando `requiere_ack=true`. Esto evita falsos positivos de lectura.

### D4 — Un solo router `avisos` con 4 endpoints
Se agrupa toda la funcionalidad en `avisos.py` router: CRUD de gestión, `mis-avisos`, `ack` y `stats`. Un solo service `AvisosService` orquesta toda la lógica. Esto es apropiado para un módulo pequeño y cohesivo.

## Risks / Trade-offs

- **Filtrado por cohorte**: un usuario puede pertenecer a 0 o N cohortes. El filtro por cohorte debe hacer join contra la tabla de asignación. Si un usuario no tiene cohorte, los avisos `PorCohorte` no se le muestran.
- **Avisos sin ack**: si `requiere_ack=false`, el aviso nunca genera registro en `AcknowledgmentAviso`. El endpoint `stats` debe reflejar esto mostrando `total_usuarios_audiencia` (estimado) y `confirmaciones` (reales).
- **Permiso `avisos:publicar`**: es un permiso de gestión. La visualización (`mis-avisos`) es abierta a cualquier usuario autenticado — no requiere permiso adicional, se controla por alcance.
