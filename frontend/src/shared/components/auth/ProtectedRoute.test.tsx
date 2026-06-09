import { render, screen } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { describe, it, expect } from 'vitest'
import { ProtectedRoute } from './ProtectedRoute'

function TestPage() {
  return <div>Página protegida</div>
}

describe('ProtectedRoute', () => {
  it('redirects to /login when not authenticated', () => {
    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <Routes>
          <Route path="/login" element={<div>Login</div>} />
          <Route
            element={
              <ProtectedRoute isAuthenticated={false} permissions={[]} />
            }
          >
            <Route path="/dashboard" element={<TestPage />} />
          </Route>
        </Routes>
      </MemoryRouter>,
    )
    expect(screen.getByText('Login')).toBeInTheDocument()
  })

  it('renders children when authenticated', () => {
    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <Routes>
          <Route path="/login" element={<div>Login</div>} />
          <Route
            element={
              <ProtectedRoute isAuthenticated={true} permissions={[]} />
            }
          >
            <Route path="/dashboard" element={<TestPage />} />
          </Route>
        </Routes>
      </MemoryRouter>,
    )
    expect(screen.getByText('Página protegida')).toBeInTheDocument()
  })

  it('redirects to /403 when missing required permission', () => {
    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <Routes>
          <Route path="/403" element={<div>Sin permiso</div>} />
          <Route
            element={
              <ProtectedRoute
                isAuthenticated={true}
                permissions={[]}
                requiredPermission="admin:ver"
              />
            }
          >
            <Route path="/dashboard" element={<TestPage />} />
          </Route>
        </Routes>
      </MemoryRouter>,
    )
    expect(screen.getByText('Sin permiso')).toBeInTheDocument()
  })
})
