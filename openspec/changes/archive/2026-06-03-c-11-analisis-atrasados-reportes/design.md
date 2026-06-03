## Context

`C-10` dejó disponibles calificaciones importadas y umbral por materia. `C-11` usa esa base para resolver el paso 5–6 de FL-02: identificar atrasados, generar ranking, reportes rápidos, notas finales agrupadas y export de TPs sin corregir. El dominio es multi-tenant y todas las consultas deben respetar sesión + `tenant_id` + alcance RBAC (`atrasados:ver`).

## Goals / Non-Goals

**Goals:**
- Exponer `/api/analisis/*` para atrasados, ranking, reportes rápidos, notas finales agrupadas y monitores.
- Implementar export de entregas finalizadas sin calificación (RN-07/RN-08).
- Soportar filtros por rol: tutor/profesor (scope asignado) y coordinación/admin (scope global + fechas).
- Mantener lógica de cálculo en Services y acceso a datos solo vía Repositories.

**Non-Goals:**
- Envío de comunicaciones y worker (C-12).
- Cambiar autenticación, tenancy model o esquema base de calificaciones de C-10.
- Resolver preguntas abiertas fuera de este alcance (PA-01/07/22/23/25).

## Decisions

1. **Servicio analítico único con submétodos por caso**  
   Se crea `AnalisisService` (atrasados/ranking/reportes/notas_finales/monitores/export). Alternativa: servicios separados por endpoint. Se elige uno para centralizar reglas RN-06/RN-09 y evitar divergencia.

2. **Repositorios con proyecciones agregadas (no SQL en services)**  
   Los cálculos de conteos, porcentajes y agrupaciones se implementan en repositorios dedicados (`analisis_repository`, `monitores_repository`). Alternativa: armar agregaciones en memoria; se descarta por costo y riesgo de inconsistencia.

3. **Scope de datos por identidad de sesión + rol efectivo**  
   El service resuelve un `AccessScope` (materias/comisiones/usuarios permitidos) desde asignaciones vigentes. Alternativa: aceptar scope por request; se rechaza por regla dura de identidad/scope desde sesión.

4. **Export sin almacenamiento persistente de archivo**  
   La exportación de TPs sin corregir se genera on-demand (CSV) con filtros aplicados. Alternativa: job async con archivo persistido; se difiere para C-12+.

## Risks / Trade-offs

- **[Ambigüedad en “nota final agrupada”]** → Definir agregación inicial (promedio ponderado simple por actividades seleccionadas) y dejar parametrización avanzada fuera de scope.
- **[Volumen alto en monitores globales]** → Mitigar con paginación obligatoria + índices por `tenant_id,materia_id,cohorte_id` + rango de fechas.
- **[Datos incompletos de finalización]** → Etiquetar filas como “potencialmente sin corregir” cuando falte correlación fuerte.

## Migration Plan

1. Implementar contratos de repositorio + tests de reglas de cálculo.
2. Exponer endpoints `/api/analisis/*` con guards y filtros validados.
3. Habilitar export CSV y paginación en monitores.
4. Validar con suite de integración sobre DB real.
5. Rollback: remover routers/servicios nuevos y revertir migración solo si existiera cambio de esquema.

## Open Questions

- Definición exacta de “notas finales agrupadas”: ¿promedio simple, ponderado por actividad o por categoría?
- Límite de rango temporal por defecto para monitor coordinación/admin (ej. últimos 30/90 días).
- Formato final del CSV de TPs sin corregir (columnas obligatorias para operación académica).
