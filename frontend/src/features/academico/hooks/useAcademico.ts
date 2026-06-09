import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useComision } from '../context/AcademicoContext'
import * as api from '../services/api'

export { useComision }

function comisionParams(materiaId: string | null, cohorteId: string | null) {
  return { enabled: !!materiaId && !!cohorteId, materiaId: materiaId!, cohorteId: cohorteId! }
}

export function useMaterias() {
  return useQuery({ queryKey: ['materias'], queryFn: api.getMaterias, staleTime: 5 * 60 * 1000 })
}

export function useCohortes() {
  return useQuery({ queryKey: ['cohortes'], queryFn: api.getCohortes, staleTime: 5 * 60 * 1000 })
}

export function useCalificaciones() {
  const { materiaId, cohorteId } = useComision()
  const { enabled, materiaId: m, cohorteId: c } = comisionParams(materiaId, cohorteId)
  return useQuery({ queryKey: ['calificaciones', m, c], queryFn: () => api.getCalificaciones(m, c), enabled })
}

export function useImportarCalificaciones() {
  const qc = useQueryClient()
  const { materiaId, cohorteId } = useComision()
  return useMutation({
    mutationFn: (file: File) => api.importarCalificaciones(materiaId!, cohorteId!, file),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['calificaciones'] }),
  })
}

export function useConfirmarCalificaciones() {
  const qc = useQueryClient()
  const { materiaId, cohorteId } = useComision()
  return useMutation({
    mutationFn: (actividades: string[]) => api.confirmarCalificaciones(materiaId!, cohorteId!, actividades),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['calificaciones'] }),
  })
}

export function useVaciarCalificaciones() {
  const qc = useQueryClient()
  const { materiaId, cohorteId } = useComision()
  return useMutation({
    mutationFn: () => api.vaciarCalificaciones(materiaId!, cohorteId!),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['calificaciones'] }),
  })
}

export function useUmbral() {
  const { materiaId } = useComision()
  return useQuery({ queryKey: ['umbral', materiaId], queryFn: () => api.getUmbral(materiaId!), enabled: !!materiaId, staleTime: 5 * 60 * 1000 })
}

export function useSetUmbral() {
  const qc = useQueryClient()
  const { materiaId } = useComision()
  return useMutation({
    mutationFn: (porcentaje: number) => api.setUmbral(materiaId!, porcentaje),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['umbral'] }),
  })
}

export function useAtrasados() {
  const { materiaId, cohorteId } = useComision()
  const { enabled, materiaId: m, cohorteId: c } = comisionParams(materiaId, cohorteId)
  return useQuery({ queryKey: ['atrasados', m, c], queryFn: () => api.getAtrasados(m, c), enabled })
}

export function useRanking() {
  const { materiaId, cohorteId } = useComision()
  const { enabled, materiaId: m, cohorteId: c } = comisionParams(materiaId, cohorteId)
  return useQuery({ queryKey: ['ranking', m, c], queryFn: () => api.getRanking(m, c), enabled })
}

export function useNotasFinales() {
  const { materiaId, cohorteId } = useComision()
  const { enabled, materiaId: m, cohorteId: c } = comisionParams(materiaId, cohorteId)
  return useQuery({ queryKey: ['notas-finales', m, c], queryFn: () => api.getNotasFinales(m, c), enabled })
}

export function useEntregasSinCorregir() {
  const { materiaId, cohorteId } = useComision()
  const { enabled, materiaId: m, cohorteId: c } = comisionParams(materiaId, cohorteId)
  return useQuery({ queryKey: ['entregas-sin-corregir', m, c], queryFn: () => api.getEntregasSinCorregir(m, c), enabled })
}

export function useSubirReporteFinalizacion() {
  const qc = useQueryClient()
  const { materiaId, cohorteId } = useComision()
  return useMutation({
    mutationFn: (file: File) => api.subirReporteFinalizacion(materiaId!, cohorteId!, file),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['entregas-sin-corregir'] }),
  })
}

export function usePreviewComunicacion() {
  const { materiaId, cohorteId } = useComision()
  return useMutation({
    mutationFn: (alumnoIds: string[]) => api.previewComunicacion(materiaId!, cohorteId!, alumnoIds),
  })
}

export function useEnviarComunicacion() {
  const { materiaId, cohorteId } = useComision()
  return useMutation({
    mutationFn: (params: { alumnoIds: string[]; asunto: string; cuerpo: string }) =>
      api.enviarComunicacion(materiaId!, cohorteId!, params.alumnoIds, params.asunto, params.cuerpo),
  })
}

export function useComunicacionTracking(loteId: string | null) {
  return useQuery({
    queryKey: ['comunicacion-tracking', loteId],
    queryFn: () => api.getComunicacionTracking(loteId!),
    enabled: !!loteId,
    refetchInterval: (query) => {
      const data = query.state.data
      if (!data) return 5000
      return data.items.every((i) => i.estado === 'ok' || i.estado === 'fallido' || i.estado === 'cancelado') ? false : 5000
    },
  })
}

export function useMonitoreo() {
  const { materiaId, cohorteId } = useComision()
  const { enabled, materiaId: m, cohorteId: c } = comisionParams(materiaId, cohorteId)
  return useQuery({ queryKey: ['monitoreo', m, c], queryFn: () => api.getMonitoreo(m, c), enabled })
}
