## Context

Módulo de programas de materia (documentos oficiales) y fechas académicas (calendarización de evaluaciones) para active-trace. Construye sobre C-06 (estructura-academica) para las FK a Materia, Carrera y Cohorte. COORDINADOR y ADMIN gestionan programas (subir archivo, versionado, activación, generación de contenido HTML para LMS) y fechas de evaluaciones (parciales, TP, coloquios, recuperatorios) por materia × cohorte.

## Goals / Non-Goals

**Goals:**
- CRUD de programas de materia con permiso `programas:gestionar` (COORDINADOR, ADMIN)
- Versionado de programas (versión entero incremental, activo booleano)
- Generación de fragmento HTML ready para LMS a partir del programa activo
- CRUD de fechas académicas con permiso `programas:gestionar` (COORDINADOR, ADMIN)
- Filtros por materia, carrera, cohorte en listados
- Soft delete en ambos modelos (activo booleano en programas, borrado lógico en fechas)
- Tenant isolation en todas las operaciones

**Non-Goals:**
- No incluye frontend — solo API REST
- No incluye almacenamiento de archivos (s3/local) — `referencia_archivo` es texto, el servicio de storage se integra en change futuro
- No incluye calendario visual ni exportación iCal
- No incluye workflow de aprobación de programas (el campo `aprobado_en` es informativo)

## Decisions

### D1 — Versionado simple con activo booleano
ProgramaMateria tiene `version` (entero) y `activo` (booleano). Al crear un nuevo programa para la misma materia × carrera × cohorte, se incrementa la versión automáticamente y se desactiva la anterior. Esto permite mantener histórico sin complejidad de tabla de versiones separada.

### D2 — Generación de contenido HTML con template simple
El endpoint `POST /api/programas/{id}/generar-contenido` toma el programa activo y genera un fragmento HTML con los datos del programa (título, materia, carrera, cohorte, referencia). Usa un template string en el service, sin engine externo. Suficiente para el caso de uso actual de publicación en LMS.

### D3 — FechasAcademicas como recurso independiente
Aunque conceptualmente relacionado con programas, FechaAcademica es un recurso separado con su propio router y endpoints. Comparten el permiso `programas:gestionar` por economía de permisos, pero podrían separarse en el futuro.

### D4 — Soft delete consistente
ProgramaMateria usa `activo` booleano (desactivar en lugar de borrar). FechaAcademica usa soft delete estándar (BaseModelMixin con `deleted_at`). Los listados excluyen registros desactivados/borrados por defecto, con opción `incluir_inactivos`.

### D5 — Dos routers separados
`programas.py` para endpoints de programa (CRUD + generar-contenido) y `fechas_academicas.py` para fechas. Cada uno con su propio service y repository. Separación limpia aunque compartan permiso.

## Risks / Trade-offs

- **referencia_archivo sin validación de storage**: El campo almacena una ruta texto sin verificar que el archivo exista. El service de almacenamiento real se integrará en un change posterior. Mitigación: el campo es opcional en creación.
- **contenido_html generado simple**: El template es un string fijo. Si se requieren formatos complejos (tablas, estilos), habrá que migrar a un engine de templates. Por ahora es suficiente.
- **Permiso compartido `programas:gestionar`**: Si en el futuro se necesita separar permisos para programas vs fechas, habrá que dividir el permiso. Por ahora un solo permiso simplifica la administración.
