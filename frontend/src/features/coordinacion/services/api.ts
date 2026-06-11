import api from '@/shared/services/api'
import type { DocenteEquipoListResponse, BulkOperationResponse, AsignacionMasivaRequest, CloneRequest, VigenciaUpdateRequest, AvisoListResponse, AvisoResponse, AvisoCreateRequest, AvisoUpdateRequest, AckResponse, AvisoStatsResponse, TareaListResponse, TareaResponse, TareaCreateRequest, TareaUpdateRequest, ComentarioTareaCreate, ComentarioTareaResponse, SlotEncuentroListResponse, SlotEncuentroResponse, SlotEncuentroCreateRequest, InstanciaEncuentroListResponse, InstanciaEncuentroResponse, InstanciaEncuentroCreateRequest, InstanciaEncuentroUpdateRequest, GuardiaListResponse, GuardiaResponse, GuardiaCreateRequest, ColoquioListResponse, ColoquioResponse, ColoquioCreateRequest, ColoquioUpdateRequest, ProgramaMateriaListResponse, ProgramaMateriaResponse, ProgramaMateriaCreateRequest, ProgramaMateriaUpdateRequest, GenerarContenidoResponse } from '../types'

export function getMisEquipos(params?: { estado?: string; materia_id?: string; rol?: string; carrera_id?: string; cohorte_id?: string; limit?: number; offset?: number }) {
  return api.get<DocenteEquipoListResponse>('/equipos/mis-equipos', { params }).then((r) => r.data)
}

export function getEquipos(params?: { materia_id?: string; carrera_id?: string; cohorte_id?: string; usuario_id?: string; nombre?: string; rol?: string; responsable_id?: string; limit?: number; offset?: number }) {
  return api.get<DocenteEquipoListResponse>('/equipos', { params }).then((r) => r.data)
}

export function asignacionMasiva(data: AsignacionMasivaRequest) {
  return api.post<BulkOperationResponse>('/equipos/asignacion-masiva', data).then((r) => r.data)
}

export function clonarEquipo(data: CloneRequest) {
  return api.post<BulkOperationResponse>('/equipos/clonar', data).then((r) => r.data)
}

export function updateVigenciaEquipo(data: VigenciaUpdateRequest) {
  return api.patch<BulkOperationResponse>('/equipos/vigencia', data).then((r) => r.data)
}

export function exportarEquipo(materia_id: string, carrera_id: string, cohorte_id: string) {
  return api.get('/equipos/exportar', { params: { materia_id, carrera_id, cohorte_id }, responseType: 'blob' }).then((r) => r.data)
}

export function listarAvisos(params?: { limit?: number; offset?: number }) {
  return api.get<AvisoListResponse>('/avisos/', { params }).then((r) => r.data)
}

export function crearAviso(data: AvisoCreateRequest) {
  return api.post<AvisoResponse>('/avisos/', data).then((r) => r.data)
}

export function obtenerAviso(id: string) {
  return api.get<AvisoResponse>(`/avisos/${id}`).then((r) => r.data)
}

export function actualizarAviso(id: string, data: AvisoUpdateRequest) {
  return api.patch<AvisoResponse>(`/avisos/${id}`, data).then((r) => r.data)
}

export function eliminarAviso(id: string) {
  return api.delete(`/avisos/${id}`).then((r) => r.data)
}

export function confirmarLecturaAviso(id: string) {
  return api.post<AckResponse>(`/avisos/${id}/ack`).then((r) => r.data)
}

export function obtenerStatsAviso(id: string) {
  return api.get<AvisoStatsResponse>(`/avisos/${id}/stats`).then((r) => r.data)
}

export function listarMisAvisos(params?: { limit?: number; offset?: number }) {
  return api.get<AvisoListResponse>('/avisos/mis-avisos', { params }).then((r) => r.data)
}

export function listarTareas(params?: { limit?: number; offset?: number }) {
  return api.get<TareaListResponse>('/tareas/', { params }).then((r) => r.data)
}

export function crearTarea(data: TareaCreateRequest) {
  return api.post<TareaResponse>('/tareas/', data).then((r) => r.data)
}

export function obtenerTarea(id: string) {
  return api.get<TareaResponse>(`/tareas/${id}`).then((r) => r.data)
}

export function actualizarTarea(id: string, data: TareaUpdateRequest) {
  return api.patch<TareaResponse>(`/tareas/${id}`, data).then((r) => r.data)
}

export function listarTareasAdmin(params?: { limit?: number; offset?: number }) {
  return api.get<TareaListResponse>('/tareas/admin', { params }).then((r) => r.data)
}

export function agregarComentario(tareaId: string, data: ComentarioTareaCreate) {
  return api.post<ComentarioTareaResponse>(`/tareas/${tareaId}/comentarios`, data).then((r) => r.data)
}

