## ADDED Requirements

### Requirement: COORDINADOR/ADMIN can create avisos

The system SHALL allow users with the `avisos:publicar` permission to create Aviso records with the following fields: alcance (Global|PorMateria|PorCohorte|PorRol), materia_id (nullable), cohorte_id (nullable), rol_destino (nullable enum), severidad (Info|Advertencia|Crítico), titulo, cuerpo (rich text), inicio_en (datetime), fin_en (datetime), orden (int), activo (bool), requiere_ack (bool).

#### Scenario: Create aviso as COORDINADOR

- **WHEN** a user with a COORDINADOR role and `avisos:publicar` permission sends a POST request with valid aviso data
- **THEN** the system SHALL return `201 Created` with the created aviso data including an id

#### Scenario: Create aviso as ADMIN

- **WHEN** a user with ADMIN role sends a POST request with valid aviso data
- **THEN** the system SHALL return `201 Created` with the created aviso data

#### Scenario: Create aviso without permission returns 403

- **WHEN** a user without `avisos:publicar` permission sends a POST request to create an aviso
- **THEN** the system SHALL return `403 Forbidden`

#### Scenario: Validation rejects alcance+contexto mismatch

- **WHEN** alcance is PorMateria but materia_id is null
- **THEN** the system SHALL return `422 Unprocessable Entity`

### Requirement: COORDINADOR/ADMIN can update and delete avisos

The system SHALL allow users with `avisos:publicar` to update (PATCH) any field of an aviso and soft-delete (DELETE) an aviso.

#### Scenario: Update aviso fields

- **WHEN** a user with `avisos:publicar` sends a PATCH request with updated aviso fields
- **THEN** the system SHALL update the aviso and return the updated data

#### Scenario: Soft delete aviso

- **WHEN** a user with `avisos:publicar` sends a DELETE request for an existing aviso
- **THEN** the system SHALL set `deleted_at` for that aviso

### Requirement: Users see filtered avisos in mis-avisos

The system SHALL return avisos visible to the authenticated user, filtered by: alcance matching user's context (Global shows to all; PorRol filters by user's roles; PorMateria requires user to be assigned to that materia; PorCohorte requires user to be assigned to that cohorte), activo = true, and vigencia window (inicio_en <= now <= fin_en). Results SHALL be ordered by orden ASC, then created_at DESC.

#### Scenario: Global aviso appears for all users

- **WHEN** a user calls GET /api/avisos/mis-avisos and there is an active Global aviso within vigencia
- **THEN** the aviso SHALL appear in the response

#### Scenario: PorRol aviso only shows for matching role users

- **WHEN** a user with role PROFESOR calls mis-avisos and there is an aviso with rol_destino = PROFESOR
- **THEN** the aviso SHALL appear in the response

#### Scenario: PorRol aviso does not show for non-matching role users

- **WHEN** a user with role ALUMNO calls mis-avisos and there is an aviso with rol_destino = PROFESOR
- **THEN** the aviso SHALL NOT appear in the response

#### Scenario: Aviso outside vigencia window is excluded

- **WHEN** the current datetime is after fin_en of an aviso
- **THEN** the aviso SHALL NOT appear in mis-avisos

#### Scenario: Inactive aviso is excluded

- **WHEN** an aviso has activo = false
- **THEN** the aviso SHALL NOT appear in mis-avisos

#### Scenario: Avisos are ordered by orden then created_at

- **WHEN** multiple avisos match the user's context
- **THEN** they SHALL be returned ordered by orden ASC, then by created_at DESC

### Requirement: Users can acknowledge an aviso

The system SHALL allow any authenticated user to POST /api/avisos/{id}/ack to confirm reading an aviso that has requiere_ack = true. The system SHALL create an AcknowledgmentAviso record with the user's id and current timestamp. The unique constraint on (aviso_id, usuario_id) SHALL prevent duplicate acknowledgments.

#### Scenario: Successful acknowledgment

- **WHEN** a user sends POST /api/avisos/{id}/ack for an aviso with requiere_ack = true
- **THEN** the system SHALL create an AcknowledgmentAviso record and return `200 OK`

#### Scenario: Duplicate acknowledgment is idempotent

- **WHEN** a user sends POST /api/avisos/{id}/ack for an aviso they already acknowledged
- **THEN** the system SHALL return `200 OK` without creating a duplicate record

#### Scenario: Ack for aviso without requiere_ack returns 409

- **WHEN** a user sends POST /api/avisos/{id}/ack for an aviso with requiere_ack = false
- **THEN** the system SHALL return `409 Conflict`

### Requirement: COORDINADOR/ADMIN can view ack stats

The system SHALL allow users with `avisos:publicar` to GET /api/avisos/{id}/stats. The response SHALL include: total_confirmaciones (COUNT of AcknowledgmentAviso records for this aviso).

#### Scenario: Stats return correct counts

- **WHEN** a user with `avisos:publicar` calls GET /api/avisos/{id}/stats
- **THEN** the system SHALL return the count of acknowledgments for that aviso

### Requirement: Avisos have soft delete

Both Aviso and AcknowledgmentAviso SHALL support soft delete via a `deleted_at` column. AcknowledgmentAviso deleted records SHALL be excluded from stats counts.

#### Scenario: Soft-deleted acknowledgment excluded from stats

- **WHEN** an AcknowledgmentAviso record has `deleted_at` set
- **THEN** it SHALL NOT be counted in the aviso stats
