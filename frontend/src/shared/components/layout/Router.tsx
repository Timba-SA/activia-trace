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
