## Why

Active-trace debe registrar los encuentros sincrónicos (clases virtuales) de cada comisión y las guardias de atención a alumnos. Sin estos módulos, no hay trazabilidad sobre qué clases se dictaron ni qué guardias se cubrieron — dos indicadores centrales para la liquidación de honorarios y la auditoría académica.

## What Changes

- Nuevo modelo `SlotEncuentro` (plantilla de recurrencia semanal)
- Nuevo modelo `InstanciaEncuentro` (encuentro concreto, opcionalmente derivado de un slot)
- Nuevo modelo `Guardia` (registro de atención de tutor/docente)
- Generación automática de N instancias al crear un slot recurrente (RN-13)
- CRUD de slots e instancias con scoping por tenant y validación de asignación/docente
- CRUD de guardias filtrable por materia/carrera/cohorte/docente
- 4 permisos nuevos: `encuentros:gestionar`, `encuentros:ver`, `guardias:registrar`, `guardias:ver`
- Endpoint de exportación HTML para aula virtual (F6.4)
- Endpoint de exportación CSV para guardias (F6.6)
- Migración Alembic 011 con las 3 tablas + enum types + seed de permisos

## Capabilities

### New Capabilities
- `encuentros`: gestión de slots e instancias de encuentro, recurrencia semanal, edición individual, exportación HTML para LMS
- `guardias`: registro de guardias por tutor, consulta global por coordinación, exportación CSV

### Modified Capabilities
- `rbac`: agregar 4 permisos nuevos (`encuentros:gestionar`, `encuentros:ver`, `guardias:registrar`, `guardias:ver`)

## Impact

- **Models**: 3 nuevos modelos SQLAlchemy (`SlotEncuentro`, `InstanciaEncuentro`, `Guardia`) con herencia de `BaseModelMixin`
- **Schemas**: Pydantic v2 request/response schemas por modelo (`extra='forbid'`)
- **Repositories**: 1 repositorio por modelo (Slots + Instancias comparten lógica en `encuentro_repository.py`)
- **Services**: `EncuentroService` (creación de slots, generación de instancias, CRUD, export HTML) y `GuardiaService` (CRUD con filtros, export CSV)
- **Routers**: `encuentros.py` y `guardias.py` bajo `/api/v1/routers/`
- **Permissions**: seed de 4 permisos + asignación a roles existentes
- **Migration**: `011_encuentros_guardias.py` con tablas, enums y seed data
