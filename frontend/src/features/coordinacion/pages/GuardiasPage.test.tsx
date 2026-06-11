import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import GuardiasPage from './GuardiasPage'

vi.mock('../services/api', () => ({
  listarGuardias: vi.fn(),
  misGuardias: vi.fn(),
  crearGuardia: vi.fn(),
  actualizarEstadoGuardia: vi.fn(),
}))

import * as api from '../services/api'

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <GuardiasPage />
    </QueryClientProvider>,
  )
}

describe('GuardiasPage', () => {
  it('muestra título', async () => {
    vi.mocked(api.listarGuardias).mockResolvedValue({ items: [], total: 0, pages: 0 })
    vi.mocked(api.misGuardias).mockResolvedValue({ items: [], total: 0, pages: 0 })
    renderPage()
    await waitFor(() => expect(screen.getByText('Guardias')).toBeInTheDocument())
  })

  it('muestra sin guardias cuando no hay', async () => {
    vi.mocked(api.listarGuardias).mockResolvedValue({ items: [], total: 0, pages: 0 })
    vi.mocked(api.misGuardias).mockResolvedValue({ items: [], total: 0, pages: 0 })
    renderPage()
    await waitFor(() => expect(screen.getByText('Sin guardias.')).toBeInTheDocument())
  })

  it('lista guardias', async () => {
    vi.mocked(api.listarGuardias).mockResolvedValue({
      items: [
        { id: 'g1', tenant_id: 't1', asignacion_id: 'a1', materia_id: 'm1', carrera_id: 'c1', cohorte_id: 'ch1', dia: 'Lunes', horario: '18:00–20:00', estado: 'Pendiente', comentarios: null, creada_at: '2025-01-01T00:00:00Z' },
        { id: 'g2', tenant_id: 't1', asignacion_id: 'a2', materia_id: 'm2', carrera_id: 'c2', cohorte_id: 'ch2', dia: 'Miercoles', horario: '14:00–16:00', estado: 'Pendiente', comentarios: 'A confirmar', creada_at: '2025-01-02T00:00:00Z' },
      ],
      total: 2, pages: 1,
    })
    vi.mocked(api.misGuardias).mockResolvedValue({ items: [], total: 0, pages: 0 })
    renderPage()
    await waitFor(() => {
      expect(screen.getByText('Lunes – 18:00–20:00')).toBeInTheDocument()
      expect(screen.getByText('Miércoles – 14:00–16:00')).toBeInTheDocument()
    })
  })

  it('permite crear guardia', async () => {
    const user = userEvent.setup()
    vi.mocked(api.listarGuardias).mockResolvedValue({ items: [], total: 0, pages: 0 })
    vi.mocked(api.misGuardias).mockResolvedValue({ items: [], total: 0, pages: 0 })
    vi.mocked(api.crearGuardia).mockResolvedValue({ id: 'g3', tenant_id: 't1', asignacion_id: 'a1', materia_id: 'm1', carrera_id: 'c1', cohorte_id: 'ch1', dia: 'Lunes', horario: '20:00–22:00', estado: 'Pendiente', comentarios: null, creada_at: '2025-01-03T00:00:00Z' })
    renderPage()
    await waitFor(() => expect(screen.getByText('Nueva guardia')).toBeInTheDocument())
    await user.click(screen.getByText('Nueva guardia'))
    await user.type(screen.getByLabelText(/asignación id/i), 'a1')
    await user.type(screen.getByLabelText(/materia id/i), 'm1')
    await user.type(screen.getByLabelText(/carrera id/i), 'c1')
    await user.type(screen.getByLabelText(/cohorte id/i), 'ch1')
    await user.type(screen.getByLabelText(/horario/i), '20:00–22:00')
    await user.click(screen.getByRole('button', { name: /registrar/i }))
    await waitFor(() => {
      expect(vi.mocked(api.crearGuardia)).toHaveBeenCalledWith({
        asignacion_id: 'a1', materia_id: 'm1', carrera_id: 'c1', cohorte_id: 'ch1',
        dia: 'Lunes', horario: '20:00–22:00', comentarios: null,
      })
    })
  })
})
