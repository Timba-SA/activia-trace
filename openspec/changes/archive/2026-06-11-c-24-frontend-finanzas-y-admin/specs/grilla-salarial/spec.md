# Spec: Grilla Salarial — Configuración de Salarios Base, Plus y Grupos

## ADDED Requirements

### Requirement: ABM SalarioBase
The system MUST provide full CRUD (list, create, update, delete) for SalarioBase records via the endpoint GET /api/liquidaciones/salarios-base. Each SalarioBase record MUST contain the fields: rol, monto, desde, hasta. The list view MUST display all records in a table. The create and update forms MUST validate that monto is a positive number, desde is a required date, and hasta (when provided) is after desde.

#### Scenario: List all SalarioBase records
- **WHEN** the user navigates to the Grilla Salarial section and selects "Salarios Base"
- **THEN** the system MUST fetch from GET /api/liquidaciones/salarios-base and render a table with columns rol, monto, desde, hasta

#### Scenario: Create a new SalarioBase record
- **WHEN** the user clicks "Nuevo Salario Base", fills in rol, monto, desde, and optionally hasta, and submits
- **THEN** the system MUST POST to /api/liquidaciones/salarios-base with the form data, and upon success MUST refresh the list and show a success notification

#### Scenario: Update an existing SalarioBase record
- **WHEN** the user clicks "Editar" on a SalarioBase row, modifies one or more fields, and submits
- **THEN** the system MUST PUT to /api/liquidaciones/salarios-base/{id} with the updated fields, and upon success MUST refresh the list and show a success notification

#### Scenario: Delete a SalarioBase record
- **WHEN** the user clicks "Eliminar" on a SalarioBase row and confirms the action
- **THEN** the system MUST DELETE to /api/liquidaciones/salarios-base/{id}, and upon success MUST remove the row from the list and show a success notification

#### Scenario: Validation error on create with negative monto
- **WHEN** the user submits a SalarioBase form with monto set to a negative value
- **THEN** the system MUST show an inline validation error on the monto field and NOT submit the form

### Requirement: ABM SalarioPlus
The system MUST provide full CRUD (list, create, update, delete) for SalarioPlus records. Each SalarioPlus record MUST contain the fields: grupo, rol, descripcion, monto, tope_acumulacion, desde, hasta. The list MUST display all records in a table. The create and update forms MUST validate that monto is a positive number and that tope_acumulacion (when provided) is a positive number.

#### Scenario: List all SalarioPlus records
- **WHEN** the user navigates to the Grilla Salarial section and selects "Plus Salariales"
- **THEN** the system MUST fetch from GET /api/liquidaciones/plus and render a table with columns grupo, rol, descripcion, monto, tope_acumulacion, desde, hasta

#### Scenario: Create a new SalarioPlus record
- **WHEN** the user clicks "Nuevo Plus", fills in all required fields, and submits
- **THEN** the system MUST POST to /api/liquidaciones/plus with the form data, and upon success MUST refresh the list and show a success notification

#### Scenario: Update an existing SalarioPlus record
- **WHEN** the user clicks "Editar" on a SalarioPlus row, modifies fields, and submits
- **THEN** the system MUST PUT to /api/liquidaciones/plus/{id} with the updated fields, and upon success MUST refresh the list and show a success notification

#### Scenario: Delete a SalarioPlus record
- **WHEN** the user clicks "Eliminar" on a SalarioPlus row and confirms the action
- **THEN** the system MUST DELETE to /api/liquidaciones/plus/{id}, and upon success MUST remove the row from the list and show a success notification

### Requirement: ABM MateriaGrupoPlus
The system MUST provide full CRUD (list, create, update, delete) for MateriaGrupoPlus mappings. Each mapping links a materia to a grupo_plus. The list MUST display the current mappings in a table with materia identifier and grupo_plus identifier.

#### Scenario: List all MateriaGrupoPlus mappings
- **WHEN** the user navigates to the Grilla Salarial section and selects "Grupos por Materia"
- **THEN** the system MUST fetch from GET /api/liquidaciones/materias-grupo and render a table showing each materia mapped to its grupo_plus

#### Scenario: Create a new MateriaGrupoPlus mapping
- **WHEN** the user clicks "Nuevo Mapeo", selects a materia and a grupo_plus, and submits
- **THEN** the system MUST POST to /api/liquidaciones/materias-grupo with the mapping data, and upon success MUST refresh the list and show a success notification

#### Scenario: Delete a MateriaGrupoPlus mapping
- **WHEN** the user clicks "Eliminar" on a mapping row and confirms the action
- **THEN** the system MUST DELETE to /api/liquidaciones/materias-grupo/{id}, and upon success MUST remove the mapping from the list

#### Scenario: Create duplicate mapping
- **WHEN** the user attempts to create a MateriaGrupoPlus mapping for a materia that already has a mapping
- **THEN** the system MUST display the API error indicating a duplicate and NOT add the mapping
