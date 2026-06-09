## ADDED Requirements

### Requirement: Importar archivo de calificaciones
El sistema SHALL permitir al usuario subir un archivo exportado del LMS con calificaciones. El sistema SHALL procesar el archivo, detectar columnas de actividades con valores numéricos y textuales, y mostrar una vista previa.

#### Scenario: Upload exitoso con preview
- **WHEN** el usuario sube un archivo de calificaciones válido
- **THEN** el sistema muestra una tabla preview con las actividades detectadas, sus columnas y tipo de valor (numérico o textual)
- **AND** cada actividad tiene un checkbox para incluirla o excluirla del análisis

#### Scenario: Archivo inválido
- **WHEN** el usuario sube un archivo con formato no soportado o corrupto
- **THEN** el sistema muestra un mensaje de error específico y no avanza a preview

### Requirement: Confirmar selección de actividades
El sistema SHALL permitir al usuario seleccionar qué actividades incluir en el análisis y confirmar la importación.

#### Scenario: Confirmar actividades seleccionadas
- **WHEN** el usuario selecciona las actividades deseadas y confirma
- **THEN** el sistema envía la selección al backend
- **AND** redirige al dashboard de la comisión con los datos actualizados

#### Scenario: Error al confirmar
- **WHEN** el backend rechaza la confirmación
- **THEN** el sistema muestra el error y mantiene la preview para reintentar

### Requirement: Vaciar datos de una materia
El sistema SHALL permitir al usuario eliminar todos los datos de calificaciones e ingesta de la comisión seleccionada.

#### Scenario: Vaciar datos exitosamente
- **WHEN** el usuario confirma la acción de vaciar datos
- **THEN** el sistema envía DELETE al backend
- **AND** redirige al dashboard sin datos
- **AND** muestra confirmación de datos eliminados

#### Scenario: Cancelar vaciado
- **WHEN** el usuario hace clic en "Vaciar datos"
- **THEN** el sistema muestra un diálogo de confirmación
- **WHEN** el usuario cancela
- **THEN** no se realiza ninguna acción

### Requirement: Configurar umbral de aprobación
El sistema SHALL permitir al profesor configurar el porcentaje mínimo de aprobación para la materia. Valor por defecto: 60%.

#### Scenario: Configurar umbral
- **WHEN** el usuario modifica el umbral (ej. a 70%)
- **THEN** el sistema envía PUT al backend con el nuevo valor
- **AND** muestra el valor actualizado

#### Scenario: Umbral inválido
- **WHEN** el usuario ingresa un valor fuera de rango 0-100 o no numérico
- **THEN** el sistema muestra error de validación y no envía

### Requirement: Visualizar alumnos atrasados
El sistema SHALL mostrar una tabla de alumnos con actividades faltantes o con nota inferior al umbral configurado. La tabla SHALL ser filtrable por nombre de alumno y actividad.

#### Scenario: Tabla de atrasados con datos
- **WHEN** la comisión tiene datos y el usuario accede a la vista de atrasados
- **THEN** el sistema muestra una tabla con nombre del alumno, actividades faltantes, nota promedio y estado (aprobado/en riesgo/atrasado)

#### Scenario: Filtrar atrasados
- **WHEN** el usuario escribe en el campo de búsqueda
- **THEN** el sistema filtra la tabla en tiempo real por nombre de alumno

#### Scenario: Sin alumnos atrasados
- **WHEN** no hay alumnos atrasados en la comisión
- **THEN** el sistema muestra un mensaje informativo y oculta la tabla

### Requirement: Ranking de actividades aprobadas
El sistema SHALL mostrar un ranking ordenado por cantidad de actividades aprobadas por alumno, incluyendo solo alumnos con al menos una actividad aprobada.

#### Scenario: Ranking con datos
- **WHEN** el usuario accede al ranking
- **THEN** el sistema muestra tabla ordenada descendente por cantidad de actividades aprobadas

#### Scenario: Ranking sin datos suficientes
- **WHEN** no hay alumnos con actividades aprobadas
- **THEN** el sistema muestra mensaje de "sin datos"

### Requirement: Notas finales agrupadas
El sistema SHALL agrupar las actividades configuradas y calcular una nota final por alumno, mostrada en tabla.

#### Scenario: Notas finales con datos
- **WHEN** el usuario accede a notas finales
- **THEN** el sistema muestra tabla con nombre del alumno y nota final calculada

### Requirement: Reportes rápidos
El sistema SHALL mostrar métricas consolidadas de la materia: cantidad de actividades, aprobaciones, tendencias.

#### Scenario: Reportes con datos
- **WHEN** el usuario accede a reportes rápidos
- **THEN** el sistema muestra KPIs: total actividades, % aprobación, alumnos en cada categoría

#### Scenario: Reportes sin datos
- **WHEN** no hay datos importados o no hay actividades seleccionadas
- **THEN** el sistema muestra estado informativo
