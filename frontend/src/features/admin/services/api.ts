import api from '@/shared/services/api'
import type { CarreraCreateRequest, CarreraUpdateRequest, CarreraListResponse, CarreraResponse, CohorteCreateRequest, CohorteUpdateRequest, CohorteListResponse, CohorteResponse, MateriaCreateRequest, MateriaUpdateRequest, MateriaListResponse, MateriaResponse, UsuarioListResponse, UsuarioDetalleResponse, UsuarioUpdateRequest, AuditLogListResponse, MetricaAccionesPorDia } from '../types'

export function listarCarreras(params?: { limit?: number; offset?: number }) {
  return api.get<CarreraListResponse>('/admin/carreras', { params }).then((r) => r.data)
}

export function obtenerCarrera(id: string) {
  return api.get<CarreraResponse>(`/admin/carreras/${id}`).then((r) => r.data)
}

export function crearCarrera(data: CarreraCreateRequest) {
  return api.post<CarreraResponse>('/admin/carreras', data).then((r) => r.data)
}

export function actualizarCarrera(id: string, data: CarreraUpdateRequest) {
  return api.put<CarreraResponse>(`/admin/carreras/${id}`, data).then((r) => r.data)
}

export function listarCohortes(params?: { carrera_id?: string; limit?: number; offset?: number }) {
  return api.get<CohorteListResponse>('/admin/cohortes', { params }).then((r) => r.data)
}

export function obtenerCohorte(id: string) {
  return api.get<CohorteResponse>(`/admin/cohortes/${id}`).then((r) => r.data)
}

export function crearCohorte(data: CohorteCreateRequest) {
  return api.post<CohorteResponse>('/admin/cohortes', data).then((r) => r.data)
}

export function actualizarCohorte(id: string, data: CohorteUpdateRequest) {
  return api.put<CohorteResponse>(`/admin/cohortes/${id}`, data).then((r) => r.data)
}

export function listarMaterias(params?: { carrera_id?: string; limit?: number; offset?: number }) {
  return api.get<MateriaListResponse>('/admin/materias', { params }).then((r) => r.data)
}

export function obtenerMateria(id: string) {
  return api.get<MateriaResponse>(`/admin/materias/${id}`).then((r) => r.data)
}

export function crearMateria(data: MateriaCreateRequest) {
  return api.post<MateriaResponse>('/admin/materias', data).then((r) => r.data)
}

export function actualizarMateria(id: string, data: MateriaUpdateRequest) {
  return api.put<MateriaResponse>(`/admin/materias/${id}`, data).then((r) => r.data)
}

export function listarUsuarios(params?: { nombre?: string; apellido?: string; email?: string; legajo?: string; is_active?: boolean; limit?: number; offset?: number }) {
  return api.get<UsuarioListResponse>('/admin/usuarios', { params }).then((r) => r.data)
}

export function obtenerUsuario(id: string) {
  return api.get<UsuarioDetalleResponse>(`/admin/usuarios/${id}`).then((r) => r.data)
}

export function actualizarUsuario(id: string, data: UsuarioUpdateRequest) {
  return api.put<UsuarioDetalleResponse>(`/admin/usuarios/${id}`, data).then((r) => r.data)
}

export function listarUltimasAcciones(params?: { accion?: string; actor_id?: string; materia_id?: string; desde?: string; hasta?: string; limit?: number; offset?: number }) {
  return api.get<AuditLogListResponse>('/auditoria/ultimas-acciones', { params }).then((r) => r.data)
}

export function obtenerMetricasAccionesPorDia(params?: { desde?: string; hasta?: string; materia_id?: string; actor_id?: string }) {
  return api.get<{ items: MetricaAccionesPorDia[] }>('/auditoria/metricas/acciones-por-dia', { params }).then((r) => r.data)
}

export function obtenerMetricasPorDocente(params?: { desde?: string; hasta?: string; materia_id?: string }) {
  return api.get<{ items: any[] }>('/auditoria/metricas/por-docente', { params }).then((r) => r.data)
}

export function obtenerMetricasPorMateria(params?: { desde?: string; hasta?: string; actor_id?: string }) {
  return api.get<{ items: any[] }>('/auditoria/metricas/por-materia', { params }).then((r) => r.data)
}

export function obtenerMetricasComunicaciones(params?: { desde?: string; hasta?: string }) {
  return api.get<{ items: any[] }>('/auditoria/metricas/comunicaciones', { params }).then((r) => r.data)
}
