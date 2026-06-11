import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import ProgramasPage from './ProgramasPage'

vi.mock('../services/api', () => ({
  listarProgramas: vi.fn(),
  crearPrograma: vi.fn(),
  actualizarPrograma: vi.fn(),
  desactivarPrograma: vi.fn(),
  generarContenidoPrograma: vi.fn(),
}))

import * as api from '../services/api'

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <ProgramasPage />
    </QueryClientProvider>,
  )
}

describe('ProgramasPage', () => {
  it('muestra título', async () => {
    vi.mocked(api.listarProgramas).mockResolvedValue({ items: [], total: 0, page: 1, page_size: 20 })
    renderPage()
    await waitFor(() => expect(screen.getByText('Programas de Materias')).toBeInTheDocument())
  })

  it('muestra sin programas cuando no hay', async () => {
    vi.mocked(api.listarProgramas).mockResolvedValue({ items: [], total: 0, page: 1, page_size: 20 })
    renderPage()
    await waitFor(() => expect(screen.getByText('Sin programas.')).toBeInTheDocument())
  })

  it('lista programas', async () => {
    vi.mocked(api.listarProgramas).mockResolvedValue({
      items: [
        { id: 'p1', tenant_id: 't1', materia_id: 'm1', carrera_id: 'c1', cohorte_id: null, titulo: 'Álgebra I', referencia_archivo: null, contenido_html: null, version: 1, activo: true, aprobado_en: null, created_at: '2025-01-01T00:00:00Z', updated_at: '2025-01-01T00:00:00Z' },
        { id: 'p2', tenant_id: 't1', materia_id: 'm2', carrera_id: 'c1', cohorte_id: 'ch1', titulo: 'Física I', referencia_archivo: null, contenido_html: '<p>Contenido</p>', version: 2, activo: false, aprobado_en: null, created_at: '2025-02-01T00:00:00Z', updated_at: '2025-02-01T00:00:00Z' },
      ],
      total: 2, page: 1, page_size: 20,
    })
    renderPage()
    await waitFor(() => {
      expect(screen.getByText('Álgebra I')).toBeInTheDocument()
      expect(screen.getByText('Física I')).toBeInTheDocument()
    })
  })

  it('muestra formulario crear', async () => {
    const user = userEvent.setup()
    vi.mocked(api.listarProgramas).mockResolvedValue({ items: [], total: 0, page: 1, page_size: 20 })
    renderPage()
    await waitFor(() => expect(screen.getByText('Nuevo programa')).toBeInTheDocument())
    await user.click(screen.getByText('Nuevo programa'))
    await waitFor(() => expect(screen.getByText('Crear programa')).toBeInTheDocument())
  })
})
