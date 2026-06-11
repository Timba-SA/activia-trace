import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import CarrerasPage from './CarrerasPage'

vi.mock('../services/api', () => ({
  listarCarreras: vi.fn(),
  crearCarrera: vi.fn(),
  actualizarCarrera: vi.fn(),
}))

import * as api from '../services/api'

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <CarrerasPage />
    </QueryClientProvider>,
  )
}

describe('CarrerasPage', () => {
  it('muestra título', async () => {
    vi.mocked(api.listarCarreras).mockResolvedValue({ items: [], total: 0, pages: 0 })
    renderPage()
    await waitFor(() => expect(screen.getByText('Carreras')).toBeInTheDocument())
  })

  it('muestra sin carreras cuando no hay', async () => {
    vi.mocked(api.listarCarreras).mockResolvedValue({ items: [], total: 0, pages: 0 })
    renderPage()
    await waitFor(() => expect(screen.getByText('Sin carreras')).toBeInTheDocument())
  })

  it('lista carreras', async () => {
    vi.mocked(api.listarCarreras).mockResolvedValue({
      items: [
        { id: '1', tenant_id: 't1', nombre: 'Ingeniería', codigo: 'ING', descripcion: 'Civil', duracion_anios: 5, is_active: true, created_at: '2025-01-01T00:00:00Z', updated_at: '2025-01-01T00:00:00Z' },
        { id: '2', tenant_id: 't1', nombre: 'Medicina', codigo: 'MED', descripcion: null, duracion_anios: null, is_active: false, created_at: '2025-01-02T00:00:00Z', updated_at: '2025-01-02T00:00:00Z' },
      ],
      total: 2, pages: 1,
    })
    renderPage()
    await waitFor(() => {
      expect(screen.getByText('Ingeniería')).toBeInTheDocument()
      expect(screen.getByText('Medicina')).toBeInTheDocument()
    })
  })
})
