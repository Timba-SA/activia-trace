import api from '@/shared/services/api'
import type { LiquidacionListResponse, LiquidacionResponse, LiquidacionCalcularRequest, LiquidacionHistorialResponse, SalarioBaseCreateRequest, SalarioBaseUpdateRequest, SalarioBaseResponse, SalarioPlusCreateRequest, SalarioPlusUpdateRequest, SalarioPlusResponse, FacturaListResponse, FacturaResponse, FacturaCreateRequest, FacturaEstadoUpdate } from '../types'

export function listarLiquidaciones(params?: { cohorte_id?: string; periodo?: string; usuario_id?: string; limit?: number; offset?: number }) {
  return api.get<LiquidacionListResponse>('/liquidaciones', { params }).then((r) => r.data)
}

export function calcularLiquidacion(data: LiquidacionCalcularRequest) {
  return api.post<LiquidacionListResponse>('/liquidaciones/calcular', data).then((r) => r.data)
}

export function cerrarLiquidacion(id: string) {
  return api.post<LiquidacionResponse>(`/liquidaciones/${id}/cerrar`).then((r) => r.data)
}

export function historialLiquidaciones(params?: { cohorte_id?: string; periodo?: string; usuario_id?: string; limit?: number; offset?: number }) {
  return api.get<LiquidacionHistorialResponse>('/liquidaciones/historial', { params }).then((r) => r.data)
}

export function exportarLiquidaciones(data: { cohorte_id: string; periodo: string }) {
  return api.post('/liquidaciones/exportar', data, { responseType: 'blob' }).then((r) => r.data)
}

export function listarSalariosBase() {
  return api.get<SalarioBaseResponse[]>('/liquidaciones/salarios-base').then((r) => r.data)
}

export function crearSalarioBase(data: SalarioBaseCreateRequest) {
  return api.post<SalarioBaseResponse>('/liquidaciones/salarios-base', data).then((r) => r.data)
}

export function actualizarSalarioBase(id: string, data: SalarioBaseUpdateRequest) {
  return api.put<SalarioBaseResponse>(`/liquidaciones/salarios-base/${id}`, data).then((r) => r.data)
}

export function eliminarSalarioBase(id: string) {
  return api.delete(`/liquidaciones/salarios-base/${id}`).then((r) => r.data)
}

export function listarSalariosPlus() {
  return api.get<SalarioPlusResponse[]>('/liquidaciones/plus').then((r) => r.data)
}

export function crearSalarioPlus(data: SalarioPlusCreateRequest) {
  return api.post<SalarioPlusResponse>('/liquidaciones/plus', data).then((r) => r.data)
}

export function actualizarSalarioPlus(id: string, data: SalarioPlusUpdateRequest) {
  return api.put<SalarioPlusResponse>(`/liquidaciones/plus/${id}`, data).then((r) => r.data)
}

export function eliminarSalarioPlus(id: string) {
  return api.delete(`/liquidaciones/plus/${id}`).then((r) => r.data)
}

export function listarFacturas(params?: { periodo?: string; usuario_id?: string; estado?: string; limit?: number; offset?: number }) {
  return api.get<FacturaListResponse>('/facturas', { params }).then((r) => r.data)
}

export function crearFactura(data: FacturaCreateRequest) {
  return api.post<FacturaResponse>('/facturas', data).then((r) => r.data)
}

export function cambiarEstadoFactura(id: string, data: FacturaEstadoUpdate) {
  return api.patch<FacturaResponse>(`/facturas/${id}/estado`, data).then((r) => r.data)
}
