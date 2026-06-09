## ADDED Requirements

### Requirement: Seleccionar comisión activa
El sistema SHALL permitir al usuario seleccionar una materia y cohorte activa para comenzar a trabajar. La selección SHALL persistir durante la navegación dentro del feature.

#### Scenario: Usuario selecciona materia y cohorte
- **WHEN** el usuario accede a `/academico`
- **THEN** el sistema muestra un selector con materias y cohortes del tenant
- **WHEN** el usuario selecciona una materia y cohorte
- **THEN** el sistema redirige a `/academico/{materiaId}/{cohorteId}` y persiste la selección en contexto

#### Scenario: Acceso directo a una comisión
- **WHEN** el usuario navega a `/academico/{materiaId}/{cohorteId}`
- **THEN** el sistema selecciona esa comisión automáticamente y muestra su dashboard

### Requirement: Dashboard de comisión
El sistema SHALL mostrar métricas clave de la comisión seleccionada: total de alumnos, cantidad de alumnos atrasados, cantidad de actividades configuradas, y enlaces a todas las secciones.

#### Scenario: Dashboard muestra métricas de la comisión
- **WHEN** el usuario accede al dashboard de una comisión con datos
- **THEN** el sistema muestra KPIs con total de alumnos, atrasados, actividades configuradas, y enlaces a calificaciones, atrasados, notas finales, entregas, comunicaciones y monitoreo

#### Scenario: Dashboard sin datos
- **WHEN** el usuario accede al dashboard de una comisión sin datos importados
- **THEN** el sistema muestra una pantalla informativa con el botón para ir a importar calificaciones
