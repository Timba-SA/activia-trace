export interface DocenteEquipo {
  id: string
  usuario_id: string
  nombre: string | null
  apellido: string | null
  rol: string
  carrera_id: string | null
  materia_id: string | null
  cohorte_id: string | null
  responsable_id: string | null
  fecha_inicio: string
  fecha_fin: string | null
  comisiones: string[]
  is_active: boolean
}

export interface DocenteEquipoListResponse {
  items: DocenteEquipo[]
  total: number
  pages: number
}

export interface AsignacionMasivaRequest {
  usuario_ids: string[]
  materia_id: string
  carrera_id: string
  cohorte_id: string
  rol: string
  responsable_id?: string | null
  fecha_inicio: string
  fecha_fin: string
  comisiones?: string[]
}

export interface CloneRequest {
  materia_id: string
  carrera_id: string
  cohorte_origen_id: string
  cohorte_destino_id: string
  fecha_inicio: string
  fecha_fin: string
}

export interface VigenciaUpdateRequest {
  materia_id: string
  carrera_id: string
  cohorte_id: string
  fecha_inicio: string
  fecha_fin: string
}

export interface BulkOperationResponse {
  creadas?: number
  afectadas?: number
}

export type AlcanceAviso = 'Global' | 'PorMateria' | 'PorCohorte' | 'PorRol'
export type SeveridadAviso = 'Info' | 'Advertencia' | 'Critico'

export interface AvisoCreateRequest {
  alcance: AlcanceAviso
  materia_id?: string | null
  cohorte_id?: string | null
  rol_destino?: string | null
  severidad: SeveridadAviso
  titulo: string
  cuerpo: string
  inicio_en: string
  fin_en: string
  orden?: number
  activo?: boolean
  requiere_ack?: boolean
}

export interface AvisoUpdateRequest {
  alcance?: AlcanceAviso
  materia_id?: string | null
  cohorte_id?: string | null
  rol_destino?: string | null
  severidad?: SeveridadAviso
  titulo?: string
  cuerpo?: string
  inicio_en?: string
  fin_en?: string
  orden?: number
  activo?: boolean
  requiere_ack?: boolean
}

export interface AvisoResponse {
  id: string
  tenant_id: string
  alcance: AlcanceAviso
  materia_id: string | null
  cohorte_id: string | null
  rol_destino: string | null
  severidad: SeveridadAviso
  titulo: string
  cuerpo: string
  inicio_en: string
  fin_en: string
  orden: number
  activo: boolean
  requiere_ack: boolean
  created_at: string
  updated_at: string
}

export interface AvisoListResponse {
  items: AvisoResponse[]
  total: number
  page: number
  page_size: number
}

export interface AckResponse {
  message: string
}

export interface AvisoStatsResponse {
  total_confirmaciones: number
}

export type EstadoTarea = 'Pendiente' | 'En progreso' | 'Resuelta' | 'Cancelada'

export interface TareaCreateRequest {
  asignado_a: string
  materia_id?: string | null
  contexto_id?: string | null
  descripcion: string
}

export interface TareaUpdateRequest {
  estado?: EstadoTarea
  asignado_a?: string
  descripcion?: string
}

export interface TareaResponse {
  id: string
  tenant_id: string
  estado: EstadoTarea
  asignado_a: string
  asignado_por: string
  materia_id: string | null
  contexto_id: string | null
  descripcion: string
  created_at: string
  updated_at: string
}

export interface TareaListResponse {
  items: TareaResponse[]
  total: number
  page: number
  page_size: number
}

export interface ComentarioTareaCreate {
  texto: string
}

export interface ComentarioTareaResponse {
  id: string
  tarea_id: string
  autor_id: string
  texto: string
  creado_at: string
}

export type DiaSemana = 'Lunes' | 'Martes' | 'Miercoles' | 'Jueves' | 'Viernes' | 'Sabado' | 'Domingo'
export type EstadoInstancia = 'Programado' | 'Realizado' | 'Cancelado'

export interface SlotEncuentroCreateRequest {
  asignacion_id: string
  materia_id: string
  titulo: string
  hora: string
  dia_semana: DiaSemana
  fecha_inicio: string
  cant_semanas: number
  fecha_unica?: string | null
  meet_url?: string | null
  vig_desde: string
  vig_hasta: string
}

export interface SlotEncuentroUpdateRequest {
  titulo?: string
  hora?: string
  dia_semana?: DiaSemana
  fecha_inicio?: string
  cant_semanas?: number
  fecha_unica?: string | null
  meet_url?: string | null
  vig_desde?: string
  vig_hasta?: string
}

