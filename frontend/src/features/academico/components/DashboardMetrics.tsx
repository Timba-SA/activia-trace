export function DashboardMetrics({ total, atrasados, actividades }: { total: number; atrasados: number; actividades: number }) {
  const atrasadosPct = total > 0 ? Math.round((atrasados / total) * 100) : 0

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
      <div className="rounded-lg bg-surface p-4 shadow-kpi">
        <p className="text-xs font-medium uppercase tracking-wide text-on-surface-muted">Total alumnos</p>
        <p className="mt-1 text-2xl font-bold text-primary">{total}</p>
      </div>
      <div className="rounded-lg bg-surface p-4 shadow-kpi">
        <p className="text-xs font-medium uppercase tracking-wide text-on-surface-muted">Atrasados</p>
        <p className="mt-1 text-2xl font-bold text-danger">{atrasados} <span className="text-sm font-normal text-on-surface-muted">({atrasadosPct}%)</span></p>
      </div>
      <div className="rounded-lg bg-surface p-4 shadow-kpi">
        <p className="text-xs font-medium uppercase tracking-wide text-on-surface-muted">Actividades</p>
        <p className="mt-1 text-2xl font-bold text-secondary">{actividades}</p>
      </div>
    </div>
  )
}
