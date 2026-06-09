## ADDED Requirements

### Requirement: Monitor de seguimiento de alumnos (TUTOR/PROFESOR)
El sistema SHALL mostrar una vista filtrable del estado de actividades de los alumnos asignados al usuario.

#### Scenario: Monitor con filtros básicos
- **WHEN** el usuario accede al monitor de seguimiento
- **THEN** el sistema muestra tabla con alumnos, su estado de actividades y nota promedio
- **AND** permite filtrar por nombre de alumno, actividad, y mínimo de actividad cumplida

#### Scenario: Filtro sin resultados
- **WHEN** el usuario aplica filtros que no coinciden con ningún alumno
- **THEN** el sistema muestra "Sin resultados" y sugiere limpiar filtros

#### Scenario: Monitor sin datos
- **WHEN** la comisión no tiene datos de actividades
- **THEN** el sistema muestra estado informativo
