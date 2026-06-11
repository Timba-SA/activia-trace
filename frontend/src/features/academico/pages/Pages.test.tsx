import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import type { CalificacionAlumno, AlumnoAtrasado, RankingEntry, NotaFinal, MonitoreoAlumno } from '../types'

const mockUseCalificaciones = vi.fn<() => { data: CalificacionAlumno[] | undefined; isLoading: boolean }>()
const mockUseAtrasados = vi.fn<() => { data: AlumnoAtrasado[] | undefined; isLoading: boolean }>()
const mockUseRanking = vi.fn<() => { data: RankingEntry[] | undefined; isLoading: boolean }>()
const mockUseNotasFinales = vi.fn<() => { data: NotaFinal[] | undefined; isLoading: boolean }>()
const mockUseEntregasSinCorregir = vi.fn<() => { data: import('../types').EntregaSinCorregir[] | undefined; isLoading: boolean }>()
const mockUseSubirReporte = vi.fn<() => { mutate: Function; isPending: boolean; reset: Function }>()
const mockUseMonitoreo = vi.fn<() => { data: MonitoreoAlumno[] | undefined; isLoading: boolean }>()
const mockUseImportar = vi.fn<() => { mutate: Function; isPending: boolean; reset: Function }>()
const mockUseConfirmar = vi.fn<() => { mutate: Function; isPending: boolean; reset: Function }>()
const mockUseVaciar = vi.fn<() => { mutate: Function; isPending: boolean }>()
const mockUsePreview = vi.fn<() => { mutate: Function; isPending: boolean; data: null; reset: Function }>()
const mockUseEnviar = vi.fn<() => { mutate: Function; isPending: boolean; reset: Function }>()
const mockUseTracking = vi.fn<() => { data: null; isLoading: boolean }>()

vi.mock('../hooks/useAcademico', () => ({
  useComision: () => ({ materiaId: 'mat-1', cohorteId: 'coh-1', setComision: vi.fn(), clear: vi.fn() }),
  useCalificaciones: () => mockUseCalificaciones(),
  useAtrasados: () => mockUseAtrasados(),
  useRanking: () => mockUseRanking(),
  useNotasFinales: () => mockUseNotasFinales(),
  useEntregasSinCorregir: () => mockUseEntregasSinCorregir(),
  useSubirReporteFinalizacion: () => mockUseSubirReporte(),
  useMonitoreo: () => mockUseMonitoreo(),
  useImportarCalificaciones: () => mockUseImportar(),
  useConfirmarCalificaciones: () => mockUseConfirmar(),
  useVaciarCalificaciones: () => mockUseVaciar(),
  useUmbral: () => ({ data: { materia_id: 'mat-1', porcentaje: 60 }, isLoading: false }),
  useSetUmbral: () => ({ mutate: vi.fn(), isPending: false }),
  usePreviewComunicacion: () => mockUsePreview(),
  useEnviarComunicacion: () => mockUseEnviar(),
  useComunicacionTracking: () => mockUseTracking(),
}))

import ComisionPage from './ComisionPage'
import AtrasadosPage from './AtrasadosPage'
import EntregasPage from './EntregasPage'
import MonitoreoPage from './MonitoreoPage'
import NotasFinalesPage from './NotasFinalesPage'
import CalificacionesPage from './CalificacionesPage'
import ComunicacionPage from './ComunicacionPage'

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
  mockUseSubirReporte.mockReturnValue({ mutate: vi.fn(), isPending: false, reset: vi.fn() })
  mockUseImportar.mockReturnValue({ mutate: vi.fn(), isPending: false, reset: vi.fn() })
  mockUseConfirmar.mockReturnValue({ mutate: vi.fn(), isPending: false, reset: vi.fn() })
  mockUseVaciar.mockReturnValue({ mutate: vi.fn(), isPending: false })
  mockUsePreview.mockReturnValue({ mutate: vi.fn(), isPending: false, data: null, reset: vi.fn() })
  mockUseEnviar.mockReturnValue({ mutate: vi.fn(), isPending: false, reset: vi.fn() })
  mockUseTracking.mockReturnValue({ data: null, isLoading: false })
})

describe('ComisionPage', () => {
  it('shows loading skeleton', () => {
    mockUseCalificaciones.mockReturnValue({ data: undefined, isLoading: true })
    renderPage(ComisionPage)
    expect(document.querySelector('.animate-pulse')).toBeTruthy()
  })

  it('shows empty state when no data', () => {
    mockUseCalificaciones.mockReturnValue({ data: [], isLoading: false })
    renderPage(ComisionPage)
    expect(screen.getByText('Comisión sin datos')).toBeDefined()
    expect(screen.getByText('Ir a importar')).toBeDefined()
  })

  it('renders dashboard with metrics', () => {
    mockUseCalificaciones.mockReturnValue({
      data: [
        { alumno: { id: '1', nombre: 'Juan', email: 'j@t.com' }, actividades: { tp1: 80 }, atrasado: false },
        { alumno: { id: '2', nombre: 'Maria', email: 'm@t.com' }, actividades: { tp1: 40 }, atrasado: true },
      ] as CalificacionAlumno[],
      isLoading: false,
    })
    renderPage(ComisionPage)
    expect(screen.getByText('Dashboard')).toBeDefined()
    expect(screen.getByText('2')).toBeDefined()
  })
})

