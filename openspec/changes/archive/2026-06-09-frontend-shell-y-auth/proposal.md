## Why

Activia-trace tiene todo el backend completo (19 cambios, C-01 a C-20) pero cero frontend. Para que los usuarios (PROFESOR, COORDINADOR, ADMIN, etc.) puedan usar el sistema, necesitamos una SPA que consuma los endpoints existentes. Este cambio construye el cascarón del frontend y la capa de autenticación, sin la cual ninguna otra feature frontend puede funcionar.

## What Changes

- Scaffolding completo de React 18 + TypeScript + Vite con estructura feature-based
- Cliente HTTP centralizado con Axios: interceptor de auth, refresh transparente de JWT, manejo de 401/403
- Pantalla de login (email + password) consumiendo `POST /api/auth/login`
- Pantalla de 2FA (TOTP) para usuarios con doble factor habilitado
- Pantalla de recuperación de contraseña (forgot + reset)
- Logout con invalidación de sesión
- Guard de rutas por permiso (`modulo:accion`): sin sesión → login, sin permiso → 403
- Layout principal con sidebar de 280px y menú adaptado a permisos del usuario logueado
- Design System "Institutional Navy" aplicado: tokens de color, tipografía Inter + JetBrains Mono, spacing 4px

## Capabilities

### New Capabilities
- `frontend-shell`: Scaffolding Vite + React + Tailwind + estructura feature-based + layout principal con sidebar dinámico
- `frontend-auth`: Pantallas de login, 2FA, forgot/reset password, logout + guard de rutas + cliente HTTP con refresh transparente

### Modified Capabilities
<!-- No existing specs change. First frontend change. -->

## Impact

- New directory: `frontend/` con toda la SPA
- Dependencias npm: React 18, TanStack Query, React Hook Form, Zod, Axios, Tailwind, React Router
- Consume APIs existentes de C-03 (auth) y C-04 (RBAC para permisos del menú)
- El layout y menú dependen del endpoint de permisos del usuario logueado (perfil/permisos)
