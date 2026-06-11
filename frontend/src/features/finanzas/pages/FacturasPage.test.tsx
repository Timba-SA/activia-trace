import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('../services/api', () => ({
  listarFacturas: vi.fn(),
  crearFactura: vi.fn(),
  cambiarEstadoFactura: vi.fn(),
}))

import * as api from '../services/api'
import FacturasPage from './FacturasPage'

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <FacturasPage />
    </QueryClientProvider>,
  )
}

beforeEach(() => {
  vi.clearAllMocks()
  vi.mocked(api.listarFacturas).mockResolvedValue({
    items: [], total: 0, page: 1, page_size: 20,
  })
  vi.mocked(api.crearFactura).mockResolvedValue({
    id: 'new-1', tenant_id: 't1', usuario_id: 'u1', periodo: '2025-01',
    detalle: null, referencia_archivo: 'fac.pdf', tamano_kb: null,
    estado: 'Pendiente', cargada_at: '2025-01-15T00:00:00Z',
    abonada_at: null, created_at: '', updated_at: '',
  })
})

describe('FacturasPage', () => {
  it('muestra título', () => {
    renderPage()
    expect(screen.getByText('Facturas')).toBeInTheDocument()
  })

  it('muestra sin facturas cuando no hay', async () => {
    renderPage()
    expect(await screen.findByText('Sin facturas.')).toBeInTheDocument()
  })

  it('lista facturas', async () => {
    vi.mocked(api.listarFacturas).mockResolvedValue({
      items: [{
        id: '1', tenant_id: 't1', usuario_id: 'user-12345678', periodo: '2025-01',
        detalle: 'Factura enero', referencia_archivo: 'fac-001.pdf', tamano_kb: 1024,
        estado: 'Pendiente', cargada_at: '2025-01-15T00:00:00Z',
        abonada_at: null, created_at: '', updated_at: '',
      }],
      total: 1, page: 1, page_size: 20,
    })
    renderPage()
    expect(await screen.findByText('2025-01')).toBeInTheDocument()
    expect(screen.getByText('fac-001.pdf')).toBeInTheDocument()
    expect(screen.getAllByText('Pendiente').length).toBeGreaterThanOrEqual(1)
  })
})
