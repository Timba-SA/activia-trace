import { Navigate, Outlet, useLocation } from 'react-router-dom'

interface ProtectedRouteProps {
  requiredPermission?: string
  permissions: string[]
  isAuthenticated: boolean
}

export function ProtectedRoute({
  requiredPermission,
  permissions,
  isAuthenticated,
}: ProtectedRouteProps) {
  const location = useLocation()

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  if (requiredPermission && !permissions.includes(requiredPermission)) {
    return <Navigate to="/403" replace />
  }

  return <Outlet />
}
