export interface Materia {
  id: string
  codigo: string
  nombre: string
  activa: boolean
}

export interface Cohorte {
  id: string
  nombre: string
  carrera_id: string
  carrera_nombre?: string
  activa: boolean
}

export interface ActividadDetectada {
  nombre: string
  tipo_valor: 'numerico' | 'textual'
  incluida: boolean
}

export interface Alumno {
  id: string
  nombre: string
  email: string
  comision?: string
}

export interface CalificacionAlumno {
  alumno: Alumno
  actividades: Record<string, number | string | null>
  promedio?: number
  atrasado: boolean
}

export interface Umbral {
  materia_id: string
  porcentaje: number
}

export interface AlumnoAtrasado {
  alumno: Alumno
  actividades_faltantes: string[]
  nota_promedio: number
  estado: 'aprobado' | 'en_riesgo' | 'atrasado'
}

export interface RankingEntry {
  alumno: Alumno
  actividades_aprobadas: number
  total_actividades: number
}

export interface NotaFinal {
  alumno: Alumno
  nota_final: number
  actividades_incluidas: number
}

export interface EntregaSinCorregir {
  alumno: Alumno
  actividad: string
  fecha_entrega: string
}

export interface ComunicacionPreview {
  alumno_id: string
  asunto: string
  cuerpo: string
}

export interface ComunicacionEnvio {
  alumno_ids: string[]
  asunto: string
  cuerpo: string
  materia_id: string
  cohorte_id: string
}

export interface ComunicacionTracking {
  lote_id: string
  items: Array<{
    alumno_id: string
    alumno_nombre: string
    estado: 'pendiente' | 'enviando' | 'ok' | 'fallido' | 'cancelado'
  }>
}

export interface MonitoreoAlumno {
  alumno: Alumno
  actividades_completadas: number
  total_actividades: number
  nota_promedio: number
}
