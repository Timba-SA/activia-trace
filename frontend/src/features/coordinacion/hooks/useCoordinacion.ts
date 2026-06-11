import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as api from '../services/api'
import type { AsignacionMasivaRequest, CloneRequest, VigenciaUpdateRequest, AvisoCreateRequest, AvisoUpdateRequest, TareaCreateRequest, TareaUpdateRequest, ComentarioTareaCreate, SlotEncuentroCreateRequest, InstanciaEncuentroCreateRequest, InstanciaEncuentroUpdateRequest, GuardiaCreateRequest, ColoquioCreateRequest, ColoquioUpdateRequest, ProgramaMateriaCreateRequest, ProgramaMateriaUpdateRequest } from '../types'

export function useMisEquipos(params?: { estado?: string; materia_id?: string; rol?: string }) {
  return useQuery({
    queryKey: ['mis-equipos', params],
    queryFn: () => api.getMisEquipos(params),
  })
}

export function useEquipos(params?: { materia_id?: string; carrera_id?: string; cohorte_id?: string; nombre?: string; rol?: string }) {
  return useQuery({
    queryKey: ['equipos', params],
    queryFn: () => api.getEquipos(params),
  })
}

export function useAsignacionMasiva() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: AsignacionMasivaRequest) => api.asignacionMasiva(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['equipos'] })
      qc.invalidateQueries({ queryKey: ['mis-equipos'] })
    },
  })
}

export function useClonarEquipo() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: CloneRequest) => api.clonarEquipo(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['equipos'] })
      qc.invalidateQueries({ queryKey: ['mis-equipos'] })
    },
  })
}

export function useUpdateVigencia() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: VigenciaUpdateRequest) => api.updateVigenciaEquipo(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['equipos'] })
      qc.invalidateQueries({ queryKey: ['mis-equipos'] })
    },
  })
}

export function useExportarEquipo() {
  return useMutation({
    mutationFn: ({ materia_id, carrera_id, cohorte_id }: { materia_id: string; carrera_id: string; cohorte_id: string }) =>
      api.exportarEquipo(materia_id, carrera_id, cohorte_id),
  })
}

export function useAvisos(params?: { limit?: number; offset?: number }) {
  return useQuery({
    queryKey: ['avisos', params],
    queryFn: () => api.listarAvisos(params),
  })
}

export function useCrearAviso() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: AvisoCreateRequest) => api.crearAviso(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['avisos'] }),
  })
}

export function useActualizarAviso() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: AvisoUpdateRequest }) => api.actualizarAviso(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['avisos'] }),
  })
}

export function useEliminarAviso() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => api.eliminarAviso(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['avisos'] }),
  })
}

export function useConfirmarLectura() {
  return useMutation({
    mutationFn: (id: string) => api.confirmarLecturaAviso(id),
  })
}

export function useStatsAviso(id: string | null) {
  return useQuery({
    queryKey: ['avisos-stats', id],
    queryFn: () => api.obtenerStatsAviso(id!),
    enabled: !!id,
  })
}

export function useMisAvisos(params?: { limit?: number; offset?: number }) {
  return useQuery({
    queryKey: ['mis-avisos', params],
    queryFn: () => api.listarMisAvisos(params),
  })
}

export function useTareas(params?: { limit?: number; offset?: number }) {
  return useQuery({
    queryKey: ['tareas', params],
    queryFn: () => api.listarTareas(params),
  })
}

export function useTareasAdmin(params?: { limit?: number; offset?: number }) {
  return useQuery({
    queryKey: ['tareas-admin', params],
    queryFn: () => api.listarTareasAdmin(params),
  })
}

export function useCrearTarea() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: TareaCreateRequest) => api.crearTarea(data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['tareas'] }); qc.invalidateQueries({ queryKey: ['tareas-admin'] }) },
  })
}

export function useActualizarTarea() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: TareaUpdateRequest }) => api.actualizarTarea(id, data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['tareas'] }); qc.invalidateQueries({ queryKey: ['tareas-admin'] }) },
  })
}

