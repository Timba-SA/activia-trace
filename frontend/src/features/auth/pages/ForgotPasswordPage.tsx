import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Link } from 'react-router-dom'
import { useForgotPassword } from '../hooks/useAuth'

const forgotSchema = z.object({
  email: z.string().email('Email inválido'),
})

type ForgotForm = z.infer<typeof forgotSchema>

export default function ForgotPasswordPage() {
  const forgot = useForgotPassword()
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ForgotForm>({
    resolver: zodResolver(forgotSchema),
  })

  const onSubmit = (data: ForgotForm) => {
    forgot.mutate(data)
  }

  if (forgot.isSuccess) {
    return (
      <div className="flex min-h-[100dvh] items-center justify-center bg-surface">
        <div className="w-full max-w-sm rounded-lg bg-surface-container-lowest p-xl shadow-kpi">
          <h1 className="text-headline-md text-on-surface">Revisá tu email</h1>
          <p className="mt-sm text-body-md text-on-surface-variant">
            Si el email existe, recibirás un enlace de recuperación
          </p>
          <div className="mt-lg text-center">
            <Link to="/login" className="text-label-sm text-primary hover:underline">
              Volver al inicio de sesión
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex min-h-[100dvh] items-center justify-center bg-surface">
      <div className="w-full max-w-sm rounded-lg bg-surface-container-lowest p-xl shadow-kpi">
        <h1 className="text-headline-md text-on-surface">Recuperar contraseña</h1>
        <p className="mt-sm text-body-md text-on-surface-variant">
          Te enviaremos un enlace para restablecer tu contraseña
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
          {forgot.error && (
            <div className="rounded border border-error/20 bg-error-container p-sm">
              <p className="text-label-sm text-on-error-container">
                Error al enviar el enlace de recuperación
              </p>
            </div>
          )}
          <button
            type="submit"
            disabled={forgot.isPending}
            className="w-full rounded bg-primary px-md py-2 text-body-md font-semibold text-on-primary transition-colors hover:bg-primary/90 disabled:opacity-50"
          >
            {forgot.isPending ? 'Enviando...' : 'Enviar enlace'}
          </button>
        </form>
        <div className="mt-md text-center">
          <Link to="/login" className="text-label-sm text-primary hover:underline">
            Volver al inicio de sesión
          </Link>
        </div>
      </div>
    </div>
  )
}
