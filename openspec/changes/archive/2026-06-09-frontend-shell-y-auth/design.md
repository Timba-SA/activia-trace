## Context

Activia-trace tiene 19 cambios backend completados (C-01 a C-20) con una API REST completa: auth, RBAC, estructura académica, usuarios, calificaciones, comunicaciones, etc. No existe frontend alguno.

El frontend será una SPA React 18 + TypeScript + Vite, organizada por features de dominio, que consume la API existente. Este change construye el esqueleto: scaffold, cliente HTTP, auth UI, guard de rutas y layout principal.

## Goals / Non-Goals

**Goals:**
- Scaffolding Vite + React 18 + TS + Tailwind con estructura feature-based
- Cliente HTTP Axios centralizado con interceptor JWT y refresh transparente
- Pantallas de login, 2FA, forgot/reset password y logout
- Guard de rutas que verifique sesión y permisos (`modulo:accion`)
- Layout con sidebar de 280px (Institutional Navy) + menú dinámico según permisos
- Design System aplicado: tokens de color, tipografía, spacing 4px

**Non-Goals:**
- No incluye páginas de dominio (calificaciones, atrasados, comunicaciones, etc.) — serán C-22/23/24
- No incluye gestión de perfil ni mensajería interna — eso es C-20 (backend ya listo)
- No incluye tests E2E con Playwright — solo unitarios de componentes

## Decisions

1. **React Router v6** para ruteo. Por ser el estándar de facto, con soporte de loaders/actions y nested routes que facilitan el guard por layout. Alternativa descartada: TanStack Router (muy early en su momento, la KB no lo menciona).

2. **Axios + interceptores** para el cliente HTTP. El refresh transparente se implementa con un interceptor de respuesta: si detecta 401, intenta refresh con un **cola de promesas** (para no disparar N refreshes simultáneos ante N requests fallidas). Si el refresh falla, redirige a login.

3. **State de sesión en memoria + TanStack Query**. La sesión (usuario actual, permisos) se resuelve con un hook que cachea la respuesta de `/api/auth/me` vía TanStack Query. No hay estado global (Redux/Zustand) — TanStack Query es suficiente.

4. **Guard de rutas como layout wrapper**. En lugar de un HOC por ruta, se define un `<ProtectedRoute>` que verifica: (a) sesión activa → renderiza `<Outlet />` o redirige a login; (b) permiso específico via prop `requiredPermission` → 403 si no lo tiene. Esto permite anidar rutas protegidas sin repetir el guard.

5. **Sidebar dinámico por permisos**. El menú se construye a partir de un Map estático ruta → permiso requerido. Se filtran las entradas que el usuario no tiene permiso para ver. Esto evita hardcodear menús por rol y mantiene la lógica en un solo lugar.

## Risks / Trade-offs

- [Riesgo] **Refresh token expirado mientras el usuario está en una página larga** → el interceptor detecta 401, intenta refresh, si falla redirige a login. El usuario pierde datos no guardados. Mitigación: TanStack Query retiene el cache, al volver a autenticarse los datos siguen ahí.
- [Trade-off] **Sidebar dinámico vs fijo**. Un menú fijo es más simple pero se desyncroniza si cambian los permisos del usuario en medio de la sesión. Elegimos dinámico (se recalcula en cada `navigate`) porque los permisos rara vez cambian en sesión activa, y si lo hacen, un refresh de página lo resuelve.
- [Riesgo] **Tailwind config no alineada con el Design System**. Mitigación: la config de `docs/DESIGN_SYSTEM.md` §8 se copia textual a `tailwind.config.ts`.
