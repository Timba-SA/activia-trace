import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useResetPassword } from '../hooks/useAuth'

const resetSchema = z.object({
  password: z.string().min(8, 'La contraseña debe tener al menos 8 caracteres'),
  confirm: z.string(),
}).refine((data) => data.password === data.confirm, {
  message: 'Las contraseñas no coinciden',
  path: ['confirm'],
})

type ResetForm = z.infer<typeof resetSchema>

export default function ResetPasswordPage() {
  const reset = useResetPassword()
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ResetForm>({
    resolver: zodResolver(resetSchema),
  })

  const token = new URLSearchParams(window.location.search).get('token') ?? ''

  const onSubmit = (data: ResetForm) => {
    reset.mutate({ token, password: data.password })
  }

  return (
    <div className="flex min-h-[100dvh] items-center justify-center bg-surface">
      <div className="w-full max-w-sm rounded-lg bg-surface-container-lowest p-xl shadow-kpi">
        <h1 className="text-headline-md text-on-surface">Nueva contraseña</h1>
        <p className="mt-sm text-body-md text-on-surface-variant">
          Elegí una contraseña nueva para tu cuenta
        </p>
        <form onSubmit={handleSubmit(onSubmit)} className="mt-lg space-y-md">
          <div>
            <label htmlFor="password" className="text-label-sm text-on-surface">Nueva contraseña</label>
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
          <div>
            <label htmlFor="confirm" className="text-label-sm text-on-surface">Confirmar contraseña</label>
            <input
              id="confirm"
              type="password"
              {...register('confirm')}
              className="mt-xs block w-full rounded border border-outline px-sm py-2 text-body-md text-on-surface outline-none focus:border-primary"
              placeholder="••••••••"
            />
            {errors.confirm && (
              <p className="mt-xs text-label-sm text-error">{errors.confirm.message}</p>
            )}
          </div>
          {reset.error && (
            <div className="rounded border border-error/20 bg-error-container p-sm">
              <p className="text-label-sm text-on-error-container">
                Error al restablecer la contraseña
              </p>
            </div>
          )}
          <button
            type="submit"
            disabled={reset.isPending}
            className="w-full rounded bg-primary px-md py-2 text-body-md font-semibold text-on-primary transition-colors hover:bg-primary/90 disabled:opacity-50"
          >
            {reset.isPending ? 'Restableciendo...' : 'Restablecer contraseña'}
          </button>
        </form>
      </div>
    </div>
  )
}
