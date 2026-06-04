## Context

Actualmente active-trace maneja usuarios, asignaciones, calificaciones, mensajería y equipos docentes. Falta el módulo de encuentros sincrónicos (clases virtuales) y guardias — dos dominios directamente vinculados a la liquidación de honorarios y auditoría académica. Los modelos están definidos en `04_modelo_de_datos.md` (E9–E11), las funcionalidades en Épica 6 (F6.1–F6.6) y el flujo principal FL-06 en `07_flujos_principales.md`.

## Goals / Non-Goals

**Goals:**
- SlotEncuentro: plantilla de recurrencia semanal con FK a Asignacion y Materia
- InstanciaEncuentro: encuentro concreto, opcionalmente vinculado a un slot
- Generación automática de N instancias al crear un slot (RN-13)
- CRUD individual de instancias (editar estado, meet_url, video_url, comentario)
- Vista admin transversal (todos los encuentros del tenant, sin filtro por docente)
- Exportación HTML de calendario de encuentros para embeder en LMS (F6.4)
- Guardia: registro con FK a Asignacion, Materia, Carrera, Cohorte
- Consulta global filtrada y exportación CSV de guardias (F6.6)
- 4 permisos nuevos en el sistema RBAC existente

**Non-Goals:**
- Reprogramación automática de instancias al modificar un slot (cada instancia es independiente, RN-14)
- Webhooks o integración en vivo con Zoom/Meet (solo almacenamos URLs)
- Modificación masiva de instancias desde un slot (edición individual solamente)
- Calendario visual frontend (solo API REST + export HTML por ahora)

## Decisions

- **Slots e Instancias en un solo service**: `EncuentroService` maneja ambos modelos porque la generación de instancias desde un slot es una operación transaccional. Separar en dos services agregaría complejidad sin beneficio.
- **Repositorio compartido `SlotEncuentroRepository`**: `InstanciaEncuentroRepository` extiende `BaseRepository` de forma independiente porque las queries son distintas (filtros por slot vs fecha, estados).
- **Generación de instancias síncrona**: Al crear un slot recurrente, las N instancias se generan en la misma request. No se justifica un job async para esto (N ≤ 52, operación liviana).
- **`fecha_unica` como flag**: `cant_semanas=0` + `fecha_unica` set = encuentro único. `cant_semanas>0` + `fecha_unica=NULL` = recurrente. Validación mutuamente excluyente en schema + service.
- **Guardia sin soft delete**: El `creada_at` funciona como time-series; no se requiere borrado lógico. Si es necesario en el futuro, se agrega `deleted_at`.
- **Export CSV para guardias**: Mismo patrón que `exportar_equipo` en equipos.py — `StreamingResponse` con `text/csv`.
- **Export HTML para encuentros**: Fragmento HTML plano con tabla de encuentros, listo para copiar al LMS. Sin dependencias de templates.

## Risks / Trade-offs

- [Generación síncrona de instancias] → Para N > 52 podría ser lento. Mitigación: validar max 52 semanas en el schema. Si se necesita más en futuro, migrar a background job.
- [Instancias huerfanas al eliminar slot] → Por ahora no hay eliminación de slots con instancias asociadas. Si se agrega, debe decidirse: ¿cancelar instancias o bloquear borrado?
- [Guardias sin soft delete] → Si un tutor registra una guardia por error, no hay forma de ocultarla. Mitigación: el estado `Cancelada` permite marcar guardias incorrectas sin borrarlas.
