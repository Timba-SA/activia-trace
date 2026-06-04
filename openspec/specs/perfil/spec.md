## ADDED Requirements

### Requirement: Usuario autenticado puede ver su perfil
El sistema SHALL exponer un endpoint `GET /api/perfil` que devuelva los datos del usuario autenticado. Todos los campos de `Usuario` deben ser accesibles. Los campos PII (email, cuil, dni, cbu, alias_cbu) deben ser descifrados antes de la respuesta.

#### Scenario: Obtener perfil propio exitosamente
- **WHEN** un usuario autenticado envía `GET /api/perfil`
- **THEN** el sistema responde 200 con todos los campos del usuario, incluyendo PII descifrada

#### Scenario: Usuario no autenticado intenta obtener perfil
- **WHEN** un request sin token JWT válido envía `GET /api/perfil`
- **THEN** el sistema responde 401 Unauthorized

### Requirement: Usuario autenticado puede editar su perfil
El sistema SHALL exponer un endpoint `PATCH /api/perfil` que permita modificar campos editables: nombre, apellidos, datos bancarios (banco, CBU, alias_cbu), regional, email, legajo_profesional. El campo CUIL SHALL ser rechazado explícitamente con error 422 si se incluye en el body.

#### Scenario: Editar perfil exitosamente
- **WHEN** un usuario autenticado envía `PATCH /api/perfil` con `{"email": "nuevo@email.com", "banco": "Santander"}`
- **THEN** el sistema responde 200 con los datos actualizados, y el email y banco se persisten cifrados

#### Scenario: Intentar modificar CUIL
- **WHEN** un usuario autenticado envía `PATCH /api/perfil` con `{"cuil": "20-12345678-9"}`
- **THEN** el sistema responde 422 con un mensaje indicando que CUIL no es modificable

#### Scenario: Editar perfil con datos inválidos
- **WHEN** un usuario autenticado envía `PATCH /api/perfil` con un email mal formado
- **THEN** el sistema responde 422 con errores de validación

### Requirement: CUIL es readonly para el usuario
El sistema SHALL rechazar cualquier intento de modificar CUIL a través de `PATCH /api/perfil`. Esta validación SHALL ocurrir a nivel de schema Pydantic, no solo en el service.

#### Scenario: Schema rechaza cuil en body
- **WHEN** se define el schema `PerfilUpdate` para PATCH
- **THEN** el schema NO debe incluir el campo `cuil`, o debe tener `extra='forbid'` que lo rechace explícitamente
