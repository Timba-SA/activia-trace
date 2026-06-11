import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { EquiposList } from './EquiposList'
import { AsignacionMasivaForm } from './AsignacionMasivaForm'
import { ClonarEquipoForm } from './ClonarEquipoForm'
import { VigenciaForm } from './VigenciaForm'
import type { DocenteEquipo } from '../types'

function setDateInputs(container: HTMLElement, value: string) {
  container.querySelectorAll<HTMLInputElement>('input[type="date"]').forEach((el) => {
    el.value = value
  })
}

describe('EquiposList', () => {
  const items: DocenteEquipo[] = [
    { id: '1', usuario_id: 'u1', nombre: 'Juan', apellido: 'Perez', rol: 'PROFESOR', carrera_id: 'c1', materia_id: 'm1', cohorte_id: 'coh1', responsable_id: null, fecha_inicio: '2026-01-01', fecha_fin: '2026-12-31', comisiones: ['A', 'B'], is_active: true },
    { id: '2', usuario_id: 'u2', nombre: 'Maria', apellido: 'Gomez', rol: 'TUTOR', carrera_id: 'c1', materia_id: 'm1', cohorte_id: 'coh1', responsable_id: 'u1', fecha_inicio: '2026-01-01', fecha_fin: null, comisiones: ['C'], is_active: false },
  ]

  it('renders team members', () => {
    render(<EquiposList items={items} />)
    expect(screen.getByText('Perez, Juan')).toBeDefined()
    expect(screen.getByText('Gomez, Maria')).toBeDefined()
    expect(screen.getByText('PROFESOR')).toBeDefined()
    expect(screen.getByText('TUTOR')).toBeDefined()
    expect(screen.getByText('A, B')).toBeDefined()
    expect(screen.getByText('C')).toBeDefined()
    expect(screen.getByText('Activo')).toBeDefined()
    expect(screen.getByText('Inactivo')).toBeDefined()
  })

  it('shows empty state', () => {
    render(<EquiposList items={[]} />)
    expect(screen.getByText('Sin resultados')).toBeDefined()
  })

  it('calls onExportar when export clicked', () => {
    const onExportar = vi.fn()
    render(<EquiposList items={items} onExportar={onExportar} />)
    fireEvent.click(screen.getByText('Exportar CSV'))
    expect(onExportar).toHaveBeenCalledOnce()
  })
})

describe('AsignacionMasivaForm', () => {
  it('calls onAsignar with form data', () => {
    const onAsignar = vi.fn()
    const { container } = render(<AsignacionMasivaForm onAsignar={onAsignar} onClose={() => {}} />)
    fireEvent.change(screen.getByPlaceholderText(/uuid-1/), { target: { value: 'u1, u2' } })
    const textboxes = screen.getAllByRole('textbox').filter((el) => (el as HTMLInputElement).type !== 'date')
    fireEvent.change(textboxes[1], { target: { value: 'm1' } })
    fireEvent.change(textboxes[2], { target: { value: 'c1' } })
    fireEvent.change(textboxes[3], { target: { value: 'coh1' } })
    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'PROFESOR' } })
    setDateInputs(container, '2026-01-01')
    fireEvent.click(screen.getByText('Asignar'))
    expect(onAsignar).toHaveBeenCalled()
  })

  it('calls onClose when cancel clicked', () => {
    const onClose = vi.fn()
    render(<AsignacionMasivaForm onAsignar={() => {}} onClose={onClose} />)
    fireEvent.click(screen.getByText('Cancelar'))
    expect(onClose).toHaveBeenCalledOnce()
  })
})

describe('ClonarEquipoForm', () => {
  it('calls onClonar with form data', () => {
    const onClonar = vi.fn()
    const { container } = render(<ClonarEquipoForm onClonar={onClonar} onClose={() => {}} />)
    const textboxes = screen.getAllByRole('textbox').filter((el) => (el as HTMLInputElement).type !== 'date')
    fireEvent.change(textboxes[0], { target: { value: 'm1' } })
    fireEvent.change(textboxes[1], { target: { value: 'c1' } })
    fireEvent.change(textboxes[2], { target: { value: 'coh-origen' } })
    fireEvent.change(textboxes[3], { target: { value: 'coh-destino' } })
    setDateInputs(container, '2026-01-01')
    fireEvent.click(screen.getByText('Clonar equipo'))
    expect(onClonar).toHaveBeenCalled()
  })
})

describe('VigenciaForm', () => {
  it('calls onUpdate with form data', () => {
    const onUpdate = vi.fn()
    const { container } = render(<VigenciaForm onUpdate={onUpdate} onClose={() => {}} />)
    const textboxes = screen.getAllByRole('textbox').filter((el) => (el as HTMLInputElement).type !== 'date')
    fireEvent.change(textboxes[0], { target: { value: 'm1' } })
    fireEvent.change(textboxes[1], { target: { value: 'c1' } })
    fireEvent.change(textboxes[2], { target: { value: 'coh1' } })
    setDateInputs(container, '2026-02-01')
    fireEvent.click(screen.getByText('Actualizar vigencia'))
    expect(onUpdate).toHaveBeenCalled()
  })
})
