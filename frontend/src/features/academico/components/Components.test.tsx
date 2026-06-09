import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { ImportPreview } from './ImportPreview'
import { AtrasadosTable } from './AtrasadosTable'
import { RankingTable } from './RankingTable'
import { NotasFinalesTable } from './NotasFinalesTable'
import { DashboardMetrics } from './DashboardMetrics'
import { EntregasSinCorregir } from './EntregasSinCorregir'
import { ComunicacionPreview } from './ComunicacionPreview'
import { ComunicacionTracking } from './ComunicacionTracking'
import { MonitoreoAlumnos } from './MonitoreoAlumnos'
import type { AlumnoAtrasado, RankingEntry, NotaFinal, EntregaSinCorregir, MonitoreoAlumno } from '../types'

describe('DashboardMetrics', () => {
  it('renders metrics with correct values', () => {
    render(<DashboardMetrics total={30} atrasados={6} actividades={4} />)
    expect(screen.getByText('30')).toBeDefined()
    expect(screen.getByText('6')).toBeDefined()
    expect(screen.getByText('4')).toBeDefined()
    expect(screen.getByText('(20%)')).toBeDefined()
  })
})

describe('ImportPreview', () => {
  const actividades = [
    { nombre: 'TP1', tipo_valor: 'numerico' as const, incluida: true },
    { nombre: 'TP2', tipo_valor: 'textual' as const, incluida: false },
  ]

  it('renders detected activities', () => {
    render(<ImportPreview actividades={actividades} onConfirm={() => {}} />)
    expect(screen.getByText('TP1')).toBeDefined()
    expect(screen.getByText('TP2')).toBeDefined()
    expect(screen.getByText('Numérico')).toBeDefined()
    expect(screen.getByText('Textual')).toBeDefined()
  })

  it('calls onConfirm with selected activities', () => {
    const onConfirm = vi.fn()
    render(<ImportPreview actividades={actividades} onConfirm={onConfirm} />)
    fireEvent.click(screen.getByText('Confirmar (1 actividades)'))
    expect(onConfirm).toHaveBeenCalledWith(['TP1'])
  })
})

describe('AtrasadosTable', () => {
  const alumnos: AlumnoAtrasado[] = [
    { alumno: { id: '1', nombre: 'Juan Perez', email: 'juan@test.com' }, actividades_faltantes: ['TP1'], nota_promedio: 40, estado: 'atrasado' },
    { alumno: { id: '2', nombre: 'Maria Gomez', email: 'maria@test.com' }, actividades_faltantes: [], nota_promedio: 75, estado: 'aprobado' },
  ]

  it('renders alumnos with states', () => {
    render(<AtrasadosTable alumnos={alumnos} />)
    expect(screen.getByText('Juan Perez')).toBeDefined()
    expect(screen.getByText('Maria Gomez')).toBeDefined()
    expect(screen.getByText('Atrasado')).toBeDefined()
    expect(screen.getByText('Aprobado')).toBeDefined()
  })
})

describe('RankingTable', () => {
  const entries: RankingEntry[] = [
    { alumno: { id: '1', nombre: 'Juan', email: 'juan@test.com' }, actividades_aprobadas: 5, total_actividades: 6 },
  ]

  it('renders ranking rows', () => {
    render(<RankingTable entries={entries} />)
    expect(screen.getByText('Juan')).toBeDefined()
    expect(screen.getByText('5')).toBeDefined()
    expect(screen.getByText('6')).toBeDefined()
  })
})

describe('NotasFinalesTable', () => {
  const notas: NotaFinal[] = [
    { alumno: { id: '1', nombre: 'Juan', email: 'juan@test.com' }, nota_final: 75, actividades_incluidas: 4 },
  ]

  it('renders final grades', () => {
    render(<NotasFinalesTable notas={notas} />)
    expect(screen.getByText('Juan')).toBeDefined()
    expect(screen.getByText('75.0')).toBeDefined()
  })
})

describe('EntregasSinCorregir', () => {
  const entregas: EntregaSinCorregir[] = [
    { alumno: { id: '1', nombre: 'Juan Perez', email: 'juan@test.com' }, actividad: 'TP1', fecha_entrega: '2026-06-01' },
  ]

  it('renders entregas table', () => {
    render(<EntregasSinCorregir entregas={entregas} />)
    expect(screen.getByText('TP1')).toBeDefined()
    expect(screen.getByText('Exportar CSV')).toBeDefined()
  })
})

describe('ComunicacionPreview', () => {
  const previews = [
    { alumno_id: '1', asunto: 'Recordatorio', cuerpo: 'Estimado alumno...' },
    { alumno_id: '2', asunto: 'Recordatorio 2', cuerpo: 'Otro mensaje' },
  ]

  it('renders preview and navigates between recipients', () => {
    render(<ComunicacionPreview previews={previews} onEnviar={() => {}} onClose={() => {}} />)
    expect(screen.getByText('Recordatorio')).toBeDefined()
    expect(screen.getByText(/Destinatario 1 de 2/)).toBeDefined()
    fireEvent.click(screen.getByText('Siguiente'))
    expect(screen.getByText(/Destinatario 2 de 2/)).toBeDefined()
    fireEvent.click(screen.getByText('Anterior'))
    expect(screen.getByText(/Destinatario 1 de 2/)).toBeDefined()
  })
})

describe('ComunicacionTracking', () => {
  it('shows final summary when all items done', () => {
    const data = {
      lote_id: '1',
      items: [
        { alumno_id: '1', alumno_nombre: 'Juan', estado: 'ok' as const },
        { alumno_id: '2', alumno_nombre: 'Maria', estado: 'fallido' as const },
      ],
    }
    render(<ComunicacionTracking data={data} />)
    expect(screen.getByText(/Comunicación finalizada/)).toBeDefined()
    expect(screen.getByText('Enviado')).toBeDefined()
    expect(screen.getByText('Fallido')).toBeDefined()
  })
})

describe('MonitoreoAlumnos', () => {
  const alumnos: MonitoreoAlumno[] = [
    { alumno: { id: '1', nombre: 'Juan Perez', email: 'juan@test.com' }, actividades_completadas: 3, total_actividades: 5, nota_promedio: 70 },
  ]

  it('renders monitoring table', () => {
    render(<MonitoreoAlumnos alumnos={alumnos} />)
    expect(screen.getByText('Juan Perez')).toBeDefined()
    expect(screen.getByText('60%')).toBeDefined()
  })
})
