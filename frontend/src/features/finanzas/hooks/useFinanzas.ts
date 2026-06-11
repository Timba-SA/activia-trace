import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as api from '../services/api'
import type { LiquidacionCalcularRequest, SalarioBaseCreateRequest, SalarioBaseUpdateRequest, SalarioPlusCreateRequest, SalarioPlusUpdateRequest, FacturaCreateRequest, FacturaEstadoUpdate } from '../types'

export function useLiquidaciones(params?: { cohorte_id?: string; periodo?: string; limit?: number; offset?: number }) {
  return useQuery({ queryKey: ['liquidaciones', params], queryFn: () => api.listarLiquidaciones(params) })
}

export function useCalcularLiquidacion() {
  const qc = useQueryClient()
  return useMutation({ mutationFn: (data: LiquidacionCalcularRequest) => api.calcularLiquidacion(data), onSuccess: () => qc.invalidateQueries({ queryKey: ['liquidaciones'] }) })
}

export function useCerrarLiquidacion() {
  const qc = useQueryClient()
  return useMutation({ mutationFn: (id: string) => api.cerrarLiquidacion(id), onSuccess: () => qc.invalidateQueries({ queryKey: ['liquidaciones'] }) })
}

export function useHistorialLiquidaciones(params?: { cohorte_id?: string; periodo?: string; limit?: number; offset?: number }) {
  return useQuery({ queryKey: ['historial-liquidaciones', params], queryFn: () => api.historialLiquidaciones(params) })
}

export function useExportarLiquidaciones() {
  return useMutation({ mutationFn: (data: { cohorte_id: string; periodo: string }) => api.exportarLiquidaciones(data) })
}

export function useSalariosBase() {
  return useQuery({ queryKey: ['salarios-base'], queryFn: () => api.listarSalariosBase() })
}

export function useCrearSalarioBase() {
  const qc = useQueryClient()
  return useMutation({ mutationFn: (data: SalarioBaseCreateRequest) => api.crearSalarioBase(data), onSuccess: () => qc.invalidateQueries({ queryKey: ['salarios-base'] }) })
}

export function useActualizarSalarioBase() {
  const qc = useQueryClient()
  return useMutation({ mutationFn: ({ id, data }: { id: string; data: SalarioBaseUpdateRequest }) => api.actualizarSalarioBase(id, data), onSuccess: () => qc.invalidateQueries({ queryKey: ['salarios-base'] }) })
}

export function useEliminarSalarioBase() {
  const qc = useQueryClient()
  return useMutation({ mutationFn: (id: string) => api.eliminarSalarioBase(id), onSuccess: () => qc.invalidateQueries({ queryKey: ['salarios-base'] }) })
}

export function useSalariosPlus() {
  return useQuery({ queryKey: ['salarios-plus'], queryFn: () => api.listarSalariosPlus() })
}

export function useCrearSalarioPlus() {
  const qc = useQueryClient()
  return useMutation({ mutationFn: (data: SalarioPlusCreateRequest) => api.crearSalarioPlus(data), onSuccess: () => qc.invalidateQueries({ queryKey: ['salarios-plus'] }) })
}

export function useActualizarSalarioPlus() {
  const qc = useQueryClient()
  return useMutation({ mutationFn: ({ id, data }: { id: string; data: SalarioPlusUpdateRequest }) => api.actualizarSalarioPlus(id, data), onSuccess: () => qc.invalidateQueries({ queryKey: ['salarios-plus'] }) })
}

export function useEliminarSalarioPlus() {
  const qc = useQueryClient()
  return useMutation({ mutationFn: (id: string) => api.eliminarSalarioPlus(id), onSuccess: () => qc.invalidateQueries({ queryKey: ['salarios-plus'] }) })
}

export function useFacturas(params?: { periodo?: string; usuario_id?: string; estado?: string; limit?: number; offset?: number }) {
  return useQuery({ queryKey: ['facturas', params], queryFn: () => api.listarFacturas(params) })
}

export function useCrearFactura() {
  const qc = useQueryClient()
  return useMutation({ mutationFn: (data: FacturaCreateRequest) => api.crearFactura(data), onSuccess: () => qc.invalidateQueries({ queryKey: ['facturas'] }) })
}

export function useCambiarEstadoFactura() {
  const qc = useQueryClient()
  return useMutation({ mutationFn: ({ id, data }: { id: string; data: FacturaEstadoUpdate }) => api.cambiarEstadoFactura(id, data), onSuccess: () => qc.invalidateQueries({ queryKey: ['facturas'] }) })
}
