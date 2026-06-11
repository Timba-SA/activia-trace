import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import CohortesPage from './CohortesPage'

vi.mock('../services/api', () => ({
  listarCohortes: vi.fn(),
  crearCohorte: vi.fn(),
  actualizarCohorte: vi.fn(),
}))

import * as api from '../services/api'

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <CohortesPage />
    </QueryClientProvider>,
  )
}

describe('CohortesPage', () => {
  it('muestra título', async () => {
    vi.mocked(api.listarCohortes).mockResolvedValue({ items: [], total: 0, pages: 0 })
    renderPage()
    await waitFor(() => expect(screen.getByText('Cohortes')).toBeInTheDocument())
  })

  it('muestra sin cohortes cuando no hay', async () => {
    vi.mocked(api.listarCohortes).mockResolvedValue({ items: [], total: 0, pages: 0 })
    renderPage()
    await waitFor(() => expect(screen.getByText('Sin cohortes')).toBeInTheDocument())
  })

  it('lista cohortes', async () => {
    vi.mocked(api.listarCohortes).mockResolvedValue({
      items: [
        { id: '1', tenant_id: 't1', carrera_id: 'c1', nombre: '2025 A', anio: 2025, is_active: true, created_at: '2025-01-01T00:00:00Z', updated_at: '2025-01-01T00:00:00Z' },
        { id: '2', tenant_id: 't1', carrera_id: 'c1', nombre: '2025 B', anio: 2025, is_active: false, created_at: '2025-01-02T00:00:00Z', updated_at: '2025-01-02T00:00:00Z' },
      ],
      total: 2, pages: 1,
    })
    renderPage()
    await waitFor(() => {
      expect(screen.getByText('2025 A')).toBeInTheDocument()
      expect(screen.getByText('2025 B')).toBeInTheDocument()
    })
  })
})
