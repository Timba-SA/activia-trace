## 1. Scaffolding y configuración

- [x] 1.1 Inicializar proyecto Vite + React 18 + TypeScript en `frontend/`
- [x] 1.2 Instalar dependencias: Tailwind CSS, React Router v6, TanStack Query, React Hook Form + Zod, Axios
- [x] 1.3 Configurar Tailwind con tokens del Design System (colores, tipografía, spacing, radius)
- [x] 1.4 Configurar `tsconfig.json` con path alias `@/` apuntando a `src/`
- [x] 1.5 Crear estructura de directorios: `features/{auth}/`, `shared/{services,components,hooks}`
- [x] 1.6 Configurar Axios instance en `shared/services/api.ts` con interceptores de auth y refresh
- [x] 1.7 Agregar tipado base: `types/auth.ts`, `types/api.ts`

## 2. Layout y navegación

- [x] 2.1 Crear layout principal: sidebar 280px + content area fluid
- [x] 2.2 Implementar sidebar con Institutional Navy (#002855), logo, y menú dinámico por permisos
- [x] 2.3 Implementar sidebar responsive: icon rail (768-1023px), drawer (<768px)
- [x] 2.4 Crear `<ProtectedRoute>` que verifica sesión y permiso opcional
- [x] 2.5 Configurar React Router con lazy loading de páginas
- [x] 2.6 Crear página 403 "Sin permiso" y ruta comodín 404

## 3. Auth — login y 2FA

- [x] 3.1 Crear hook `useAuth` que consulta sesión (TanStack Query) y expone login/logout/refresh
- [x] 3.2 Implementar pantalla de login con email + password, validación Zod, llamada a POST /api/auth/login
- [x] 3.3 Implementar pantalla de 2FA (TOTP 6 dígitos) si `requires_2fa: true`
- [x] 3.4 Implementar pantalla de forgot password con POST /api/auth/forgot
- [x] 3.5 Implementar pantalla de reset password con token desde URL + POST /api/auth/reset
- [x] 3.6 Implementar logout: llamada POST /api/auth/logout + limpiar tokens + redirigir a login
- [x] 3.7 Manejar rate-limiting (429) en login con mensaje al usuario

## 4. Tests

- [x] 4.1 Test: login render y submit con mock de API
- [x] 4.2 Test: ProtectedRoute redirige a login sin sesión
- [x] 4.3 Test: ProtectedRoute muestra 403 sin permiso
- [x] 4.4 Test: interceptor refresh transparente (401 → refresh → retry)
- [x] 4.5 Test: sidebar filtra items por permisos