export function listarComentarios(tareaId: string) {
  return api.get<ComentarioTareaResponse[]>(`/tareas/${tareaId}/comentarios`).then((r) => r.data)
}

export function listarSlotsEncuentro(params?: { materia_id?: string; asignacion_id?: string; limit?: number; offset?: number }) {
  return api.get<SlotEncuentroListResponse>('/encuentros/slots', { params }).then((r) => r.data)
}

export function crearSlotEncuentro(data: SlotEncuentroCreateRequest) {
  return api.post<SlotEncuentroResponse>('/encuentros/slots', data).then((r) => r.data)
}

export function listarInstanciasEncuentro(params?: { materia_id?: string; estado?: string; fecha_desde?: string; fecha_hasta?: string; limit?: number; offset?: number }) {
  return api.get<InstanciaEncuentroListResponse>('/encuentros/instancias', { params }).then((r) => r.data)
}

export function crearInstanciaEncuentro(data: InstanciaEncuentroCreateRequest) {
  return api.post<InstanciaEncuentroResponse>('/encuentros/instancias', data).then((r) => r.data)
}

export function actualizarInstanciaEncuentro(id: string, data: InstanciaEncuentroUpdateRequest) {
  return api.patch<InstanciaEncuentroResponse>(`/encuentros/instancias/${id}`, data).then((r) => r.data)
}

export function listarInstanciasPorSlot(slotId: string, params?: { limit?: number; offset?: number }) {
  return api.get<InstanciaEncuentroListResponse>(`/encuentros/slots/${slotId}/instancias`, { params }).then((r) => r.data)
}

export function listarGuardias(params?: { materia_id?: string; carrera_id?: string; cohorte_id?: string; asignacion_id?: string; estado?: string; fecha_desde?: string; fecha_hasta?: string; limit?: number; offset?: number }) {
  return api.get<GuardiaListResponse>('/guardias', { params }).then((r) => r.data)
}

export function crearGuardia(data: GuardiaCreateRequest) {
  return api.post<GuardiaResponse>('/guardias', data).then((r) => r.data)
}

export function misGuardias(params?: { limit?: number; offset?: number }) {
  return api.get<GuardiaListResponse>('/guardias/mis-guardias', { params }).then((r) => r.data)
}

export function actualizarEstadoGuardia(id: string, data: { estado: string }) {
  return api.patch<GuardiaResponse>(`/guardias/${id}`, data).then((r) => r.data)
}

export function listarConvocatorias(params?: { materia_id?: string; limit?: number; offset?: number }) {
  return api.get<ColoquioListResponse>('/coloquios/convocatorias', { params }).then((r) => r.data)
}

export function crearConvocatoria(data: ColoquioCreateRequest) {
  return api.post<ColoquioResponse>('/coloquios/convocatorias', data).then((r) => r.data)
}

export function obtenerConvocatoria(id: string) {
  return api.get<ColoquioResponse>(`/coloquios/convocatorias/${id}`).then((r) => r.data)
}

export function actualizarConvocatoria(id: string, data: ColoquioUpdateRequest) {
  return api.patch<ColoquioResponse>(`/coloquios/convocatorias/${id}`, data).then((r) => r.data)
}

export function importarAlumnosColoquio(id: string, data: { alumno_ids: string[] }) {
  return api.post(`/coloquios/convocatorias/${id}/importar-alumnos`, data).then((r) => r.data)
}

export function cerrarConvocatoria(id: string) {
  return api.post(`/coloquios/convocatorias/${id}/cerrar`).then((r) => r.data)
}

export function listarProgramas(params?: { materia_id?: string; carrera_id?: string; cohorte_id?: string; activo?: boolean; incluir_inactivos?: boolean; limit?: number; offset?: number }) {
  return api.get<ProgramaMateriaListResponse>('/programas/', { params }).then((r) => r.data)
}

export function crearPrograma(data: ProgramaMateriaCreateRequest) {
  return api.post<ProgramaMateriaResponse>('/programas/', data).then((r) => r.data)
}

export function obtenerPrograma(id: string) {
  return api.get<ProgramaMateriaResponse>(`/programas/${id}`).then((r) => r.data)
}

export function actualizarPrograma(id: string, data: ProgramaMateriaUpdateRequest) {
  return api.patch<ProgramaMateriaResponse>(`/programas/${id}`, data).then((r) => r.data)
}

export function desactivarPrograma(id: string) {
  return api.delete(`/programas/${id}`).then((r) => r.data)
}

export function generarContenidoPrograma(id: string) {
  return api.post<GenerarContenidoResponse>(`/programas/${id}/generar-contenido`).then((r) => r.data)
}
