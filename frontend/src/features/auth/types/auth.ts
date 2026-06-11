export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  requires_2fa: boolean
  temp_token?: string
}

export interface TwoFactorRequest {
  code: string
  temp_token: string
}

export interface ForgotPasswordRequest {
  email: string
}

export interface ResetPasswordRequest {
  token: string
  password: string
}

export interface UserSession {
  id: string
  email: string
  nombre: string | null
  apellido: string | null
  roles: string[]
  permissions: string[]
  tenant_id: string
}
