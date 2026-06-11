import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { AvisosList } from './AvisosList'
import type { AvisoResponse } from '../types'

const aviso: AvisoResponse = {
  id: '1', tenant_id: 't1', alcance: 'Global', severidad: 'Critico',
  titulo: 'Error crítico', cuerpo: 'Revisar servidores',
  inicio_en: '2026-06-01T00:00:00Z', fin_en: '2026-06-30T00:00:00Z',
  orden: 0, activo: true, requiere_ack: true,
  materia_id: null, cohorte_id: null, rol_destino: null,
  created_at: '2026-06-01T00:00:00Z', updated_at: '2026-06-01T00:00:00Z',
}

describe('AvisosList', () => {
  it('renders avisos', () => {
    render(<AvisosList items={[aviso]} />)
    expect(screen.getByText('Error crítico')).toBeDefined()
    expect(screen.getByText('Critico')).toBeDefined()
    expect(screen.getByText('General')).toBeDefined()
    expect(screen.getByText('Activo')).toBeDefined()
  })

  it('shows empty state', () => {
    render(<AvisosList items={[]} />)
    expect(screen.getByText('Sin avisos')).toBeDefined()
  })

  it('calls onEdit and onDelete', () => {
    const onEdit = vi.fn()
    const onDelete = vi.fn()
    render(<AvisosList items={[aviso]} onEdit={onEdit} onDelete={onDelete} />)
    fireEvent.click(screen.getByText('Editar'))
    expect(onEdit).toHaveBeenCalledWith(aviso)
    fireEvent.click(screen.getByText('Eliminar'))
    expect(onDelete).toHaveBeenCalledWith('1')
  })
})
