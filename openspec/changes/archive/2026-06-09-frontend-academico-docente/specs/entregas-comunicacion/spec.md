## ADDED Requirements

### Requirement: Detectar entregas sin corregir
El sistema SHALL permitir al usuario subir un reporte de finalización de actividades del LMS y mostrar las entregas detectadas como pendientes de corrección.

#### Scenario: Detección con resultados
- **WHEN** el usuario sube un reporte de finalización de actividades
- **THEN** el sistema cruza el reporte con las calificaciones existentes
- **AND** muestra una tabla con alumno, actividad y fecha de entrega para cada posible entrega sin corregir

#### Scenario: Sin entregas sin corregir
- **WHEN** todas las entregas tienen calificación registrada
- **THEN** el sistema muestra mensaje de "sin entregas pendientes"

### Requirement: Exportar entregas sin corregir
El sistema SHALL permitir descargar un archivo CSV con el listado de entregas sin corregir.

#### Scenario: Exportar CSV exitosamente
- **WHEN** el usuario hace clic en "Exportar"
- **THEN** el sistema descarga un archivo CSV con los datos de entregas sin corregir
- **AND** el archivo incluye columnas: alumno, actividad, fecha de entrega

### Requirement: Preview de comunicación
El sistema SHALL generar una previsualización del mensaje (asunto + cuerpo) personalizado para los alumnos seleccionados antes del envío.

#### Scenario: Generar preview
- **WHEN** el usuario selecciona alumnos atrasados y hace clic en "Previsualizar mensaje"
- **THEN** el sistema muestra un side-sheet con asunto y cuerpo del mensaje tal como lo recibirá el destinatario

#### Scenario: Preview con múltiples destinatarios
- **WHEN** el usuario selecciona múltiples alumnos
- **THEN** el sistema permite navegar entre previews individuales dentro del side-sheet
- **AND** muestra un contador "Destinatario X de Y"

### Requirement: Envío masivo de comunicaciones
El sistema SHALL enviar los mensajes a los alumnos seleccionados a través de la cola de comunicaciones del backend.

#### Scenario: Enviar comunicación exitosamente
- **WHEN** el usuario confirma el envío desde el preview
- **THEN** el sistema envía POST al backend
- **AND** redirige al tracking de estado

#### Scenario: Error en envío
- **WHEN** el backend rechaza el envío
- **THEN** el sistema muestra el error y permite reintentar

### Requirement: Tracking de estado en tiempo real
El sistema SHALL mostrar el estado de cada mensaje enviado con actualización periódica. Estados: Pendiente, Enviando, OK, Fallido, Cancelado.

#### Scenario: Tracking muestra estados
- **WHEN** el usuario accede al tracking de un lote de comunicaciones
- **THEN** el sistema muestra una tabla con destinatario y estado actual
- **AND** actualiza los estados automáticamente cada 5 segundos mientras la página esté visible

#### Scenario: Tracking finalizado
- **WHEN** todos los mensajes del lote están en estado OK, Fallido o Cancelado
- **THEN** el sistema detiene la actualización automática
- **AND** muestra un resumen: "X enviados, Y fallidos, Z cancelados"
