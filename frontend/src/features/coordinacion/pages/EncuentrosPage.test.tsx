import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import EncuentrosPage from './EncuentrosPage'

vi.mock('../services/api', () => ({
  listarInstanciasEncuentro: vi.fn(),
  listarSlotsEncuentro: vi.fn(),
  crearInstanciaEncuentro: vi.fn(),
  crearSlotEncuentro: vi.fn(),
  actualizarInstanciaEncuentro: vi.fn(),
}))

import * as api from '../services/api'

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <EncuentrosPage />
    </QueryClientProvider>,
  )
}

describe('EncuentrosPage', () => {
  it('muestra título', async () => {
    vi.mocked(api.listarInstanciasEncuentro).mockResolvedValue({ items: [], total: 0, pages: 0 })
    vi.mocked(api.listarSlotsEncuentro).mockResolvedValue({ items: [], total: 0, pages: 0 })
    renderPage()
    await waitFor(() => expect(screen.getByText('Encuentros y Guardias')).toBeInTheDocument())
  })

  it('muestra sin instancias cuando no hay', async () => {
    vi.mocked(api.listarInstanciasEncuentro).mockResolvedValue({ items: [], total: 0, pages: 0 })
    vi.mocked(api.listarSlotsEncuentro).mockResolvedValue({ items: [], total: 0, pages: 0 })
    renderPage()
    await waitFor(() => expect(screen.getByText('Sin instancias.')).toBeInTheDocument())
  })

  it('lista instancias', async () => {
    vi.mocked(api.listarInstanciasEncuentro).mockResolvedValue({
      items: [
        { id: 'i1', tenant_id: 't1', slot_id: null, materia_id: 'm1', fecha: '2025-03-10', hora: '10:00', titulo: 'Clase 1', estado: 'Programado', meet_url: null, video_url: null, comentario: null, created_at: '2025-01-01T00:00:00Z', updated_at: '2025-01-01T00:00:00Z' },
        { id: 'i2', tenant_id: 't1', slot_id: null, materia_id: 'm1', fecha: '2025-03-12', hora: '14:00', titulo: 'Clase 2', estado: 'Realizado', meet_url: 'https://meet.google.com/abc', video_url: null, comentario: null, created_at: '2025-01-02T00:00:00Z', updated_at: '2025-01-02T00:00:00Z' },
      ],
      total: 2, pages: 1,
    })
    vi.mocked(api.listarSlotsEncuentro).mockResolvedValue({ items: [], total: 0, pages: 0 })
    renderPage()
    await waitFor(() => {
      expect(screen.getByText('Clase 1')).toBeInTheDocument()
      expect(screen.getByText('Clase 2')).toBeInTheDocument()
    })
  })

  it('muestra slots tab', async () => {
    const user = userEvent.setup()
    vi.mocked(api.listarInstanciasEncuentro).mockResolvedValue({ items: [], total: 0, pages: 0 })
    vi.mocked(api.listarSlotsEncuentro).mockResolvedValue({
      items: [
        { id: 's1', tenant_id: 't1', asignacion_id: 'a1', materia_id: 'm1', titulo: 'Slot Semanal', hora: '18:00', dia_semana: 'Lunes', fecha_inicio: '2025-03-01', cant_semanas: 16, fecha_unica: null, meet_url: null, vig_desde: '2025-03-01', vig_hasta: '2025-07-01', created_at: '2025-01-01T00:00:00Z', updated_at: '2025-01-01T00:00:00Z' },
      ],
      total: 1, pages: 1,
    })
    renderPage()
    await user.click(screen.getByText('Slots'))
    await waitFor(() => {
      expect(screen.getByText('Slot Semanal')).toBeInTheDocument()
    })
  })
})
