import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import ColoquiosPage from './ColoquiosPage'

vi.mock('../services/api', () => ({
  listarConvocatorias: vi.fn(),
  crearConvocatoria: vi.fn(),
  cerrarConvocatoria: vi.fn(),
}))

import * as api from '../services/api'

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <ColoquiosPage />
    </QueryClientProvider>,
  )
}

describe('ColoquiosPage', () => {
  it('muestra título', async () => {
    vi.mocked(api.listarConvocatorias).mockResolvedValue({ items: [], total: 0, pages: 0 })
    renderPage()
    await waitFor(() => expect(screen.getByText('Coloquios')).toBeInTheDocument())
  })

  it('muestra sin convocatorias cuando no hay', async () => {
    vi.mocked(api.listarConvocatorias).mockResolvedValue({ items: [], total: 0, pages: 0 })
    renderPage()
    await waitFor(() => expect(screen.getByText('Sin convocatorias.')).toBeInTheDocument())
  })

  it('lista convocatorias', async () => {
    vi.mocked(api.listarConvocatorias).mockResolvedValue({
      items: [
        {
          id: 'c1', tenant_id: 't1', materia_id: 'm1', cohorte_id: 'ch1',
          tipo: 'Parcial', instancia: '1er Parcial',
          turnos: [{ id: 't1', fecha: '2025-04-01', hora: '18:00', cupo_total: 30, cupos_restantes: 25 }],
          created_at: '2025-01-01T00:00:00Z', updated_at: '2025-01-01T00:00:00Z',
        },
        {
          id: 'c2', tenant_id: 't1', materia_id: 'm1', cohorte_id: 'ch1',
          tipo: 'Coloquio', instancia: 'Coloquio Diciembre',
          turnos: [
            { id: 't2', fecha: '2025-06-15', hora: '09:00', cupo_total: 40, cupos_restantes: 30 },
            { id: 't3', fecha: '2025-06-16', hora: '09:00', cupo_total: 40, cupos_restantes: 40 },
          ],
          created_at: '2025-02-01T00:00:00Z', updated_at: '2025-02-01T00:00:00Z',
        },
      ],
      total: 2, pages: 1,
    })
    renderPage()
    await waitFor(() => {
      expect(screen.getByText('Parcial – 1er Parcial')).toBeInTheDocument()
      expect(screen.getByText('Coloquio – Coloquio Diciembre')).toBeInTheDocument()
    })
  })
})
