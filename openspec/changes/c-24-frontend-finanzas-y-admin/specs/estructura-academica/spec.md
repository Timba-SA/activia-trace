# Spec: Estructura Académica — ABM Carreras, Cohortes y Materias

## ADDED Requirements

### Requirement: ABM Carreras
The system MUST provide full CRUD for Carreras via endpoints GET /api/admin/carreras, POST /api/admin/carreras, and PUT /api/admin/carreras/{id}. Each Carrera MUST contain the fields: nombre, codigo, descripcion, duracion_anios, is_active. The list MUST display all carreras in a table. The create and update forms MUST validate that nombre and codigo are required and duracion_anios is a positive integer.

#### Scenario: List all carreras
- **WHEN** the user navigates to the Estructura Académica section and selects "Carreras"
- **THEN** the system MUST fetch from GET /api/admin/carreras and render a table with columns nombre, codigo, descripcion, duracion_anios, is_active

#### Scenario: Create a new carrera
- **WHEN** the user clicks "Nueva Carrera", fills in nombre, codigo, descripcion, duracion_anios, and is_active, and submits
- **THEN** the system MUST POST to /api/admin/carreras with the form data, and upon success MUST refresh the list and show a success notification

#### Scenario: Update an existing carrera
- **WHEN** the user clicks "Editar" on a carrera row, modifies one or more fields, and submits
- **THEN** the system MUST PUT to /api/admin/carreras/{id} with the updated fields, and upon success MUST refresh the list and show a success notification

#### Scenario: Validation error on create with negative duracion_anios
- **WHEN** the user submits a carrera form with duracion_anios set to zero or a negative value
- **THEN** the system MUST show an inline validation error on duracion_anios and NOT submit the form

#### Scenario: Create carrera with duplicate codigo
- **WHEN** the user submits a carrera with a codigo that already exists
- **THEN** the system MUST display the API error message indicating duplicate codigo and NOT create the carrera

### Requirement: ABM Cohortes
The system MUST provide list, create, and update for Cohortes via endpoints GET /api/admin/cohortes (filterable by carrera_id), POST /api/admin/cohortes, and PUT /api/admin/cohortes/{id}. Each Cohorte MUST contain the fields: carrera_id, nombre, anio, is_active. The list MUST filter by carrera_id when a carrera is selected. The create and update forms MUST validate carrera_id and nombre are required.

#### Scenario: List cohortes filtered by carrera
- **WHEN** the user selects a carrera from a dropdown in the Cohortes section
- **THEN** the system MUST fetch from GET /api/admin/cohortes?carrera_id={id} and render a table with columns carrera_id, nombre, anio, is_active

#### Scenario: Create a new cohorte
- **WHEN** the user clicks "Nuevo Cohorte", selects a carrera, fills in nombre and anio, sets is_active, and submits
- **THEN** the system MUST POST to /api/admin/cohortes with the form data, and upon success MUST refresh the list and show a success notification

#### Scenario: Update an existing cohorte
- **WHEN** the user clicks "Editar" on a cohorte row, modifies fields, and submits
- **THEN** the system MUST PUT to /api/admin/cohortes/{id} with the updated fields, and upon success MUST refresh the list and show a success notification

#### Scenario: List cohortes without carrera filter
- **WHEN** the user opens the Cohortes section without selecting a carrera
- **THEN** the system MUST show an empty table or prompt the user to select a carrera first

### Requirement: ABM Materias
The system MUST provide list, create, and update for Materias via endpoints GET /api/admin/materias (filterable by carrera_id), POST /api/admin/materias, and PUT /api/admin/materias/{id}. Each Materia MUST contain the fields: carrera_id, codigo, nombre, descripcion, carga_horaria, is_active. The list MUST filter by carrera_id when a carrera is selected. The create and update forms MUST validate carrera_id, codigo, and nombre are required.

#### Scenario: List materias filtered by carrera
- **WHEN** the user selects a carrera from a dropdown in the Materias section
- **THEN** the system MUST fetch from GET /api/admin/materias?carrera_id={id} and render a table with columns carrera_id, codigo, nombre, descripcion, carga_horaria, is_active

#### Scenario: Create a new materia
- **WHEN** the user clicks "Nueva Materia", selects a carrera, fills in codigo, nombre, descripcion, carga_horaria, and submits
- **THEN** the system MUST POST to /api/admin/materias with the form data, and upon success MUST refresh the list and show a success notification

#### Scenario: Update an existing materia
- **WHEN** the user clicks "Editar" on a materia row, modifies fields, and submits
- **THEN** the system MUST PUT to /api/admin/materias/{id} with the updated fields, and upon success MUST refresh the list and show a success notification

#### Scenario: Create materia with duplicate codigo within same carrera
- **WHEN** the user submits a materia with a codigo that already exists in the selected carrera
- **THEN** the system MUST display the API error message indicating duplicate codigo and NOT create the materia
