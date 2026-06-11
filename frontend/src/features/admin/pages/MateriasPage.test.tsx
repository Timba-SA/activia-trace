import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import MateriasPage from './MateriasPage'

vi.mock('../services/api', () => ({
  listarMaterias: vi.fn(),
  crearMateria: vi.fn(),
  actualizarMateria: vi.fn(),
}))

import * as api from '../services/api'

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <MateriasPage />
    </QueryClientProvider>,
  )
}

describe('MateriasPage', () => {
  it('muestra título', async () => {
    vi.mocked(api.listarMaterias).mockResolvedValue({ items: [], total: 0, pages: 0 })
    renderPage()
    await waitFor(() => expect(screen.getByText('Materias')).toBeInTheDocument())
  })

  it('muestra sin materias cuando no hay', async () => {
    vi.mocked(api.listarMaterias).mockResolvedValue({ items: [], total: 0, pages: 0 })
    renderPage()
    await waitFor(() => expect(screen.getByText('Sin materias')).toBeInTheDocument())
  })

  it('lista materias', async () => {
    vi.mocked(api.listarMaterias).mockResolvedValue({
      items: [
        { id: '1', tenant_id: 't1', carrera_id: 'c1', codigo: 'MAT101', nombre: 'Álgebra', descripcion: 'Lineal', carga_horaria: 80, is_active: true, created_at: '2025-01-01T00:00:00Z', updated_at: '2025-01-01T00:00:00Z', deleted_at: null },
        { id: '2', tenant_id: 't1', carrera_id: null, codigo: 'FIS101', nombre: 'Física', descripcion: null, carga_horaria: null, is_active: false, created_at: '2025-01-02T00:00:00Z', updated_at: '2025-01-02T00:00:00Z', deleted_at: null },
      ],
      total: 2, pages: 1,
    })
    renderPage()
    await waitFor(() => {
      expect(screen.getByText('Álgebra')).toBeInTheDocument()
      expect(screen.getByText('Física')).toBeInTheDocument()
    })
  })
})