export function useComentarios(tareaId: string | null) {
  return useQuery({
    queryKey: ['comentarios', tareaId],
    queryFn: () => api.listarComentarios(tareaId!),
    enabled: !!tareaId,
  })
}

export function useAgregarComentario() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ tareaId, data }: { tareaId: string; data: ComentarioTareaCreate }) => api.agregarComentario(tareaId, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['comentarios'] }),
  })
}

export function useSlotsEncuentro(params?: { materia_id?: string; asignacion_id?: string; limit?: number; offset?: number }) {
  return useQuery({
    queryKey: ['slots-encuentro', params],
    queryFn: () => api.listarSlotsEncuentro(params),
  })
}

export function useCrearSlotEncuentro() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: SlotEncuentroCreateRequest) => api.crearSlotEncuentro(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['slots-encuentro'] }),
  })
}

export function useInstanciasEncuentro(params?: { materia_id?: string; estado?: string; fecha_desde?: string; fecha_hasta?: string; limit?: number; offset?: number }) {
  return useQuery({
    queryKey: ['instancias-encuentro', params],
    queryFn: () => api.listarInstanciasEncuentro(params),
  })
}

export function useCrearInstanciaEncuentro() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: InstanciaEncuentroCreateRequest) => api.crearInstanciaEncuentro(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['instancias-encuentro'] }),
  })
}

export function useActualizarInstanciaEncuentro() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: InstanciaEncuentroUpdateRequest }) => api.actualizarInstanciaEncuentro(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['instancias-encuentro'] }),
  })
}

export function useGuardias(params?: { materia_id?: string; carrera_id?: string; cohorte_id?: string; estado?: string; limit?: number; offset?: number }) {
  return useQuery({
    queryKey: ['guardias', params],
    queryFn: () => api.listarGuardias(params),
  })
}

export function useMisGuardias(params?: { limit?: number; offset?: number }) {
  return useQuery({
    queryKey: ['mis-guardias', params],
    queryFn: () => api.misGuardias(params),
  })
}

export function useCrearGuardia() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: GuardiaCreateRequest) => api.crearGuardia(data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['guardias'] }); qc.invalidateQueries({ queryKey: ['mis-guardias'] }) },
  })
}

export function useActualizarEstadoGuardia() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, estado }: { id: string; estado: string }) => api.actualizarEstadoGuardia(id, { estado }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['guardias'] }); qc.invalidateQueries({ queryKey: ['mis-guardias'] }) },
  })
}

export function useConvocatorias(params?: { materia_id?: string; limit?: number; offset?: number }) {
  return useQuery({
    queryKey: ['convocatorias', params],
    queryFn: () => api.listarConvocatorias(params),
  })
}

export function useCrearConvocatoria() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: ColoquioCreateRequest) => api.crearConvocatoria(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['convocatorias'] }),
  })
}

export function useActualizarConvocatoria() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: ColoquioUpdateRequest }) => api.actualizarConvocatoria(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['convocatorias'] }),
  })
}

export function useCerrarConvocatoria() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => api.cerrarConvocatoria(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['convocatorias'] }),
  })
}

export function useProgramas(params?: { materia_id?: string; carrera_id?: string; cohorte_id?: string; activo?: boolean; incluir_inactivos?: boolean; limit?: number; offset?: number }) {
  return useQuery({
    queryKey: ['programas', params],
    queryFn: () => api.listarProgramas(params),
  })
}

export function useCrearPrograma() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: ProgramaMateriaCreateRequest) => api.crearPrograma(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['programas'] }),
  })
}

export function useActualizarPrograma() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: ProgramaMateriaUpdateRequest }) => api.actualizarPrograma(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['programas'] }),
  })
}

export function useDesactivarPrograma() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => api.desactivarPrograma(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['programas'] }),
  })
}

export function useGenerarContenidoPrograma() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => api.generarContenidoPrograma(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['programas'] }),
  })
}