export interface SlotEncuentroResponse {
  id: string
  tenant_id: string
  asignacion_id: string
  materia_id: string
  titulo: string
  hora: string
  dia_semana: DiaSemana
  fecha_inicio: string
  cant_semanas: number
  fecha_unica: string | null
  meet_url: string | null
  vig_desde: string
  vig_hasta: string
  created_at: string
  updated_at: string
}

export interface SlotEncuentroListResponse {
  items: SlotEncuentroResponse[]
  total: number
  pages: number
}

export interface InstanciaEncuentroCreateRequest {
  materia_id: string
  slot_id?: string | null
  fecha: string
  hora: string
  titulo: string
  meet_url?: string | null
}

export interface InstanciaEncuentroUpdateRequest {
  estado?: EstadoInstancia
  meet_url?: string
  video_url?: string
  comentario?: string
}

export interface InstanciaEncuentroResponse {
  id: string
  tenant_id: string
  slot_id: string | null
  materia_id: string
  fecha: string
  hora: string
  titulo: string
  estado: EstadoInstancia
  meet_url: string | null
  video_url: string | null
  comentario: string | null
  created_at: string
  updated_at: string
}

export interface InstanciaEncuentroListResponse {
  items: InstanciaEncuentroResponse[]
  total: number
  pages: number
}

export type DiaSemanaGuardia = 'Lunes' | 'Martes' | 'Miercoles' | 'Jueves' | 'Viernes' | 'Sabado' | 'Domingo'
export type EstadoGuardia = 'Pendiente' | 'Realizada' | 'Cancelada'

export interface GuardiaCreateRequest {
  asignacion_id: string
  materia_id: string
  carrera_id: string
  cohorte_id: string
  dia: DiaSemanaGuardia
  horario: string
  estado?: EstadoGuardia
  comentarios?: string | null
}

export interface GuardiaUpdateRequest {
  estado: EstadoGuardia
}

export interface GuardiaResponse {
  id: string
  tenant_id: string
  asignacion_id: string
  materia_id: string
  carrera_id: string
  cohorte_id: string
  dia: DiaSemanaGuardia
  horario: string
  estado: EstadoGuardia
  comentarios: string | null
  creada_at: string
}

export interface GuardiaListResponse {
  items: GuardiaResponse[]
  total: number
  pages: number
}

export type TipoEvaluacion = 'Parcial' | 'TP' | 'Coloquio' | 'Recuperatorio'
export type EstadoReserva = 'Activa' | 'Cancelada'

export interface TurnoDisponibleCreate {
  fecha: string
  hora: string
  cupo_total: number
}

export interface TurnoDisponibleResponse {
  id: string
  fecha: string
  hora: string
  cupo_total: number
  cupos_restantes: number
}

export interface ColoquioCreateRequest {
  materia_id: string
  cohorte_id: string
  tipo: TipoEvaluacion
  instancia: string
  turnos: TurnoDisponibleCreate[]
}

export interface ColoquioUpdateRequest {
  tipo?: TipoEvaluacion
  instancia?: string
  turnos?: TurnoDisponibleCreate[]
}

export interface ColoquioResponse {
  id: string
  tenant_id: string
  materia_id: string
  cohorte_id: string
  tipo: TipoEvaluacion
  instancia: string
  turnos: TurnoDisponibleResponse[]
  created_at: string
  updated_at: string
}

export interface ColoquioListResponse {
  items: ColoquioResponse[]
  total: number
  pages: number
}

export interface ProgramaMateriaCreateRequest {
  materia_id: string
  carrera_id: string
  cohorte_id?: string | null
  titulo: string
  referencia_archivo?: string | null
  aprobado_en?: string | null
}

export interface ProgramaMateriaUpdateRequest {
  titulo?: string
  referencia_archivo?: string
  contenido_html?: string
  aprobado_en?: string
}

export interface ProgramaMateriaResponse {
  id: string
  tenant_id: string
  materia_id: string
  carrera_id: string
  cohorte_id: string | null
  titulo: string
  referencia_archivo: string | null
  contenido_html: string | null
  version: number
  activo: boolean
  aprobado_en: string | null
  created_at: string
  updated_at: string
}

export interface ProgramaMateriaListResponse {
  items: ProgramaMateriaResponse[]
  total: number
  page: number
  page_size: number
}

export interface GenerarContenidoResponse {
  contenido_html: string
}
