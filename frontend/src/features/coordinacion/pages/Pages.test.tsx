import { render, screen, fireEvent } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect, vi, beforeEach } from 'vitest'

const mockUseEquipos = vi.fn<() => { data: import('../types').DocenteEquipoListResponse | undefined; isLoading: boolean }>()
const mockUseAvisos = vi.fn<() => { data: import('../types').AvisoListResponse | undefined; isLoading: boolean }>()
const mockCrearAviso = vi.fn<() => { mutate: Function; isPending: boolean; data: import('../types').AvisoResponse | null }>()
const mockActualizarAviso = vi.fn<() => { mutate: Function; isPending: boolean; data: import('../types').AvisoResponse | null }>()
const mockEliminarAviso = vi.fn<() => { mutate: Function; isPending: boolean }>()
const mockStatsAviso = vi.fn<() => { data: import('../types').AvisoStatsResponse | undefined }>()
const mockAsignacion = vi.fn<() => { mutate: Function; isPending: boolean; data: import('../types').BulkOperationResponse | null }>()
const mockClonar = vi.fn<() => { mutate: Function; isPending: boolean; data: import('../types').BulkOperationResponse | null }>()
const mockVigencia = vi.fn<() => { mutate: Function; isPending: boolean; data: import('../types').BulkOperationResponse | null }>()
const mockExportar = vi.fn<() => { mutate: Function; isPending: boolean }>()

vi.mock('../hooks/useCoordinacion', () => ({
  useEquipos: () => mockUseEquipos(),
  useAsignacionMasiva: () => mockAsignacion(),
  useClonarEquipo: () => mockClonar(),
  useUpdateVigencia: () => mockVigencia(),
  useExportarEquipo: () => mockExportar(),
  useAvisos: () => mockUseAvisos(),
  useCrearAviso: () => mockCrearAviso(),
  useActualizarAviso: () => mockActualizarAviso(),
  useEliminarAviso: () => mockEliminarAviso(),
  useStatsAviso: () => mockStatsAviso(),
}))

import EquiposPage from './EquiposPage'
import AvisosPage from './AvisosPage'

function renderPage(Component: React.ComponentType) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter>
        <Component />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

beforeEach(() => {
  vi.clearAllMocks()
  mockAsignacion.mockReturnValue({ mutate: vi.fn(), isPending: false, data: null })
  mockClonar.mockReturnValue({ mutate: vi.fn(), isPending: false, data: null })
  mockVigencia.mockReturnValue({ mutate: vi.fn(), isPending: false, data: null })
  mockExportar.mockReturnValue({ mutate: vi.fn(), isPending: false })
  mockCrearAviso.mockReturnValue({ mutate: vi.fn(), isPending: false, data: null })
  mockActualizarAviso.mockReturnValue({ mutate: vi.fn(), isPending: false, data: null })
  mockEliminarAviso.mockReturnValue({ mutate: vi.fn(), isPending: false })
  mockStatsAviso.mockReturnValue({ data: undefined })
})

describe('EquiposPage', () => {
  it('shows loading state', () => {
    mockUseEquipos.mockReturnValue({ data: undefined, isLoading: true })
    renderPage(EquiposPage)
    expect(document.querySelector('.animate-pulse')).toBeTruthy()
  })

  it('renders equipo list with data', () => {
    mockUseEquipos.mockReturnValue({
      data: {
        items: [{ id: '1', usuario_id: 'u1', nombre: 'Juan', apellido: 'Perez', rol: 'PROFESOR', carrera_id: 'c1', materia_id: 'm1', cohorte_id: 'coh1', responsable_id: null, fecha_inicio: '2026-01-01', fecha_fin: '2026-12-31', comisiones: ['A'], is_active: true }],
        total: 1, pages: 1,
      },
      isLoading: false,
    })
    renderPage(EquiposPage)
    expect(screen.getByText('Perez, Juan')).toBeDefined()
    expect(screen.getByText('PROFESOR')).toBeDefined()
  })

  it('switches to asignacion tab', () => {
    mockUseEquipos.mockReturnValue({ data: undefined, isLoading: true })
    renderPage(EquiposPage)
    fireEvent.click(screen.getByText('Asignación masiva'))
    expect(screen.getByText('Asignación masiva de docentes')).toBeDefined()
  })

  it('switches to clonar tab', () => {
    mockUseEquipos.mockReturnValue({ data: undefined, isLoading: true })
    renderPage(EquiposPage)
    fireEvent.click(screen.getByText('Clonar equipo'))
    expect(screen.getByText('Clonar equipo de cohorte')).toBeDefined()
  })

  it('switches to vigencia tab', () => {
    mockUseEquipos.mockReturnValue({ data: undefined, isLoading: true })
    renderPage(EquiposPage)
    fireEvent.click(screen.getByText('Actualizar vigencia'))
    expect(screen.getByText('Actualizar vigencia del equipo')).toBeDefined()
  })
})

describe('AvisosPage', () => {
  it('shows loading state', () => {
    mockUseAvisos.mockReturnValue({ data: undefined, isLoading: true })
    renderPage(AvisosPage)
    expect(document.querySelector('.animate-pulse')).toBeTruthy()
  })

  it('renders avisos list', () => {
    mockUseAvisos.mockReturnValue({
      data: { items: [{ id: '1', tenant_id: 't1', alcance: 'Global', severidad: 'Critico', titulo: 'Test', cuerpo: 'Cuerpo', inicio_en: '2026-06-01T00:00:00Z', fin_en: '2026-06-30T00:00:00Z', orden: 0, activo: true, requiere_ack: false, materia_id: null, cohorte_id: null, rol_destino: null, created_at: '', updated_at: '' }], total: 1, page: 1, page_size: 20 },
      isLoading: false,
    })
    renderPage(AvisosPage)
    expect(screen.getByText('Test')).toBeDefined()
    expect(screen.getByText('Nuevo aviso')).toBeDefined()
  })

  it('toggles new aviso form', () => {
    mockUseAvisos.mockReturnValue({ data: { items: [], total: 0, page: 1, page_size: 20 }, isLoading: false })
    renderPage(AvisosPage)
    fireEvent.click(screen.getByText('Nuevo aviso'))
    expect(screen.getByText('Crear nuevo aviso')).toBeDefined()
  })
})
