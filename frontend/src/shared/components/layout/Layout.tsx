import { useState } from 'react'
import { Outlet, NavLink } from 'react-router-dom'

interface NavItem {
  label: string
  path: string
  permission: string | null
}

const sidebarNavItems: NavItem[] = [
  { label: 'Inicio', path: '/', permission: null },
  { label: 'Académico', path: '/academico', permission: 'calificaciones:ver' },
  { label: 'Equipos', path: '/equipos', permission: 'equipos:asignar' },
  { label: 'Encuentros', path: '/encuentros', permission: 'encuentros:gestionar' },
  { label: 'Guardias', path: '/guardias', permission: 'guardias:ver' },
  { label: 'Coloquios', path: '/coloquios', permission: 'coloquios:gestionar' },
  { label: 'Programas', path: '/programas', permission: 'programas:ver' },
  { label: 'Avisos', path: '/avisos', permission: 'avisos:publicar' },
  { label: 'Tareas', path: '/tareas', permission: 'tareas:gestionar' },
  { label: 'Finanzas', path: '/liquidaciones', permission: 'liquidaciones:ver' },
  { label: 'Admin', path: '/admin/carreras', permission: 'estructura:gestionar' },
  { label: 'Auditoría', path: '/admin/auditoria', permission: 'auditoria:ver' },
  { label: 'Perfil', path: '/perfil', permission: null },
]

const navIcons: Record<string, string> = {
  '/': 'H',
  '/academico': 'AC',
  '/equipos': 'E',
  '/encuentros': 'S',
  '/coloquios': 'O',
  '/avisos': 'N',
  '/tareas': 'T',
  '/liquidaciones': 'L',
  '/auditoria': 'R',
  '/perfil': 'P',
}

interface LayoutProps {
  permissions: string[]
  onLogout: () => void
}

export function Layout({ permissions, onLogout }: LayoutProps) {
  const [mobileOpen, setMobileOpen] = useState(false)
  const visibleItems = sidebarNavItems.filter(
    (item) => item.permission === null || permissions.includes(item.permission),
  )

  const sidebarContent = (compact: boolean) => (
    <>
      <div className="flex h-16 items-center justify-center gap-3 px-md lg:justify-start">
        <div className="size-8 shrink-0 rounded bg-primary-fixed" />
        {!compact && <span className="text-headline-sm text-on-primary">trace</span>}
      </div>
      <nav className="flex-1 overflow-y-auto px-xs">
        {visibleItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === '/'}
            onClick={() => setMobileOpen(false)}
            className={({ isActive }) =>
              `flex items-center justify-center gap-3 rounded px-sm py-2 text-body-md transition-colors lg:justify-start ${
                isActive
                  ? 'bg-white/10 text-on-primary'
                  : 'text-on-primary/80 hover:bg-white/10'
              }`
            }
          >
            <span className="flex size-6 shrink-0 items-center justify-center rounded bg-white/10 text-xs font-semibold text-on-primary">{navIcons[item.path]}</span>
            {!compact && <span>{item.label}</span>}
          </NavLink>
        ))}
      </nav>
      <div className="border-t border-white/10 p-md">
        <button
          type="button"
          onClick={onLogout}
          className="flex w-full items-center justify-center gap-3 rounded px-sm py-2 text-body-md text-on-primary/80 transition-colors hover:bg-white/10 lg:justify-start"
        >
          <span className="flex size-6 shrink-0 items-center justify-center rounded bg-white/10 text-xs font-semibold text-on-primary">X</span>
          {!compact && <span>Cerrar sesión</span>}
        </button>
      </div>
    </>
  )

  return (
    <div className="flex min-h-[100dvh]">
      {/* Desktop sidebar (full) */}
      <aside className="hidden w-sidebar shrink-0 flex-col bg-primary lg:flex">
        {sidebarContent(false)}
      </aside>

      {/* Tablet icon rail */}
      <aside className="hidden w-[72px] shrink-0 flex-col bg-primary md:flex lg:hidden">
        {sidebarContent(true)}
      </aside>

      {/* Mobile drawer overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 md:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Mobile drawer */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-sidebar flex-col bg-primary transition-transform md:hidden ${
          mobileOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {sidebarContent(false)}
      </aside>

      {/* Main content */}
      <main className="flex flex-1 flex-col bg-surface">
        {/* Mobile header */}
        <div className="flex h-14 items-center gap-3 border-b border-outline-variant px-md md:hidden">
          <button
            type="button"
            onClick={() => setMobileOpen(true)}
            className="rounded p-1 text-on-surface"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 6h18M3 12h18M3 18h18" />
            </svg>
          </button>
          <span className="text-headline-sm text-on-surface">trace</span>
        </div>
        <div className="flex-1 p-xl">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
