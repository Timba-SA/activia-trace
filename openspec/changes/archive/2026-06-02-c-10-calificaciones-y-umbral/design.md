## Context

El sistema ya cuenta con el padrón de alumnos (C-09) y los catálogos académicos (C-06, C-07). Los PROFESORES necesitan importar las calificaciones de sus materias desde el LMS para analizar el estado de los alumnos. Este change implementa el modelo de calificaciones y la configuración de umbrales, siguiendo el patrón existente de import en dos pasos (preview → confirm) usado en padron.

## Goals / Non-Goals

**Goals:**
- Modelo `Calificacion` que soporte notas numéricas (ej: "8.5") y textuales (ej: "Aprobado")
- `aprobado` derivado denormalizado: se calcula al escribir según umbral/valores_aprobados
- Modelo `UmbralMateria` configurable por materia con default 60%
- Import en dos pasos: preview (analiza columnas) → confirm (bulk create)
- 5 endpoints REST con guards de permiso
- Seed del permiso `calificaciones:configurar-umbral`

**Non-Goals:**
- Cómputo de atrasados, rankings o notas finales (C-11)
- Integración con Moodle WS (se importa desde archivo)
- Reportes o exportación
- Umbral a nivel de tenant (solo por materia)

## Decisions

1. **`aprobado` denormalizado (stored)**: se calcula al escribir el registro. Alternativa considerada: calcular en query-time. Se elige stored porque las consultas de listado y filtrado son mucho más rápidas y el costo de recálculo es bajo (solo al importar o al cambiar umbral).
2. **Detección de columnas numéricas vs textuales**: se intenta `float()` en el primer valor no vacío de cada columna. Si todos los valores de la columna parsean a float → es numérica. Si al menos uno falla → es textual. Alternativa: forzar al usuario a declarar el tipo. Se elige detección automática porque es la experiencia esperada (el usuario sube el archivo y el sistema lo interpreta).
3. **Import en dos pasos** (preview → confirm con hash): mismo patrón que padron. El preview retorna un hash SHA-256 del contenido; confirm verifica el hash para detectar cambios entre pasos.
4. **Origen `Importado`/`Manual`**: `metadata_json` almacena los datos crudos del archivo importado para trazabilidad; origen permite distinguir registros creados por import masivo vs entrada manual futura.
5. **FK a `entrada_padron` en lugar de `usuario_id`**: la calificación pertenece a una entrada del padrón, no directamente a un usuario. Esto preserva la trazabilidad incluso cuando el alumno cambia de usuario_id.

## Risks / Trade-offs

- [Cambio de umbral no recalcula histórico] → Almacenar `aprobado` denormalizado significa que cambiar el umbral no afecta calificaciones ya importadas. Se acepta como trade-off; si se necesita recalcular, será una operación batch explícita.
- [Archivos grandes en preview] → El preview carga todo el archivo en memoria. Para archivos típicos de LMS (<1MB) es aceptable. Si se necesita escalar, migrar a streaming.
- [Detección automática errónea] → Si una columna tiene valores mixtos (ej: "8.5" y "N/A"), se clasifica como textual. El usuario puede ver la clasificación en el preview y decidir.
