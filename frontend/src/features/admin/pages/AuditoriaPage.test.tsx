import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import AuditoriaPage from './AuditoriaPage'

vi.mock('../services/api', () => ({
  listarUltimasAcciones: vi.fn(),
  obtenerMetricasAccionesPorDia: vi.fn(),
  obtenerMetricasPorDocente: vi.fn(),
  obtenerMetricasPorMateria: vi.fn(),
  obtenerMetricasComunicaciones: vi.fn(),
}))

import * as api from '../services/api'

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <AuditoriaPage />
    </QueryClientProvider>,
  )
}

describe('AuditoriaPage', () => {
  it('muestra título', async () => {
    vi.mocked(api.listarUltimasAcciones).mockResolvedValue({ items: [], total: 0, pages: 0, limit: 20, offset: 0 })
    vi.mocked(api.obtenerMetricasAccionesPorDia).mockResolvedValue({ items: [{ fecha: '2025-01-01', total: 10 }] })
    vi.mocked(api.obtenerMetricasPorDocente).mockResolvedValue({ items: [{ docente_id: 'd1', nombre: 'Docente 1', total_acciones: 5 }] })
    vi.mocked(api.obtenerMetricasPorMateria).mockResolvedValue({ items: [{ materia_id: 'm1', nombre: 'Materia 1', total_acciones: 3 }] })
    vi.mocked(api.obtenerMetricasComunicaciones).mockResolvedValue({ items: [{ docente_id: 'd1', nombre: 'Docente 1', total_enviadas: 8, total_recibidas: 12 }] })
    renderPage()
    await waitFor(() => expect(screen.getByText('Auditoría')).toBeInTheDocument())
  })

  it('muestra dashboard tab con métricas', async () => {
    vi.mocked(api.listarUltimasAcciones).mockResolvedValue({ items: [], total: 0, pages: 0, limit: 20, offset: 0 })
    vi.mocked(api.obtenerMetricasAccionesPorDia).mockResolvedValue({
      items: [
        { fecha: '2025-01-01', total: 10 },
        { fecha: '2025-01-02', total: 20 },
      ],
    })
    vi.mocked(api.obtenerMetricasPorDocente).mockResolvedValue({
      items: [
        { docente_id: 'd1', nombre: 'Docente A', total_acciones: 15 },
        { docente_id: 'd2', nombre: 'Docente B', total_acciones: 7 },
      ],
    })
    vi.mocked(api.obtenerMetricasPorMateria).mockResolvedValue({
      items: [
        { materia_id: 'm1', nombre: 'Matemática', total_acciones: 12 },
      ],
    })
    vi.mocked(api.obtenerMetricasComunicaciones).mockResolvedValue({
      items: [
        { docente_id: 'd1', nombre: 'Docente A', total_enviadas: 30, total_recibidas: 20 },
        { docente_id: 'd2', nombre: 'Docente B', total_enviadas: 10, total_recibidas: 5 },
      ],
    })
    renderPage()
    await waitFor(() => {
      // KPI cards with computed totals
      expect(screen.getByText('Acciones totales')).toBeInTheDocument()
      expect(screen.getByText('Docentes activos')).toBeInTheDocument()
      expect(screen.getByText('Materias con actividad')).toBeInTheDocument()
      expect(screen.getByText('Comunicaciones')).toBeInTheDocument()
    })
    await waitFor(() => {
      expect(screen.getByText('30')).toBeInTheDocument() // totalAcciones = 30 (10+20)
      expect(screen.getByText('2')).toBeInTheDocument()   // totalDocentes = 2
      expect(screen.getByText('1')).toBeInTheDocument()   // totalMaterias = 1
      expect(screen.getByText('65')).toBeInTheDocument()  // totalComms = (30+20)+(10+5) = 65
    })
  })
})
