import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as api from '../services/api'
import type { CarreraCreateRequest, CarreraUpdateRequest, CohorteCreateRequest, CohorteUpdateRequest, MateriaCreateRequest, MateriaUpdateRequest, UsuarioUpdateRequest } from '../types'

export function useCarreras(params?: { limit?: number; offset?: number }) {
  return useQuery({ queryKey: ['carreras', params], queryFn: () => api.listarCarreras(params) })
}

export function useCrearCarrera() {
  const qc = useQueryClient()
  return useMutation({ mutationFn: (data: CarreraCreateRequest) => api.crearCarrera(data), onSuccess: () => qc.invalidateQueries({ queryKey: ['carreras'] }) })
}

export function useActualizarCarrera() {
  const qc = useQueryClient()
  return useMutation({ mutationFn: ({ id, data }: { id: string; data: CarreraUpdateRequest }) => api.actualizarCarrera(id, data), onSuccess: () => qc.invalidateQueries({ queryKey: ['carreras'] }) })
}

export function useCohortes(params?: { carrera_id?: string; limit?: number; offset?: number }) {
  return useQuery({ queryKey: ['cohortes', params], queryFn: () => api.listarCohortes(params) })
}

export function useCrearCohorte() {
  const qc = useQueryClient()
  return useMutation({ mutationFn: (data: CohorteCreateRequest) => api.crearCohorte(data), onSuccess: () => qc.invalidateQueries({ queryKey: ['cohortes'] }) })
}

export function useActualizarCohorte() {
  const qc = useQueryClient()
  return useMutation({ mutationFn: ({ id, data }: { id: string; data: CohorteUpdateRequest }) => api.actualizarCohorte(id, data), onSuccess: () => qc.invalidateQueries({ queryKey: ['cohortes'] }) })
}

export function useMaterias(params?: { carrera_id?: string; limit?: number; offset?: number }) {
  return useQuery({ queryKey: ['materias', params], queryFn: () => api.listarMaterias(params) })
}

export function useCrearMateria() {
  const qc = useQueryClient()
  return useMutation({ mutationFn: (data: MateriaCreateRequest) => api.crearMateria(data), onSuccess: () => qc.invalidateQueries({ queryKey: ['materias'] }) })
}

export function useActualizarMateria() {
  const qc = useQueryClient()
  return useMutation({ mutationFn: ({ id, data }: { id: string; data: MateriaUpdateRequest }) => api.actualizarMateria(id, data), onSuccess: () => qc.invalidateQueries({ queryKey: ['materias'] }) })
}

export function useUsuarios(params?: { nombre?: string; apellido?: string; email?: string; legajo?: string; is_active?: boolean; limit?: number; offset?: number }) {
  return useQuery({ queryKey: ['usuarios', params], queryFn: () => api.listarUsuarios(params) })
}

export function useUsuario(id: string | null) {
  return useQuery({ queryKey: ['usuario', id], queryFn: () => api.obtenerUsuario(id!), enabled: !!id })
}

export function useActualizarUsuario() {
  const qc = useQueryClient()
  return useMutation({ mutationFn: ({ id, data }: { id: string; data: UsuarioUpdateRequest }) => api.actualizarUsuario(id, data), onSuccess: () => { qc.invalidateQueries({ queryKey: ['usuarios'] }); qc.invalidateQueries({ queryKey: ['usuario'] }) } })
}

export function useUltimasAcciones(params?: { accion?: string; actor_id?: string; materia_id?: string; desde?: string; hasta?: string; limit?: number; offset?: number }) {
  return useQuery({ queryKey: ['ultimas-acciones', params], queryFn: () => api.listarUltimasAcciones(params) })
}

export function useMetricasAccionesPorDia(params?: { desde?: string; hasta?: string; materia_id?: string; actor_id?: string }) {
  return useQuery({ queryKey: ['metricas-acciones-dia', params], queryFn: () => api.obtenerMetricasAccionesPorDia(params) })
}

export function useMetricasPorDocente(params?: { desde?: string; hasta?: string; materia_id?: string }) {
  return useQuery({ queryKey: ['metricas-por-docente', params], queryFn: () => api.obtenerMetricasPorDocente(params) })
}

export function useMetricasPorMateria(params?: { desde?: string; hasta?: string; actor_id?: string }) {
  return useQuery({ queryKey: ['metricas-por-materia', params], queryFn: () => api.obtenerMetricasPorMateria(params) })
}

export function useMetricasComunicaciones(params?: { desde?: string; hasta?: string }) {
  return useQuery({ queryKey: ['metricas-comunicaciones', params], queryFn: () => api.obtenerMetricasComunicaciones(params) })
}
