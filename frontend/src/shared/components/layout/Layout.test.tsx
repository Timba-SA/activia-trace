import { render, screen } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { describe, it, expect } from 'vitest'
import { Layout } from './Layout'

describe('Layout', () => {
  it('shows items when user has matching permissions', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <Routes>
          <Route element={<Layout permissions={['calificaciones:ver', 'atrasados:ver']} onLogout={() => {}} />}>
            <Route path="/" element={<div>Home</div>} />
          </Route>
        </Routes>
      </MemoryRouter>,
    )
    expect(screen.getAllByText('Dashboard Analítico').length).toBeGreaterThanOrEqual(1)
    expect(screen.getAllByText('Académico').length).toBeGreaterThanOrEqual(1)
    expect(screen.queryByText('Auditoría')).not.toBeInTheDocument()
  })

  it('hides permission-gated items when user lacks permissions', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <Routes>
          <Route element={<Layout permissions={[]} onLogout={() => {}} />}>
            <Route path="/" element={<div>Home</div>} />
          </Route>
        </Routes>
      </MemoryRouter>,
    )
    expect(screen.getAllByText('Dashboard Analítico').length).toBeGreaterThanOrEqual(1)
    expect(screen.queryByText('Académico')).toBeNull()
    expect(screen.queryByText('Equipos')).toBeNull()
  })
})
