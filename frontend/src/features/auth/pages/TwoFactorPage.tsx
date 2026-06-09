import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useVerify2fa } from '../hooks/useAuth'

const twoFactorSchema = z.object({
  code: z.string().length(6, 'El código debe tener 6 dígitos'),
})

type TwoFactorForm = z.infer<typeof twoFactorSchema>

export default function TwoFactorPage() {
  const verify2fa = useVerify2fa()
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<TwoFactorForm>({
    resolver: zodResolver(twoFactorSchema),
  })

  const onSubmit = (data: TwoFactorForm) => {
    const tempToken = new URLSearchParams(window.location.search).get('token') ?? ''
    verify2fa.mutate({ code: data.code, temp_token: tempToken })
  }

  return (
    <div className="flex min-h-[100dvh] items-center justify-center bg-surface">
      <div className="w-full max-w-sm rounded-lg bg-surface-container-lowest p-xl shadow-kpi">
        <h1 className="text-headline-md text-on-surface">Verificación en dos pasos</h1>
        <p className="mt-sm text-body-md text-on-surface-variant">
          Ingresá el código de 6 dígitos de tu aplicación de autenticación
        </p>
        <form onSubmit={handleSubmit(onSubmit)} className="mt-lg space-y-md">
          <div>
            <label htmlFor="code" className="text-label-sm text-on-surface">Código</label>
            <input
              id="code"
              type="text"
              maxLength={6}
              {...register('code')}
              className="mt-xs block w-full rounded border border-outline px-sm py-2 text-center text-headline-md text-on-surface outline-none focus:border-primary"
              placeholder="000000"
            />
            {errors.code && (
              <p className="mt-xs text-center text-label-sm text-error">{errors.code.message}</p>
            )}
          </div>
          {verify2fa.error && (
            <div className="rounded border border-error/20 bg-error-container p-sm">
              <p className="text-label-sm text-on-error-container">
                Código inválido
              </p>
            </div>
          )}
          <button
            type="submit"
            disabled={verify2fa.isPending}
            className="w-full rounded bg-primary px-md py-2 text-body-md font-semibold text-on-primary transition-colors hover:bg-primary/90 disabled:opacity-50"
          >
            {verify2fa.isPending ? 'Verificando...' : 'Verificar'}
          </button>
        </form>
      </div>
    </div>
  )
}
