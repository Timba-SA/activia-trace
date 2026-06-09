import { Link } from 'react-router-dom'

export default function ForbiddenPage() {
  return (
    <div className="flex min-h-[100dvh] flex-col items-center justify-center bg-surface">
      <h1 className="text-display-lg text-on-surface">403</h1>
      <p className="mt-sm text-body-lg text-on-surface-variant">
        No tenés permiso para acceder a esta página
      </p>
      <Link
        to="/"
        className="mt-lg rounded bg-primary px-md py-2 text-body-md font-semibold text-on-primary transition-colors hover:bg-primary/90"
      >
        Volver al inicio
      </Link>
    </div>
  )
}
