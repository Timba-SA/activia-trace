import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import UsuariosPage from './UsuariosPage'

vi.mock('../services/api', () => ({
  listarUsuarios: vi.fn(),
  obtenerUsuario: vi.fn(),
  actualizarUsuario: vi.fn(),
}))

import * as api from '../services/api'

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <UsuariosPage />
    </QueryClientProvider>,
  )
}

describe('UsuariosPage', () => {
  it('muestra título', async () => {
    vi.mocked(api.listarUsuarios).mockResolvedValue({ items: [], total: 0, pages: 0 })
    renderPage()
    await waitFor(() => expect(screen.getByText('Usuarios')).toBeInTheDocument())
  })

  it('muestra sin usuarios cuando no hay', async () => {
    vi.mocked(api.listarUsuarios).mockResolvedValue({ items: [], total: 0, pages: 0 })
    renderPage()
    await waitFor(() => expect(screen.getByText('Sin usuarios')).toBeInTheDocument())
  })

  it('lista usuarios', async () => {
    vi.mocked(api.listarUsuarios).mockResolvedValue({
      items: [
        { id: '1', tenant_id: 't1', email: 'juan@test.com', nombre: 'Juan', apellido: 'Pérez', legajo: 'L001', is_active: true },
        { id: '2', tenant_id: 't1', email: 'ana@test.com', nombre: 'Ana', apellido: 'García', legajo: 'L002', is_active: false },
      ],
      total: 2, pages: 1,
    })
    renderPage()
    await waitFor(() => {
      expect(screen.getByText('Juan')).toBeInTheDocument()
      expect(screen.getByText('Ana')).toBeInTheDocument()
    })
  })
})
