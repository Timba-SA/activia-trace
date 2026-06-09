import api from '@/shared/services/api'
import type { Materia, Cohorte, ActividadDetectada, Umbral, CalificacionAlumno, AlumnoAtrasado, RankingEntry, NotaFinal, EntregaSinCorregir, ComunicacionPreview, ComunicacionTracking, MonitoreoAlumno } from '../types'

export function getMaterias() {
  return api.get<Materia[]>('/materias').then((r) => r.data)
}

export function getCohortes() {
  return api.get<Cohorte[]>('/cohortes').then((r) => r.data)
}

export function importarCalificaciones(materiaId: string, cohorteId: string, file: File) {
  const fd = new FormData()
  fd.append('file', file)
  fd.append('materia_id', materiaId)
  fd.append('cohorte_id', cohorteId)
  return api.post<{ actividades: ActividadDetectada[] }>('/calificaciones/importar', fd).then((r) => r.data)
}

export function confirmarCalificaciones(materiaId: string, cohorteId: string, actividades: string[]) {
  return api.post('/calificaciones/confirmar', { materia_id: materiaId, cohorte_id: cohorteId, actividades }).then((r) => r.data)
}

export function vaciarCalificaciones(materiaId: string, cohorteId: string) {
  return api.delete('/calificaciones/vaciar', { data: { materia_id: materiaId, cohorte_id: cohorteId } }).then((r) => r.data)
}

export function getCalificaciones(materiaId: string, cohorteId: string) {
  return api.get<CalificacionAlumno[]>('/calificaciones', { params: { materia_id: materiaId, cohorte_id: cohorteId } }).then((r) => r.data)
}

export function getUmbral(materiaId: string) {
  return api.get<Umbral>('/umbral', { params: { materia_id: materiaId } }).then((r) => r.data)
}

export function setUmbral(materiaId: string, porcentaje: number) {
  return api.put('/umbral', { materia_id: materiaId, porcentaje }).then((r) => r.data)
}

export function getAtrasados(materiaId: string, cohorteId: string) {
  return api.get<AlumnoAtrasado[]>('/atrasados', { params: { materia_id: materiaId, cohorte_id: cohorteId } }).then((r) => r.data)
}

export function getRanking(materiaId: string, cohorteId: string) {
  return api.get<RankingEntry[]>('/ranking', { params: { materia_id: materiaId, cohorte_id: cohorteId } }).then((r) => r.data)
}

export function getNotasFinales(materiaId: string, cohorteId: string) {
  return api.get<NotaFinal[]>('/notas-finales', { params: { materia_id: materiaId, cohorte_id: cohorteId } }).then((r) => r.data)
}

export function subirReporteFinalizacion(materiaId: string, cohorteId: string, file: File) {
  const fd = new FormData()
  fd.append('file', file)
  fd.append('materia_id', materiaId)
  fd.append('cohorte_id', cohorteId)
  return api.post<{ entregas: EntregaSinCorregir[] }>('/entregas-sin-corregir', fd).then((r) => r.data)
}

export function getEntregasSinCorregir(materiaId: string, cohorteId: string) {
  return api.get<EntregaSinCorregir[]>('/entregas-sin-corregir', { params: { materia_id: materiaId, cohorte_id: cohorteId } }).then((r) => r.data)
}

export function previewComunicacion(materiaId: string, cohorteId: string, alumnoIds: string[]) {
  return api.post<ComunicacionPreview[]>('/comunicacion/preview', { materia_id: materiaId, cohorte_id: cohorteId, alumno_ids: alumnoIds }).then((r) => r.data)
}

export function enviarComunicacion(materiaId: string, cohorteId: string, alumnoIds: string[], asunto: string, cuerpo: string) {
  return api.post<{ lote_id: string }>('/comunicacion/enviar', { materia_id: materiaId, cohorte_id: cohorteId, alumno_ids: alumnoIds, asunto, cuerpo }).then((r) => r.data)
}

export function getComunicacionTracking(loteId: string) {
  return api.get<ComunicacionTracking>('/comunicacion/tracking', { params: { lote_id: loteId } }).then((r) => r.data)
}

export function getMonitoreo(materiaId: string, cohorteId: string) {
  return api.get<MonitoreoAlumno[]>('/monitoreo', { params: { materia_id: materiaId, cohorte_id: cohorteId } }).then((r) => r.data)
}
