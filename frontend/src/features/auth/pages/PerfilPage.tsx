import { useSession } from '@/features/auth/hooks/useAuth'

function Icon({ name, className = '' }: { name: string; className?: string }) {
  return <span className={`material-symbols-outlined ${className}`}>{name}</span>
}

export default function PerfilPage() {
  const { data: session } = useSession()
  const displayName = [session?.nombre, session?.apellido].filter(Boolean).join(' ') || session?.email || '—'

  return (
    <div className="mx-auto max-w-2xl space-y-lg">
      {/* Page Header */}
      <div>
        <h2 className="text-display-lg text-on-background">Mi Perfil</h2>
        <p className="mt-1 text-body-md text-on-surface-variant">
          Información de tu cuenta y acceso al sistema.
        </p>
      </div>

      {/* User Avatar + Name Card */}
      <div className="flex items-center gap-lg rounded-xl border border-outline-variant bg-surface-container-lowest p-lg shadow-kpi">
        <div className="flex size-16 items-center justify-center rounded-full bg-primary-container text-headline-lg font-semibold text-on-primary-container">
          {(session?.nombre?.[0] ?? session?.email?.[0] ?? '?').toUpperCase()}
        </div>
        <div>
          <h3 className="text-headline-sm text-on-background">{displayName}</h3>
          <p className="text-body-md text-on-surface-variant">{session?.email}</p>
        </div>
      </div>

      {/* Details Grid */}
      <div className="grid gap-lg sm:grid-cols-2">
        <div className="space-y-sm rounded-xl border border-outline-variant bg-surface-container-lowest p-lg shadow-kpi">
          <div className="flex items-center gap-sm text-on-surface-variant">
            <Icon name="badge" className="text-lg" />
            <span className="text-label-sm">Nombre</span>
          </div>
          <p className="text-body-md text-on-background">{session?.nombre ?? '—'}</p>
        </div>

        <div className="space-y-sm rounded-xl border border-outline-variant bg-surface-container-lowest p-lg shadow-kpi">
          <div className="flex items-center gap-sm text-on-surface-variant">
            <Icon name="badge" className="text-lg" />
            <span className="text-label-sm">Apellido</span>
          </div>
          <p className="text-body-md text-on-background">{session?.apellido ?? '—'}</p>
        </div>

        <div className="space-y-sm rounded-xl border border-outline-variant bg-surface-container-lowest p-lg shadow-kpi">
          <div className="flex items-center gap-sm text-on-surface-variant">
            <Icon name="mail" className="text-lg" />
            <span className="text-label-sm">Email</span>
          </div>
          <p className="text-body-md text-on-background">{session?.email}</p>
        </div>

        <div className="space-y-sm rounded-xl border border-outline-variant bg-surface-container-lowest p-lg shadow-kpi">
          <div className="flex items-center gap-sm text-on-surface-variant">
            <Icon name="shield" className="text-lg" />
            <span className="text-label-sm">Roles</span>
          </div>
          <p className="text-body-md text-on-background">
            {session?.roles?.length ? session.roles.join(', ') : '—'}
          </p>
        </div>
      </div>
    </div>
  )
}
