# Spec: Usuarios del Tenant — Listado, Detalle y Edición

## ADDED Requirements

### Requirement: Listar usuarios del tenant
The system MUST display a paginated list of users fetched from GET /api/admin/usuarios with filter controls for nombre, apellido, email, legajo, and is_active. Each row MUST show basic user information excluding PII. The system MUST reflect applied filters in the URL query string.

#### Scenario: List users with text filters
- **WHEN** the user types in the nombre, apellido, email, or legajo filter fields
- **THEN** the system MUST fetch from GET /api/admin/usuarios?nombre={n}&apellido={a}&email={e}&legajo={l} and render a paginated table of matching users

#### Scenario: List users with is_active filter
- **WHEN** the user toggles the is_active filter between "Active", "Inactive", and "All"
- **THEN** the system MUST fetch from GET /api/admin/usuarios?is_active={true|false} and render the filtered list

#### Scenario: List users without filters
- **WHEN** the user navigates to the Usuarios section without applying filters
- **THEN** the system MUST fetch all users from GET /api/admin/usuarios and render the first page of results

#### Scenario: Empty search results
- **WHEN** the applied filters return zero results
- **THEN** the system MUST display an empty-state message indicating no users match the current filters

#### Scenario: Paginated results
- **WHEN** the total result count exceeds the page size
- **THEN** the system MUST show pagination controls (previous, next, page numbers) and fetch the corresponding page via GET /api/admin/usuarios?page={n}

### Requirement: Ver detalle de usuario
The system MUST display a user detail view fetched from GET /api/admin/usuarios/{id}. When the authenticated user has the `usuarios:ver-pii` permission, the detail view MUST include PII fields (DNI, CBU, email, dirección, teléfono). When the user lacks this permission, PII fields MUST be masked or omitted.

#### Scenario: View user detail with PII permission
- **WHEN** the user clicks on a user row and the authenticated session has the `usuarios:ver-pii` permission
- **THEN** the system MUST fetch from GET /api/admin/usuarios/{id} and display all available fields including PII (DNI, CBU, email, dirección, teléfono)

#### Scenario: View user detail without PII permission
- **WHEN** the user clicks on a user row and the authenticated session does NOT have the `usuarios:ver-pii` permission
- **THEN** the system MUST fetch from GET /api/admin/usuarios/{id} and display only non-PII fields, with PII fields shown as masked (e.g., "***") or omitted

#### Scenario: View detail for non-existent user
- **WHEN** the user navigates to a detail view for a user ID that does not exist
- **THEN** the system MUST display a 404 error message with a link back to the user list

### Requirement: Editar usuario
The system MUST provide a form to edit a user via PUT /api/admin/usuarios/{id}. The form MUST pre-populate with current user data. The system MUST validate that email has a valid format and that legajo (when provided) is not a duplicate.

#### Scenario: Edit user successfully
- **WHEN** the user clicks "Editar" on a user detail view, modifies editable fields (nombre, apellido, email, is_active, legajo), and submits
- **THEN** the system MUST PUT to /api/admin/usuarios/{id} with the updated fields, and upon success MUST refresh the detail view and show a success notification

#### Scenario: Edit user with invalid email format
- **WHEN** the user submits the edit form with an invalid email format
- **THEN** the system MUST show an inline validation error on the email field and NOT submit the form

#### Scenario: Edit user with duplicate legajo
- **WHEN** the user submits the edit form with a legajo that already belongs to another user
- **THEN** the system MUST display the API error message indicating duplicate legajo
