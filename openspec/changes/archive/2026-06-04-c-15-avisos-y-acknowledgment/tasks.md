## 1. Modelos y migración

- [x] 1.1 Crear modelo `Aviso` con tenant_id, alcance (enum: Global|PorMateria|PorCohorte|PorRol), materia_id (nullable FK), cohorte_id (nullable FK), rol_destino (nullable enum), severidad (enum: Info|Advertencia|Crítico), titulo, cuerpo (Text), inicio_en, fin_en, orden (int), activo (bool), requiere_ack (bool), soft delete fields
- [x] 1.2 Crear modelo `AcknowledgmentAviso` con tenant_id, aviso_id (FK), usuario_id (FK), confirmado_at (datetime), UniqueConstraint(aviso_id, usuario_id), soft delete fields
- [x] 1.3 Generar migration 013 con tablas `aviso` y `acknowledgment_aviso` + índices compuestos por tenant + índices en aviso_id/usuario_id

## 2. Schemas Pydantic

- [x] 2.1 Crear enums `AlcanceAviso` (Global, PorMateria, PorCohorte, PorRol), `SeveridadAviso` (Info, Advertencia, Critico)
- [x] 2.2 Crear `AvisoCreate`, `AvisoUpdate`, `AvisoResponse`, `AvisoListResponse` con `extra='forbid'` y `from_attributes=True`
- [x] 2.3 Crear `AckResponse`, `AvisoStatsResponse` (total_confirmaciones)

## 3. Repositories

- [x] 3.1 Crear `AvisoRepository` con CRUD, listado paginado (con filtro por alcance/activo/vigencia), y método `listar_visibles` para filtrar avisos según contexto del usuario
- [x] 3.2 Crear `AcknowledgmentRepository` con create (upsert idempotente), count por aviso_id, y verificación de existencia

## 4. Services

- [x] 4.1 Crear `AvisosService` con métodos: crear_aviso, actualizar_aviso, eliminar_aviso, obtener_aviso
- [x] 4.2 Implementar `listar_mis_avisos(usuario)` que construye filtros según alcance (Global/PorRol/PorMateria/PorCohorte) combinando roles del usuario, materias asignadas y cohortes
- [x] 4.3 Implementar `confirmar_lectura(aviso_id, usuario_id)` con idempotencia y validación de requiere_ack
- [x] 4.4 Implementar `obtener_stats(aviso_id)` con conteo derivado de AcknowledgmentAviso

## 5. Endpoints (Routers)

- [x] 5.1 Crear `avisos.py` router con POST/GET /avisos, GET /avisos/{id}, PATCH /avisos/{id}, DELETE /avisos/{id} — protegidos con `require_permission("avisos:publicar")`
- [x] 5.2 Implementar GET /avisos/mis-avisos — filtrado por audiencia, sin permiso adicional (solo autenticación)
- [x] 5.3 Implementar POST /avisos/{id}/ack — confirmar lectura, cualquier usuario autenticado
- [x] 5.4 Implementar GET /avisos/{id}/stats — contadores de confirmaciones, protegido con `require_permission("avisos:publicar")`
- [x] 5.5 Registrar `avisos.router` en `api/v1/main.py` o router principal

## 6. Permisos RBAC

- [x] 6.1 Agregar permiso `avisos:publicar` al seed de permisos en migration 013
- [x] 6.2 Asignar `avisos:publicar` a COORDINADOR y ADMIN en migration 013
- [x] 6.3 Agregar decoradores `require_permission` en endpoints de gestión

## 7. Tests

- [x] 7.1 Tests unitarios para servicios: creación de aviso, filtrado de mis-avisos por alcance, confirmación idempotente, stats derivados
- [x] 7.2 Tests de integración para endpoints: CRUD avisos, mis-avisos, ack, stats
- [x] 7.3 Tests de permisos: COORDINADOR puede publicar, ALUMNO no puede publicar, ALUMNO puede ver mis-avisos
- [x] 7.4 Tests de edge cases: aviso fuera de vigencia excluido, ack duplicado es idempotente, ack en aviso sin requiere_ack da 409
