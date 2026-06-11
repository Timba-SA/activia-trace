export interface CarreraCreateRequest {
  nombre: string
  codigo: string
  descripcion?: string | null
  duracion_anios?: number | null
}

export interface CarreraUpdateRequest {
  nombre?: string
  codigo?: string
  descripcion?: string
  duracion_anios?: number
  is_active?: boolean
}

export interface CarreraResponse {
  id: string
  tenant_id: string
  nombre: string
  codigo: string
  descripcion: string | null
  duracion_anios: number | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface CarreraListResponse {
  items: CarreraResponse[]
  total: number
  pages: number
}

export interface CohorteCreateRequest {
  carrera_id: string
  nombre: string
  anio: number
}

export interface CohorteUpdateRequest {
  nombre?: string
  anio?: number
  is_active?: boolean
}

export interface CohorteResponse {
  id: string
  tenant_id: string
  carrera_id: string
  nombre: string
  anio: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface CohorteListResponse {
  items: CohorteResponse[]
  total: number
  pages: number
}

export interface MateriaCreateRequest {
  carrera_id?: string | null
  codigo: string
  nombre: string
  descripcion?: string | null
  carga_horaria?: number | null
}

export interface MateriaUpdateRequest {
  nombre?: string
  descripcion?: string
  carga_horaria?: number
  is_active?: boolean
}

export interface MateriaResponse {
  id: string
  tenant_id: string
  carrera_id: string | null
  codigo: string
  nombre: string
  descripcion: string | null
  carga_horaria: number | null
  is_active: boolean
  created_at: string
  updated_at: string
  deleted_at: string | null
}

export interface MateriaListResponse {
  items: MateriaResponse[]
  total: number
  pages: number
}

export interface UsuarioResponse {
  id: string
  tenant_id: string
  email: string
  nombre: string
  apellido: string
  legajo: string
  is_active: boolean
}

export interface UsuarioListResponse {
  items: UsuarioResponse[]
  total: number
  pages: number
}

export interface UsuarioDetalleResponse {
  id: string
  tenant_id: string
  email: string
  nombre: string
  apellido: string
  legajo: string
  cuil?: string | null
  dni?: string | null
  telefono?: string | null
  is_active: boolean
  roles: string[]
  created_at: string
  updated_at: string
}

export interface UsuarioUpdateRequest {
  nombre?: string
  apellido?: string
  email?: string
  telefono?: string
  is_active?: boolean
}

export interface AuditLogResponse {
  id: string
  tenant_id: string
  accion: string
  actor_id: string
  materia_id: string | null
  detalles: Record<string, unknown> | null
  ip: string | null
  user_agent: string | null
  created_at: string
}

export interface AuditLogListResponse {
  items: AuditLogResponse[]
  total: number
  pages: number
  limit: number
  offset: number
}

export interface MetricaAccionesPorDia {
  fecha: string
  total: number
}

export interface MetricaPorDocente {
  docente_id: string
  nombre: string
  total_acciones: number
}

export interface MetricaPorMateria {
  materia_id: string
  nombre: string
  total_acciones: number
}

export interface MetricaComunicacion {
  docente_id: string
  nombre: string
  total_enviadas: number
  total_recibidas: number
}
