import { lazy, Suspense, useMemo } from 'react'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
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

export function AppRouter() {
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

  const router = useMemo(() => createBrowserRouter([
    {
      path: '/login',
      element: (
        <Suspense fallback={<PageLoader />}>
          <LoginPage />
        </Suspense>
      ),
    },
    {
      path: '/auth/2fa',
      element: (
        <Suspense fallback={<PageLoader />}>
          <TwoFactorPage />
        </Suspense>
      ),
    },
    {
      path: '/auth/forgot',
      element: (
        <Suspense fallback={<PageLoader />}>
          <ForgotPasswordPage />
        </Suspense>
      ),
    },
    {
      path: '/auth/reset',
      element: (
        <Suspense fallback={<PageLoader />}>
          <ResetPasswordPage />
        </Suspense>
      ),
    },
    {
      path: '/403',
      element: (
        <Suspense fallback={<PageLoader />}>
          <ForbiddenPage />
        </Suspense>
      ),
    },
    {
      element: (
        <ProtectedRoute isAuthenticated={isAuthenticated} permissions={permissions} />
      ),
      children: [
        {
          element: <Layout permissions={permissions} onLogout={handleLogout} />,
          children: [
            {
              index: true,
              element: (
                <Suspense fallback={<PageLoader />}>
                  <HomePage />
                </Suspense>
              ),
            },
            {
              path: 'academico/:materiaId?/:cohorteId?',
              element: (
                <Suspense fallback={<PageLoader />}>
                  <AcademicoLayout />
                </Suspense>
              ),
              children: [
                {
                  index: true,
                  element: (
                    <Suspense fallback={<PageLoader />}>
                      <ComisionPage />
                    </Suspense>
                  ),
                },
                {
                  path: 'calificaciones',
                  element: (
                    <Suspense fallback={<PageLoader />}>
                      <CalificacionesPage />
                    </Suspense>
                  ),
                },
                {
                  path: 'atrasados',
                  element: (
                    <Suspense fallback={<PageLoader />}>
                      <AtrasadosPage />
                    </Suspense>
                  ),
                },
                {
                  path: 'notas-finales',
                  element: (
                    <Suspense fallback={<PageLoader />}>
                      <NotasFinalesPage />
                    </Suspense>
                  ),
                },
                {
                  path: 'entregas',
                  element: (
                    <Suspense fallback={<PageLoader />}>
                      <EntregasPage />
                    </Suspense>
                  ),
                },
                {
                  path: 'comunicaciones',
                  element: (
                    <Suspense fallback={<PageLoader />}>
                      <ComunicacionPage />
                    </Suspense>
                  ),
                },
                {
                  path: 'monitoreo',
                  element: (
                    <Suspense fallback={<PageLoader />}>
                      <MonitoreoPage />
                    </Suspense>
                  ),
                },
              ],
            },
            {
              path: 'equipos',
              element: (
                <Suspense fallback={<PageLoader />}>
                  <EquiposPage />
                </Suspense>
              ),
            },
            {
              path: 'avisos',
              element: (
                <Suspense fallback={<PageLoader />}>
                  <AvisosPage />
                </Suspense>
              ),
            },
            {
              path: 'tareas',
              element: (
                <Suspense fallback={<PageLoader />}>
                  <TareasPage />
                </Suspense>
              ),
            },
            {
              path: 'encuentros',
              element: (
                <Suspense fallback={<PageLoader />}>
                  <EncuentrosPage />
                </Suspense>
              ),
            },
            {
              path: 'guardias',
              element: (
                <Suspense fallback={<PageLoader />}>
                  <GuardiasPage />
                </Suspense>
              ),
            },
            {
              path: 'coloquios',
              element: (
                <Suspense fallback={<PageLoader />}>
                  <ColoquiosPage />
                </Suspense>
              ),
            },
            {
              path: 'programas',
              element: (
                <Suspense fallback={<PageLoader />}>
                  <ProgramasPage />
                </Suspense>
              ),
            },
            {
              path: 'liquidaciones',
              element: (
                <Suspense fallback={<PageLoader />}>
                  <LiquidacionesPage />
                </Suspense>
              ),
            },
            {
              path: 'grilla-salarial',
              element: (
                <Suspense fallback={<PageLoader />}>
                  <GrillaSalarialPage />
                </Suspense>
              ),
            },
            {
              path: 'facturas',
              element: (
                <Suspense fallback={<PageLoader />}>
                  <FacturasPage />
                </Suspense>
              ),
            },
            {
              path: 'admin/carreras',
              element: (
                <Suspense fallback={<PageLoader />}>
                  <CarrerasPage />
                </Suspense>
              ),
            },
            {
              path: 'admin/cohortes',
              element: (
                <Suspense fallback={<PageLoader />}>
                  <CohortesPage />
                </Suspense>
              ),
            },
            {
              path: 'admin/materias',
              element: (
                <Suspense fallback={<PageLoader />}>
                  <MateriasPage />
                </Suspense>
              ),
            },
            {
              path: 'admin/usuarios',
              element: (
                <Suspense fallback={<PageLoader />}>
                  <UsuariosPage />
                </Suspense>
              ),
            },
            {
              path: 'admin/auditoria',
              element: (
                <Suspense fallback={<PageLoader />}>
                  <AuditoriaPage />
                </Suspense>
              ),
            },
          ],
        },
      ],
    },
    {
      path: '*',
      element: (
        <Suspense fallback={<PageLoader />}>
          <NotFoundPage />
        </Suspense>
      ),
    },
  ]), [isAuthenticated, permissions, handleLogout])

  return <RouterProvider router={router} />
}
