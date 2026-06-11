import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import TareasPage from './TareasPage'

vi.mock('../services/api', () => ({
  listarTareas: vi.fn(),
  listarTareasAdmin: vi.fn(),
  crearTarea: vi.fn(),
  actualizarTarea: vi.fn(),
  listarComentarios: vi.fn(),
  agregarComentario: vi.fn(),
}))

import * as api from '../services/api'

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <TareasPage />
    </QueryClientProvider>,
  )
}

describe('TareasPage', () => {
  it('muestra título', async () => {
    vi.mocked(api.listarTareas).mockResolvedValue({ items: [], total: 0, page: 1, page_size: 20 })
    renderPage()
    await waitFor(() => expect(screen.getByText('Tareas internas')).toBeInTheDocument())
  })

  it('muestra sin tareas cuando no hay', async () => {
    vi.mocked(api.listarTareas).mockResolvedValue({ items: [], total: 0, page: 1, page_size: 20 })
    renderPage()
    await waitFor(() => expect(screen.getByText('Sin tareas.')).toBeInTheDocument())
  })

  it('lista tareas del usuario', async () => {
    vi.mocked(api.listarTareas).mockResolvedValue({
      items: [
        { id: '1', tenant_id: 't1', estado: 'PENDIENTE', asignado_a: 'a1', asignado_por: 'a2', materia_id: null, contexto_id: null, descripcion: 'Revisar parcial', created_at: '2025-01-01T00:00:00Z', updated_at: '2025-01-01T00:00:00Z' },
        { id: '2', tenant_id: 't1', estado: 'EN_PROGRESO', asignado_a: 'a1', asignado_por: 'a2', materia_id: null, contexto_id: null, descripcion: 'Corregir TP', created_at: '2025-01-02T00:00:00Z', updated_at: '2025-01-02T00:00:00Z' },
      ],
      total: 2, page: 1, page_size: 20,
    })
    renderPage()
    await waitFor(() => {
      expect(screen.getByText('Revisar parcial')).toBeInTheDocument()
      expect(screen.getByText('Corregir TP')).toBeInTheDocument()
    })
  })

  it('permite crear tarea', async () => {
    const user = userEvent.setup()
    vi.mocked(api.listarTareas).mockResolvedValue({ items: [], total: 0, page: 1, page_size: 20 })
    vi.mocked(api.crearTarea).mockResolvedValue({ id: '3', tenant_id: 't1', estado: 'PENDIENTE', asignado_a: 'a1', asignado_por: 'a2', materia_id: null, contexto_id: null, descripcion: 'Nueva', created_at: '2025-01-03T00:00:00Z', updated_at: '2025-01-03T00:00:00Z' })
    renderPage()
    await waitFor(() => expect(screen.getByText('Nueva tarea')).toBeInTheDocument())
    await user.click(screen.getByText('Nueva tarea'))
    await user.type(screen.getByLabelText(/asignado a/i), 'user-1')
    await user.type(screen.getByLabelText(/descripción/i), 'Nueva tarea de prueba')
    await user.click(screen.getByRole('button', { name: /crear$/i }))
    await waitFor(() => {
      expect(vi.mocked(api.crearTarea)).toHaveBeenCalledWith({ asignado_a: 'user-1', descripcion: 'Nueva tarea de prueba', materia_id: null })
    })
  })
})
