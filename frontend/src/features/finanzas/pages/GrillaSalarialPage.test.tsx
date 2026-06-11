import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('../services/api', () => ({
  listarSalariosBase: vi.fn(),
  listarSalariosPlus: vi.fn(),
  crearSalarioBase: vi.fn(),
  crearSalarioPlus: vi.fn(),
  eliminarSalarioBase: vi.fn(),
  eliminarSalarioPlus: vi.fn(),
  actualizarSalarioBase: vi.fn(),
  actualizarSalarioPlus: vi.fn(),
}))

import * as api from '../services/api'
import GrillaSalarialPage from './GrillaSalarialPage'

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <GrillaSalarialPage />
    </QueryClientProvider>,
  )
}

beforeEach(() => {
  vi.clearAllMocks()
  vi.mocked(api.listarSalariosBase).mockResolvedValue([])
  vi.mocked(api.listarSalariosPlus).mockResolvedValue([])
  vi.mocked(api.crearSalarioBase).mockResolvedValue({
    id: 'new-1', tenant_id: 't1', rol: 'PROFESOR', monto: 50000,
    desde: '2025-01-01', hasta: null, created_at: '', updated_at: '',
  })
  vi.mocked(api.crearSalarioPlus).mockResolvedValue({
    id: 'new-1', tenant_id: 't1', grupo: 'G1', rol: 'PROFESOR',
    descripcion: null, monto: 5000, tope_acumulacion: null,
    desde: '2025-01-01', hasta: null, created_at: '', updated_at: '',
  })
  vi.mocked(api.eliminarSalarioBase).mockResolvedValue(undefined)
  vi.mocked(api.eliminarSalarioPlus).mockResolvedValue(undefined)
  vi.mocked(api.actualizarSalarioBase).mockResolvedValue({
    id: '1', tenant_id: 't1', rol: 'PROFESOR', monto: 55000,
    desde: '2025-01-01', hasta: null, created_at: '', updated_at: '',
  })
  vi.mocked(api.actualizarSalarioPlus).mockResolvedValue({
    id: '1', tenant_id: 't1', grupo: 'G1', rol: 'PROFESOR',
    descripcion: null, monto: 5500, tope_acumulacion: null,
    desde: '2025-01-01', hasta: null, created_at: '', updated_at: '',
  })
})

describe('GrillaSalarialPage', () => {
  it('muestra título', () => {
    renderPage()
    expect(screen.getByText('Grilla Salarial')).toBeInTheDocument()
  })

  it('muestra pestaña salarios base', async () => {
    vi.mocked(api.listarSalariosBase).mockResolvedValue([
      {
        id: '1', tenant_id: 't1', rol: 'PROFESOR', monto: 50000,
        desde: '2025-01-01', hasta: null, created_at: '', updated_at: '',
      },
    ])
    renderPage()
    expect(await screen.findByText('PROFESOR')).toBeInTheDocument()
    expect(screen.getByText('$50000.00')).toBeInTheDocument()
    expect(screen.getByText('2025-01-01')).toBeInTheDocument()
  })

  it('permite cambiar a pestaña plus', () => {
    renderPage()
    fireEvent.click(screen.getByText('Plus'))
    expect(screen.getByLabelText('Grupo')).toBeInTheDocument()
    expect(screen.getByText('Nuevo salario plus')).toBeInTheDocument()
  })

  it('permite crear salario base', async () => {
    const user = userEvent.setup()
    renderPage()
    await user.type(screen.getByRole('textbox', { name: 'Rol' }), 'PROFESOR')
    await user.type(screen.getByRole('spinbutton', { name: 'Monto' }), '50000')
    await user.type(screen.getByLabelText('Desde'), '2025-01-01')
    await user.click(screen.getByText('Crear'))
    expect(vi.mocked(api.crearSalarioBase)).toHaveBeenCalledWith({
      rol: 'PROFESOR', monto: 50000, desde: '2025-01-01', hasta: null,
    })
  })
})
