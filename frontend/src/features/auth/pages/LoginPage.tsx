import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Link } from 'react-router-dom'
import { useLogin } from '../hooks/useAuth'

const loginSchema = z.object({
  email: z.string().email('Email inválido'),
  password: z.string().min(1, 'La contraseña es obligatoria'),
})

type LoginForm = z.infer<typeof loginSchema>

export default function LoginPage() {
  const login = useLogin()
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  })

  const onSubmit = (data: LoginForm) => {
    login.mutate(data)
  }

  return (
    <div className="flex min-h-[100dvh] items-center justify-center bg-surface">
      <div className="w-full max-w-sm rounded-lg bg-surface-container-lowest p-xl shadow-kpi">
        <h1 className="text-headline-md text-on-surface">Iniciar sesión</h1>
        <p className="mt-sm text-body-md text-on-surface-variant">
          Ingresá tu email y contraseña
        </p>
        <form onSubmit={handleSubmit(onSubmit)} className="mt-lg space-y-md">
          <div>
            <label htmlFor="email" className="text-label-sm text-on-surface">Email</label>
            <input
              id="email"
              type="email"
              {...register('email')}
              className="mt-xs block w-full rounded border border-outline px-sm py-2 text-body-md text-on-surface outline-none focus:border-primary"
              placeholder="email@ejemplo.com"
            />
            {errors.email && (
              <p className="mt-xs text-label-sm text-error">{errors.email.message}</p>
            )}
          </div>
          <div>
            <label htmlFor="password" className="text-label-sm text-on-surface">Contraseña</label>
            <input
              id="password"
              type="password"
              {...register('password')}
              className="mt-xs block w-full rounded border border-outline px-sm py-2 text-body-md text-on-surface outline-none focus:border-primary"
              placeholder="••••••••"
            />
            {errors.password && (
              <p className="mt-xs text-label-sm text-error">{errors.password.message}</p>
            )}
          </div>
          {login.error && (
            <div className="rounded border border-error/20 bg-error-container p-sm">
              <p className="text-label-sm text-on-error-container">
                {(login.error as { detail?: string })?.detail ?? 'Error al iniciar sesión'}
              </p>
            </div>
          )}
          <button
            type="submit"
            disabled={login.isPending}
            className="w-full rounded bg-primary px-md py-2 text-body-md font-semibold text-on-primary transition-colors hover:bg-primary/90 disabled:opacity-50"
          >
            {login.isPending ? 'Ingresando...' : 'Ingresar'}
          </button>
        </form>
        <div className="mt-md text-center">
          <Link to="/auth/forgot" className="text-label-sm text-primary hover:underline">
            ¿Olvidaste tu contraseña?
          </Link>
        </div>
      </div>
    </div>
  )
}