describe('AtrasadosPage', () => {
  it('shows loading skeletons', () => {
    mockUseAtrasados.mockReturnValue({ data: undefined, isLoading: true })
    mockUseRanking.mockReturnValue({ data: undefined, isLoading: true })
    renderPage(AtrasadosPage)
    expect(document.querySelectorAll('.animate-pulse').length).toBe(2)
  })

  it('shows empty states', () => {
    mockUseAtrasados.mockReturnValue({ data: [], isLoading: false })
    mockUseRanking.mockReturnValue({ data: [], isLoading: false })
    renderPage(AtrasadosPage)
    expect(screen.getByText('No hay alumnos atrasados en esta comisión.')).toBeDefined()
    expect(screen.getByText('Sin datos suficientes para mostrar ranking.')).toBeDefined()
  })

  it('renders atrasados table and ranking', () => {
    mockUseAtrasados.mockReturnValue({
      data: [{ alumno: { id: '1', nombre: 'Juan', email: 'j@t.com' }, actividades_faltantes: ['TP1'], nota_promedio: 40, estado: 'atrasado' }] as AlumnoAtrasado[],
      isLoading: false,
    })
    mockUseRanking.mockReturnValue({
      data: [{ alumno: { id: '2', nombre: 'Maria', email: 'm@t.com' }, actividades_aprobadas: 5, total_actividades: 6 }] as RankingEntry[],
      isLoading: false,
    })
    renderPage(AtrasadosPage)
    expect(screen.getByText('Juan')).toBeDefined()
    expect(screen.getByText('Maria')).toBeDefined()
  })
})

describe('EntregasPage', () => {
  it('shows loading skeleton', () => {
    mockUseEntregasSinCorregir.mockReturnValue({ data: undefined, isLoading: true })
    renderPage(EntregasPage)
    expect(document.querySelector('.animate-pulse')).toBeTruthy()
  })

  it('shows empty state', () => {
    mockUseEntregasSinCorregir.mockReturnValue({ data: [], isLoading: false })
    renderPage(EntregasPage)
    expect(screen.getByText('No hay entregas sin corregir. Subí un reporte de finalización para detectarlas.')).toBeDefined()
  })
})

describe('MonitoreoPage', () => {
  it('shows loading skeleton', () => {
    mockUseMonitoreo.mockReturnValue({ data: undefined, isLoading: true })
    renderPage(MonitoreoPage)
    expect(document.querySelector('.animate-pulse')).toBeTruthy()
  })

  it('shows empty state', () => {
    mockUseMonitoreo.mockReturnValue({ data: [], isLoading: false })
    renderPage(MonitoreoPage)
    expect(screen.getByText('No hay datos de monitoreo para esta comisión.')).toBeDefined()
  })

  it('renders monitoreo table', () => {
    mockUseMonitoreo.mockReturnValue({
      data: [
        { alumno: { id: '1', nombre: 'Juan', email: 'j@t.com' }, actividades_completadas: 3, total_actividades: 5, nota_promedio: 70 },
      ] as MonitoreoAlumno[],
      isLoading: false,
    })
    renderPage(MonitoreoPage)
    expect(screen.getByText('Juan')).toBeDefined()
  })
})

describe('NotasFinalesPage', () => {
  it('shows loading skeleton', () => {
    mockUseNotasFinales.mockReturnValue({ data: undefined, isLoading: true })
    renderPage(NotasFinalesPage)
    expect(document.querySelector('.animate-pulse')).toBeTruthy()
  })

  it('shows empty state', () => {
    mockUseNotasFinales.mockReturnValue({ data: [], isLoading: false })
    renderPage(NotasFinalesPage)
    expect(screen.getByText('No hay notas finales calculadas para esta comisión.')).toBeDefined()
  })

  it('renders grades with average', () => {
    mockUseNotasFinales.mockReturnValue({
      data: [
        { alumno: { id: '1', nombre: 'Juan', email: 'j@t.com' }, nota_final: 80, actividades_incluidas: 4 },
        { alumno: { id: '2', nombre: 'Maria', email: 'm@t.com' }, nota_final: 60, actividades_incluidas: 4 },
      ] as NotaFinal[],
      isLoading: false,
    })
    renderPage(NotasFinalesPage)
    expect(screen.getByText('Juan')).toBeDefined()
    expect(screen.getByText('Maria')).toBeDefined()
  })
})

describe('CalificacionesPage', () => {
  it('renders import view with vaciar button', () => {
    mockUseCalificaciones.mockReturnValue({ data: [], isLoading: false })
    renderPage(CalificacionesPage)
    expect(screen.getByText('Importar calificaciones')).toBeDefined()
    expect(screen.getByText('Vaciar datos')).toBeDefined()
    expect(screen.getByText('Hacé clic para subir el archivo')).toBeDefined()
  })
})

describe('ComunicacionPage', () => {
  it('shows empty state when no atrasados', () => {
    mockUseAtrasados.mockReturnValue({ data: [], isLoading: false })
    renderPage(ComunicacionPage)
    expect(screen.getByText('No hay alumnos atrasados para comunicar.')).toBeDefined()
  })

  it('shows atrasados and preview button', () => {
    mockUseAtrasados.mockReturnValue({
      data: [{ alumno: { id: '1', nombre: 'Juan', email: 'j@t.com' }, actividades_faltantes: ['TP1'], nota_promedio: 40, estado: 'atrasado' }] as AlumnoAtrasado[],
      isLoading: false,
    })
    renderPage(ComunicacionPage)
    expect(screen.getByText('Previsualizar mensaje')).toBeDefined()
  })
})
