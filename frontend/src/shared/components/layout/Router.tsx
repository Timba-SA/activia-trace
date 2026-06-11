import { lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { useSession, useLogout } from '@/features/auth/hooks/useAuth'
import { Layout } from './Layout'
import { ProtectedRoute } from '../auth/ProtectedRoute'

const LoginPage = lazy(() => import('@/features/auth/pages/LoginPage'))
const TwoFactorPage = lazy(() => import('@/features/auth/pages/TwoFactorPage'))
const ForgotPasswordPage = lazy(() => import('@/features/auth/pages/ForgotPasswordPage'))
const ResetPasswordPage = lazy(() => import('@/features/auth/pages/ResetPasswordPage'))
const ForbiddenPage = lazy(() => import('@/features/auth/pages/ForbiddenPage'))
const NotFoundPage = lazy(() => import('@/features/auth/pages/NotFoundPage'))
const HomePage = lazy(() => import('@/features/auth/pages/HomePage'))
const PerfilPage = lazy(() => import('@/features/auth/pages/PerfilPage'))
const AcademicoLayout = lazy(() => import('@/features/academico/pages/AcademicoRootPage'))
const ComisionPage = lazy(() => import('@/features/academico/pages/ComisionPage'))
const CalificacionesPage = lazy(() => import('@/features/academico/pages/CalificacionesPage'))
const AtrasadosPage = lazy(() => import('@/features/academico/pages/AtrasadosPage'))
const NotasFinalesPage = lazy(() => import('@/features/academico/pages/NotasFinalesPage'))
const EntregasPage = lazy(() => import('@/features/academico/pages/EntregasPage'))
const ComunicacionPage = lazy(() => import('@/features/academico/pages/ComunicacionPage'))
const MonitoreoPage = lazy(() => import('@/features/academico/pages/MonitoreoPage'))
const EquiposPage = lazy(() => import('@/features/coordinacion/pages/EquiposPage'))
const AvisosPage = lazy(() => import('@/features/coordinacion/pages/AvisosPage'))
const TareasPage = lazy(() => import('@/features/coordinacion/pages/TareasPage'))
const EncuentrosPage = lazy(() => import('@/features/coordinacion/pages/EncuentrosPage'))
const GuardiasPage = lazy(() => import('@/features/coordinacion/pages/GuardiasPage'))
const ColoquiosPage = lazy(() => import('@/features/coordinacion/pages/ColoquiosPage'))
const ProgramasPage = lazy(() => import('@/features/coordinacion/pages/ProgramasPage'))
const LiquidacionesPage = lazy(() => import('@/features/finanzas/pages/LiquidacionesPage'))
const GrillaSalarialPage = lazy(() => import('@/features/finanzas/pages/GrillaSalarialPage'))
const FacturasPage = lazy(() => import('@/features/finanzas/pages/FacturasPage'))
const CarrerasPage = lazy(() => import('@/features/admin/pages/CarrerasPage'))
const CohortesPage = lazy(() => import('@/features/admin/pages/CohortesPage'))
const MateriasPage = lazy(() => import('@/features/admin/pages/MateriasPage'))
const UsuariosPage = lazy(() => import('@/features/admin/pages/UsuariosPage'))
const AuditoriaPage = lazy(() => import('@/features/admin/pages/AuditoriaPage'))

function PageLoader() {
  return (
    <div className="flex min-h-[200px] items-center justify-center">
      <div className="size-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />
    </div>
  )
}

function AppRoutes() {
  const { data: session, isLoading } = useSession()
  const logout = useLogout()

  if (isLoading) {
    return (
      <div className="flex min-h-[100dvh] items-center justify-center bg-surface">
        <div className="size-10 animate-spin rounded-full border-2 border-primary border-t-transparent" />
      </div>
    )
  }

  const isAuthenticated = !!session
  const permissions = session?.permissions ?? []
  const handleLogout = () => logout.mutate()

  return (
    <Routes>
      <Route path="/login" element={<Suspense fallback={<PageLoader />}><LoginPage /></Suspense>} />
      <Route path="/auth/2fa" element={<Suspense fallback={<PageLoader />}><TwoFactorPage /></Suspense>} />
      <Route path="/auth/forgot" element={<Suspense fallback={<PageLoader />}><ForgotPasswordPage /></Suspense>} />
      <Route path="/auth/reset" element={<Suspense fallback={<PageLoader />}><ResetPasswordPage /></Suspense>} />
      <Route path="/403" element={<Suspense fallback={<PageLoader />}><ForbiddenPage /></Suspense>} />
      <Route element={<ProtectedRoute isAuthenticated={isAuthenticated} permissions={permissions} />}>
        <Route element={<Layout permissions={permissions} onLogout={handleLogout} />}>
          <Route index element={<Suspense fallback={<PageLoader />}><HomePage /></Suspense>} />
          <Route path="perfil" element={<Suspense fallback={<PageLoader />}><PerfilPage /></Suspense>} />
          <Route path="academico/:materiaId?/:cohorteId?" element={<Suspense fallback={<PageLoader />}><AcademicoLayout /></Suspense>}>
            <Route index element={<Suspense fallback={<PageLoader />}><ComisionPage /></Suspense>} />
            <Route path="calificaciones" element={<Suspense fallback={<PageLoader />}><CalificacionesPage /></Suspense>} />
            <Route path="atrasados" element={<Suspense fallback={<PageLoader />}><AtrasadosPage /></Suspense>} />
            <Route path="notas-finales" element={<Suspense fallback={<PageLoader />}><NotasFinalesPage /></Suspense>} />
            <Route path="entregas" element={<Suspense fallback={<PageLoader />}><EntregasPage /></Suspense>} />
            <Route path="comunicaciones" element={<Suspense fallback={<PageLoader />}><ComunicacionPage /></Suspense>} />
            <Route path="monitoreo" element={<Suspense fallback={<PageLoader />}><MonitoreoPage /></Suspense>} />
          </Route>
          <Route path="equipos" element={<Suspense fallback={<PageLoader />}><EquiposPage /></Suspense>} />
          <Route path="avisos" element={<Suspense fallback={<PageLoader />}><AvisosPage /></Suspense>} />
          <Route path="tareas" element={<Suspense fallback={<PageLoader />}><TareasPage /></Suspense>} />
          <Route path="encuentros" element={<Suspense fallback={<PageLoader />}><EncuentrosPage /></Suspense>} />
          <Route path="guardias" element={<Suspense fallback={<PageLoader />}><GuardiasPage /></Suspense>} />
          <Route path="coloquios" element={<Suspense fallback={<PageLoader />}><ColoquiosPage /></Suspense>} />
          <Route path="programas" element={<Suspense fallback={<PageLoader />}><ProgramasPage /></Suspense>} />
          <Route path="liquidaciones" element={<Suspense fallback={<PageLoader />}><LiquidacionesPage /></Suspense>} />
          <Route path="grilla-salarial" element={<Suspense fallback={<PageLoader />}><GrillaSalarialPage /></Suspense>} />
          <Route path="facturas" element={<Suspense fallback={<PageLoader />}><FacturasPage /></Suspense>} />
          <Route path="admin/carreras" element={<Suspense fallback={<PageLoader />}><CarrerasPage /></Suspense>} />
          <Route path="admin/cohortes" element={<Suspense fallback={<PageLoader />}><CohortesPage /></Suspense>} />
          <Route path="admin/materias" element={<Suspense fallback={<PageLoader />}><MateriasPage /></Suspense>} />
          <Route path="admin/usuarios" element={<Suspense fallback={<PageLoader />}><UsuariosPage /></Suspense>} />
          <Route path="admin/auditoria" element={<Suspense fallback={<PageLoader />}><AuditoriaPage /></Suspense>} />
        </Route>
      </Route>
      <Route path="*" element={<Suspense fallback={<PageLoader />}><NotFoundPage /></Suspense>} />
    </Routes>
  )
}

export function AppRouter() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  )
}
