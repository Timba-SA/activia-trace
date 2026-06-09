import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import api from '@/shared/services/api'
import type { LoginRequest, LoginResponse, TwoFactorRequest, ForgotPasswordRequest, ResetPasswordRequest, UserSession } from '../types/auth'

async function fetchSession(): Promise<UserSession> {
  const { data } = await api.get<UserSession>('/auth/me')
  return data
}

async function loginFn(body: LoginRequest): Promise<LoginResponse> {
  const { data } = await api.post<LoginResponse>('/auth/login', body)
  return data
}

async function verify2faFn(body: TwoFactorRequest): Promise<LoginResponse> {
  const { data } = await api.post<LoginResponse>('/auth/2fa/verify', body)
  return data
}

async function forgotPasswordFn(body: ForgotPasswordRequest): Promise<void> {
  await api.post('/auth/forgot', body)
}

async function resetPasswordFn(body: ResetPasswordRequest): Promise<void> {
  await api.post('/auth/reset', body)
}

async function logoutFn(): Promise<void> {
  await api.post('/auth/logout')
}

export function useSession() {
  return useQuery({
    queryKey: ['session'],
    queryFn: fetchSession,
    retry: false,
    staleTime: 60_000,
  })
}

export function useLogin() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  return useMutation({
    mutationFn: loginFn,
    onSuccess: (data) => {
      if (data.requires_2fa) {
        navigate(`/auth/2fa?token=${data.temp_token}`)
        return
      }
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      queryClient.invalidateQueries({ queryKey: ['session'] })
      navigate('/')
    },
  })
}

export function useVerify2fa() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  return useMutation({
    mutationFn: verify2faFn,
    onSuccess: (data) => {
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      queryClient.invalidateQueries({ queryKey: ['session'] })
      navigate('/')
    },
  })
}

export function useForgotPassword() {
  return useMutation({
    mutationFn: forgotPasswordFn,
  })
}

export function useResetPassword() {
  const navigate = useNavigate()

  return useMutation({
    mutationFn: resetPasswordFn,
    onSuccess: () => {
      navigate('/login')
    },
  })
}

export function useLogout() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  return useMutation({
    mutationFn: logoutFn,
    onSettled: () => {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      queryClient.clear()
      navigate('/login')
    },
  })
}
