import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('../services/api', () => ({
  listarLiquidaciones: vi.fn(),
  calcularLiquidacion: vi.fn(),
  cerrarLiquidacion: vi.fn(),
  historialLiquidaciones: vi.fn(),
  exportarLiquidaciones: vi.fn(),
}))

import * as api from '../services/api'
import LiquidacionesPage from './LiquidacionesPage'

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <LiquidacionesPage />
    </QueryClientProvider>,
  )
}

beforeEach(() => {
  vi.clearAllMocks()
  vi.mocked(api.listarLiquidaciones).mockResolvedValue({
    items: [], total: 0, page: 1, page_size: 20,
  })
  vi.mocked(api.historialLiquidaciones).mockResolvedValue({
    items: [], total: 0, page: 1, page_size: 20,
  })
  vi.mocked(api.calcularLiquidacion).mockResolvedValue({
    items: [], total: 0, page: 1, page_size: 20,
  })
})

describe('LiquidacionesPage', () => {
  it('muestra título', () => {
    renderPage()
    expect(screen.getByText('Liquidaciones')).toBeInTheDocument()
  })

  it('muestra sin liquidaciones cuando no hay', async () => {
    renderPage()
    expect(await screen.findByText('Sin liquidaciones.')).toBeInTheDocument()
  })

  it('lista liquidaciones', async () => {
    vi.mocked(api.listarLiquidaciones).mockResolvedValue({
      items: [{
        id: '1', tenant_id: 't1', cohorte_id: 'c1', periodo: '2025-01',
        usuario_id: 'user-12345678', rol: 'PROFESOR', comisiones: ['A'],
        monto_base: 50000, monto_plus: 10000, total: 60000,
        es_nexo: false, excluido_por_factura: false,
        estado: 'Calculada', created_at: '2025-01-15T00:00:00Z', updated_at: '2025-01-15T00:00:00Z',
      }],
      total: 1, page: 1, page_size: 20,
    })
    renderPage()
    expect(await screen.findByText('PROFESOR')).toBeInTheDocument()
    expect(screen.getByText('$50000.00')).toBeInTheDocument()
    expect(screen.getByText('$10000.00')).toBeInTheDocument()
    expect(screen.getByText('$60000.00')).toBeInTheDocument()
    expect(screen.getByText('Calculada')).toBeInTheDocument()
  })

  it('permite calcular liquidación', async () => {
    const user = userEvent.setup()
    renderPage()
    const [cohorteInput] = screen.getAllByLabelText('Cohorte ID')
    const [periodoInput] = screen.getAllByLabelText('Periodo')
    await user.type(cohorteInput, 'coh-1')
    await user.type(periodoInput, '2025-01')
    await user.click(screen.getByText('Calcular'))
    expect(vi.mocked(api.calcularLiquidacion)).toHaveBeenCalledWith({
      cohorte_id: 'coh-1', periodo: '2025-01',
    })
  })
})
