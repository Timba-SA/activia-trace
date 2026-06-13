import { useState } from 'react'
import { Outlet, NavLink, useNavigate } from 'react-router-dom'

interface NavItem {
  label: string
  path: string
  permission: string | null
  icon: string
}

const sidebarNavItems: NavItem[] = [
  { label: 'Dashboard Analítico', path: '/', permission: null, icon: 'dashboard' },
  { label: 'Académico', path: '/academico', permission: 'calificaciones:ver', icon: 'history_edu' },
  { label: 'Equipos', path: '/equipos', permission: 'equipos:asignar', icon: 'groups' },
  { label: 'Encuentros', path: '/encuentros', permission: 'encuentros:gestionar', icon: 'event' },
  { label: 'Guardias', path: '/guardias', permission: 'guardias:ver', icon: 'shield' },
  { label: 'Coloquios', path: '/coloquios', permission: 'coloquios:gestionar', icon: 'quiz' },
  { label: 'Programas', path: '/programas', permission: 'programas:ver', icon: 'account_tree' },
  { label: 'Avisos', path: '/avisos', permission: 'avisos:publicar', icon: 'campaign' },
  { label: 'Tareas', path: '/tareas', permission: 'tareas:gestionar', icon: 'assignment' },
  { label: 'Finanzas', path: '/liquidaciones', permission: 'liquidaciones:ver', icon: 'payments' },
  { label: 'Admin', path: '/admin/carreras', permission: 'estructura:gestionar', icon: 'tune' },
  { label: 'Auditoría', path: '/admin/auditoria', permission: 'auditoria:ver', icon: 'monitoring' },
  { label: 'Perfil', path: '/perfil', permission: null, icon: 'account_circle' },
]

interface LayoutProps {
  permissions: string[]
  onLogout: () => void
}

function Icon({ name, className = '' }: { name: string; className?: string }) {
  return <span className={`material-symbols-outlined ${className}`}>{name}</span>
}

