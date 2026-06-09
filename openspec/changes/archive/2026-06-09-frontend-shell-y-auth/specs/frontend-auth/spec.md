## ADDED Requirements

### Requirement: Login page
The system SHALL render a login page at `/login` with email and password fields. On submit, it SHALL call `POST /api/auth/login` with `{ email, password }`. On success, it SHALL store the access token and redirect to the home page. On 401, it SHALL display an inline error message. On rate-limit (429), it SHALL display "Demasiados intentos. Intente de nuevo en 60 segundos."

#### Scenario: Successful login
- **WHEN** the user enters valid credentials and submits
- **THEN** the system calls POST /api/auth/login, stores the tokens, and redirects to `/`

#### Scenario: Invalid credentials
- **WHEN** the user enters invalid credentials
- **THEN** the system displays "Email o contraseña incorrectos" as an inline error

### Requirement: 2FA verification page
If the login response indicates 2FA is required (`requires_2fa: true`), the system SHALL redirect to a 2FA verification page at `/auth/2fa`. The user SHALL enter a 6-digit TOTP code. On verification, the system SHALL call the 2FA verification endpoint and complete the session.

#### Scenario: 2FA challenge after login
- **WHEN** the login response includes `requires_2fa: true`
- **THEN** the system redirects to `/auth/2fa` and waits for TOTP input

#### Scenario: Invalid TOTP code
- **WHEN** the user enters an invalid TOTP code
- **THEN** the system displays "Código inválido" and allows retry

### Requirement: Password recovery flow
The system SHALL provide a forgot password page at `/auth/forgot` (email input) and a reset password page at `/auth/reset` (token from URL + new password). The forgot page SHALL call `POST /api/auth/forgot` and display a success message ("Si el email existe, recibirás un enlace de recuperación"). The reset page SHALL call `POST /api/auth/reset` with token + new password.

#### Scenario: Forgot password submits email
- **WHEN** the user enters an email and submits the forgot password form
- **THEN** the system calls POST /api/auth/forgot and shows a generic success message

#### Scenario: Reset password with valid token
- **WHEN** the user navigates to /auth/reset?token=valid_token and submits a new password
- **THEN** the system calls POST /api/auth/reset and redirects to login with a success message

### Requirement: Centralized HTTP client with transparent refresh
The system SHALL provide a centralized Axios instance in `frontend/src/shared/services/api.ts`. It SHALL:
- Attach the access token to every request via an interceptor
- On 401 response, attempt to refresh the token via `POST /api/auth/refresh` **without** racing multiple simultaneous refreshes (promise queue pattern)
- On successful refresh, retry the original failed request with the new token
- On failed refresh, clear tokens and redirect to `/login`
- On 403, redirect to a "Sin permiso" page

#### Scenario: Transparent refresh on expired token
- **WHEN** a request returns 401 and the refresh endpoint succeeds
- **THEN** the original request is retried with the new token transparently

#### Scenario: Redirect to login on expired refresh
- **WHEN** a request returns 401 and the refresh endpoint also returns 401
- **THEN** tokens are cleared and the user is redirected to `/login`

#### Scenario: 403 triggers permission denied
- **WHEN** any API response returns 403
- **THEN** the system navigates to a `/403` page

### Requirement: Route guard by permission
The system SHALL define a `<ProtectedRoute>` component that checks authentication and optionally a required permission (`modulo:accion`). Without a valid session, it SHALL redirect to `/login`. Without the required permission, it SHALL render a 403 page.

#### Scenario: Unauthenticated user is redirected
- **WHEN** an unauthenticated user navigates to `/calificaciones`
- **THEN** the system redirects to `/login`

#### Scenario: Authenticated user without permission sees 403
- **WHEN** a user without `calificaciones:ver` navigates to `/calificaciones`
- **THEN** the system renders a 403 page

#### Scenario: Logout
- **WHEN** the user clicks "Cerrar sesión"
- **THEN** the system calls POST /api/auth/logout, clears tokens, and redirects to `/login`
