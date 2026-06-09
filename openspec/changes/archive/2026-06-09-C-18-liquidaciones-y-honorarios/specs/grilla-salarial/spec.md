## ADDED Requirements

### Requirement: ABM Salario Base

El sistema SHALL permitir gestionar la grilla de salarios base por rol con vigencia temporal.

#### Scenario: Crear salario base
- **WHEN** se invoca `POST /api/liquidaciones/salarios-base` con `rol`, `monto`, `desde` y opcionalmente `hasta`
- **THEN** el sistema crea un registro SalarioBase y retorna 201

#### Scenario: Crear salario base con overlap de vigencia
- **WHEN** se invoca `POST /api/liquidaciones/salarios-base` y ya existe un registro activo para el mismo rol en el mismo período
- **THEN** el sistema retorna 409 Conflict

#### Scenario: Listar salarios base
- **WHEN** se invoca `GET /api/liquidaciones/salarios-base`
- **THEN** el sistema retorna 200 con todos los registros SalarioBase del tenant

#### Scenario: Actualizar salario base
- **WHEN** se invoca `PUT /api/liquidaciones/salarios-base/{id}` con `monto` y/o fechas de vigencia
- **THEN** el sistema actualiza el registro y retorna 200

#### Scenario: Eliminar salario base
- **WHEN** se invoca `DELETE /api/liquidaciones/salarios-base/{id}`
- **THEN** el sistema realiza soft-delete del registro y retorna 204

### Requirement: ABM Salario Plus

El sistema SHALL permitir gestionar los plus salariales por (grupo, rol) con vigencia y tope configurable.

#### Scenario: Crear plus salarial
- **WHEN** se invoca `POST /api/liquidaciones/plus` con `grupo`, `rol`, `monto`, `desde` y opcionalmente `hasta` y `tope_acumulacion`
- **THEN** el sistema crea un registro SalarioPlus y retorna 201

#### Scenario: Crear plus con tope nulo
- **WHEN** se invoca `POST /api/liquidaciones/plus` sin `tope_acumulacion`
- **THEN** el sistema crea el registro con `tope_acumulacion = NULL` (sin tope)

#### Scenario: Crear plus con tope numérico
- **WHEN** se invoca `POST /api/liquidaciones/plus` con `tope_acumulacion = 5`
- **THEN** el sistema crea el registro con ese tope

#### Scenario: Listar plus
- **WHEN** se invoca `GET /api/liquidaciones/plus`
- **THEN** el sistema retorna 200 con todos los registros SalarioPlus del tenant

#### Scenario: Actualizar plus salarial
- **WHEN** se invoca `PUT /api/liquidaciones/plus/{id}`
- **THEN** el sistema actualiza el registro y retorna 200

#### Scenario: Eliminar plus salarial
- **WHEN** se invoca `DELETE /api/liquidaciones/plus/{id}`
- **THEN** el sistema realiza soft-delete y retorna 204

### Requirement: ABM Materia-Grupo Plus

El sistema SHALL permitir gestionar el mapeo de materias a grupos de plus con vigencia temporal.

#### Scenario: Crear mapeo materia-grupo
- **WHEN** se invoca `POST /api/liquidaciones/materias-grupo` con `materia_id`, `grupo`, `desde` y opcionalmente `hasta`
- **THEN** el sistema crea un registro MateriaGrupoPlus y retorna 201

#### Scenario: Crear mapeo duplicado en mismo período
- **WHEN** se invoca `POST /api/liquidaciones/materias-grupo` para una materia ya asignada al mismo grupo en el mismo período
- **THEN** el sistema retorna 409 Conflict

#### Scenario: Listar mapeos
- **WHEN** se invoca `GET /api/liquidaciones/materias-grupo`
- **THEN** el sistema retorna 200 con todos los registros MateriaGrupoPlus del tenant

#### Scenario: Actualizar mapeo
- **WHEN** se invoca `PUT /api/liquidaciones/materias-grupo/{id}`
- **THEN** el sistema actualiza el registro y retorna 200

#### Scenario: Eliminar mapeo
- **WHEN** se invoca `DELETE /api/liquidaciones/materias-grupo/{id}`
- **THEN** el sistema realiza soft-delete y retorna 204

### Requirement: Resolución de grupo vigente para una materia en un período

El sistema SHALL resolver el grupo de plus de una materia en un período específico buscando el registro MateriaGrupoPlus con `desde <= período <= hasta`.

#### Scenario: Materia sin grupo asignado
- **WHEN** una materia no tiene ningún registro MateriaGrupoPlus vigente para el período
- **THEN** esa materia no genera plus (solo aplica SalarioBase)
