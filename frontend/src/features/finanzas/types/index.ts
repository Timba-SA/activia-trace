export interface LiquidacionResponse {
  id: string
  tenant_id: string
  cohorte_id: string
  periodo: string
  usuario_id: string
  rol: string
  comisiones: string[]
  monto_base: number
  monto_plus: number
  total: number
  es_nexo: boolean
  excluido_por_factura: boolean
  estado: string
  created_at: string
  updated_at: string
}

export interface LiquidacionListResponse {
  items: LiquidacionResponse[]
  total: number
  page: number
  page_size: number
}

export interface LiquidacionCalcularRequest {
  cohorte_id: string
  periodo: string
}

export interface LiquidacionHistorialResponse {
  items: LiquidacionResponse[]
  total: number
  page: number
  page_size: number
}

export interface SalarioBaseCreateRequest {
  rol: string
  monto: number
  desde: string
  hasta?: string | null
}

export interface SalarioBaseUpdateRequest {
  monto?: number
  desde?: string
  hasta?: string | null
}

export interface SalarioBaseResponse {
  id: string
  tenant_id: string
  rol: string
  monto: number
  desde: string
  hasta: string | null
  created_at: string
  updated_at: string
}

export interface SalarioPlusCreateRequest {
  grupo: string
  rol: string
  descripcion?: string | null
  monto: number
  tope_acumulacion?: number | null
  desde: string
  hasta?: string | null
}

export interface SalarioPlusUpdateRequest {
  grupo?: string
  rol?: string
  descripcion?: string
  monto?: number
  tope_acumulacion?: number | null
  desde?: string
  hasta?: string | null
}

export interface SalarioPlusResponse {
  id: string
  tenant_id: string
  grupo: string
  rol: string
  descripcion: string | null
  monto: number
  tope_acumulacion: number | null
  desde: string
  hasta: string | null
  created_at: string
  updated_at: string
}

export interface FacturaCreateRequest {
  usuario_id: string
  periodo: string
  detalle?: string | null
  referencia_archivo: string
  tamano_kb?: number | null
}

export interface FacturaResponse {
  id: string
  tenant_id: string
  usuario_id: string
  periodo: string
  detalle: string | null
  referencia_archivo: string
  tamano_kb: number | null
  estado: string
  cargada_at: string
  abonada_at: string | null
  created_at: string
  updated_at: string
}

export interface FacturaListResponse {
  items: FacturaResponse[]
  total: number
  page: number
  page_size: number
}

export interface FacturaEstadoUpdate {
  estado: string
}