export function Layout({ permissions, onLogout }: LayoutProps) {
  const navigate = useNavigate()
  const [mobileOpen, setMobileOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [notifOpen, setNotifOpen] = useState(false)
  const [sedeOpen, setSedeOpen] = useState(false)
  const visibleItems = sidebarNavItems.filter(
    (item) => item.permission === null || permissions.includes(item.permission),
  )

  const sidebarContent = (compact: boolean) => (
    <>
      <div className="flex flex-col gap-1 px-lg py-lg">
        <h1 className="text-headline-sm font-black text-on-primary">Active Trace</h1>
        {!compact && <p className="text-label-sm uppercase tracking-widest text-on-primary/70">Enterprise Audit</p>}
      </div>
      <nav className="flex-1 overflow-y-auto px-xs">
        {visibleItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === '/'}
            onClick={() => setMobileOpen(false)}
            className={({ isActive }) =>
              `flex items-center gap-md rounded px-md py-sm text-label-sm transition-colors border-l-4 ${
                isActive
                  ? 'border-primary-fixed-dim bg-white/10 text-on-primary'
                  : 'border-transparent text-on-primary/70 hover:bg-white/10'
              }`
            }
          >
            <Icon name={item.icon} />
            {!compact && <span>{item.label}</span>}
          </NavLink>
        ))}
      </nav>
      <div className="mt-auto border-t border-white/10 py-lg px-xs">
        <NavLink
          to="/perfil"
          onClick={() => setMobileOpen(false)}
          className={({ isActive }) =>
            `flex items-center gap-md rounded px-md py-sm text-label-sm transition-colors border-l-4 ${
              isActive
                ? 'border-primary-fixed-dim bg-white/10 text-on-primary'
                : 'border-transparent text-on-primary/70 hover:bg-white/10'
            }`
          }
        >
          <Icon name="help" />
          {!compact && <span>Soporte</span>}
        </NavLink>
        <button
          type="button"
          onClick={onLogout}
          className="flex w-full items-center gap-md rounded px-md py-sm text-label-sm text-on-primary/70 transition-colors hover:bg-white/10 border-l-4 border-transparent"
        >
          <Icon name="logout" />
          {!compact && <span>Cerrar Sesión</span>}
        </button>
      </div>
    </>
  )

  return (
    <div className="flex h-full overflow-hidden">
      {/* Desktop sidebar (full) */}
      <aside className="hidden w-sidebar shrink-0 flex-col bg-primary md:flex lg:flex" style={{ backgroundColor: '#001430' }}>
        {sidebarContent(false)}
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
        style={{ backgroundColor: '#001430' }}
      >
        {sidebarContent(false)}
      </aside>

      {/* Main content area */}
      <div className="flex flex-1 flex-col h-full overflow-hidden">
        {/* Top navbar */}
        <header className="flex items-center justify-between h-16 shrink-0 border-b border-outline-variant bg-surface px-lg">
          {/* Mobile menu toggle */}
          <button
            type="button"
            onClick={() => setMobileOpen(true)}
            className="mr-sm rounded-full p-sm text-on-surface-variant hover:bg-surface-container-high transition-colors md:hidden"
          >
            <Icon name="menu" />
          </button>

          {/* Search bar */}
          <div className="relative flex-1 max-w-md hidden sm:block">
            <Icon name="search" className="absolute left-sm top-1/2 -translate-y-1/2 text-on-surface-variant text-[20px]" />
            <input
              type="text"
              placeholder="Buscar alumnos, cohortes..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && searchQuery.trim()) {
                  navigate(`/?q=${encodeURIComponent(searchQuery.trim())}`)
                  setSearchQuery('')
                }
              }}
              className="w-full rounded-full border border-outline-variant bg-surface-container-low py-2 pl-xl pr-sm text-body-md text-on-surface outline-none transition-colors placeholder:text-on-surface-variant/70 focus:border-primary focus:ring-1 focus:ring-primary"
            />
          </div>

          <div className="flex items-center gap-md ml-auto">
            {/* Tenant selector */}
            <div
              className="relative hidden items-center gap-sm rounded-lg border border-outline-variant bg-surface-container-low px-sm py-xs text-primary transition-colors hover:bg-surface-container-high cursor-pointer lg:flex"
              onClick={() => { setSedeOpen(o => !o); setNotifOpen(false) }}
            >
              <Icon name="domain" className="text-[18px]" />
              <span className="text-label-sm font-bold text-primary">Sede Central / Facultad Regional</span>
              <Icon name="arrow_drop_down" className="text-[18px] text-on-surface-variant" />
              {sedeOpen && (
                <div className="absolute right-0 top-full mt-1 w-64 rounded-lg border border-outline-variant bg-surface shadow-lg z-50" onClick={e => e.stopPropagation()}>
                  {[
                    { label: 'Sede Central', sub: 'Facultad Regional Buenos Aires' },
                    { label: 'Sede Norte', sub: 'Facultad Regional Zona Norte' },
                  ].map((s, i) => (
                    <button key={i} type="button" onClick={() => setSedeOpen(false)} className="flex w-full flex-col px-md py-sm text-left transition-colors hover:bg-surface-container-low first:rounded-t-lg last:rounded-b-lg">
                      <span className="text-label-sm font-medium text-on-surface">{s.label}</span>
                      <span className="text-label-sm text-on-surface-variant">{s.sub}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Icons */}
            <div className="flex items-center gap-xs">
              <div className="relative">
                <button
                  type="button"
                  onClick={() => { setNotifOpen(o => !o); setSedeOpen(false) }}
                  className="relative rounded-full p-2 text-on-surface-variant transition-colors hover:bg-surface-container-high hover:text-on-surface cursor-pointer active:scale-95"
                >
                  <Icon name="notifications" />
                  <span className="absolute right-1.5 top-1.5 size-2 rounded-full bg-error" />
                </button>
                {notifOpen && (
                  <div className="absolute right-0 top-full mt-2 w-80 rounded-xl border border-outline-variant bg-surface shadow-lg z-50">
                    <div className="flex items-center justify-between border-b border-outline-variant px-md py-sm">
                      <p className="text-label-sm font-semibold text-on-surface">Notificaciones</p>
                      <span className="rounded-full bg-error px-2 py-0.5 text-label-sm text-white">3</span>
                    </div>
                    {([
                      { icon: 'warning', color: 'text-error', title: 'Alumno en riesgo de deserción', desc: 'Martina Rossi — sin actividad hace 14 días', time: 'Hace 2h' },
                      { icon: 'assignment_late', color: 'text-warning', title: 'TP 1 sin corregir', desc: '12 entregas pendientes en Programación I', time: 'Hace 5h' },
                      { icon: 'event_available', color: 'text-primary', title: 'Encuentro programado', desc: 'Funciones — mañana a las 18:00', time: 'Hace 1d' },
                    ] as const).map((n, i) => (
                      <div key={i} onClick={() => setNotifOpen(false)} className="flex items-start gap-sm border-b border-outline-variant px-md py-sm last:border-0 hover:bg-surface-container-low cursor-pointer">
                        <Icon name={n.icon} className={`mt-0.5 shrink-0 text-[18px] ${n.color}`} />
                        <div className="min-w-0 flex-1">
                          <p className="text-label-sm font-medium text-on-surface">{n.title}</p>
                          <p className="truncate text-label-sm text-on-surface-variant">{n.desc}</p>
                        </div>
                        <span className="shrink-0 text-label-sm text-on-surface-variant">{n.time}</span>
                      </div>
                    ))}
                    <div className="px-md py-sm text-center">
                      <button type="button" onClick={() => setNotifOpen(false)} className="text-label-sm text-primary hover:underline">Ver todas las notificaciones</button>
                    </div>
                  </div>
                )}
              </div>
              <button type="button" onClick={() => navigate('/')} className="hidden rounded-full p-2 text-on-surface-variant transition-colors hover:bg-surface-container-high hover:text-on-surface sm:block cursor-pointer active:scale-95">
                <Icon name="apps" />
              </button>
              <button type="button" onClick={() => navigate('/perfil')} className="rounded-full p-2 text-on-surface-variant transition-colors hover:bg-surface-container-high hover:text-on-surface cursor-pointer active:scale-95">
                <Icon name="account_circle" />
              </button>
            </div>
          </div>
        </header>

        {/* Scrollable page content */}
        <main className="flex-1 overflow-y-auto p-md md:p-lg">
          <div className="mx-auto max-w-7xl">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
