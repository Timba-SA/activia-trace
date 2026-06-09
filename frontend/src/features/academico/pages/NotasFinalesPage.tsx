import { useNotasFinales } from '../hooks/useAcademico'
import { NotasFinalesTable } from '../components/NotasFinalesTable'

export default function NotasFinalesPage() {
  const { data: notas, isLoading } = useNotasFinales()

  return (
    <div className="space-y-6">
      <h2 className="text-lg font-semibold text-primary">Notas finales</h2>
      {isLoading ? (
        <div className="h-24 animate-pulse rounded bg-border" />
      ) : notas && notas.length > 0 ? (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
            <div className="rounded-lg bg-surface p-4 shadow-kpi">
              <p className="text-xs font-medium uppercase text-on-surface-muted">Total alumnos</p>
              <p className="mt-1 text-2xl font-bold text-primary">{notas.length}</p>
            </div>
            <div className="rounded-lg bg-surface p-4 shadow-kpi">
              <p className="text-xs font-medium uppercase text-on-surface-muted">Promedio general</p>
              <p className="mt-1 text-2xl font-bold text-secondary">
                {(notas.reduce((s, n) => s + n.nota_final, 0) / notas.length).toFixed(1)}
              </p>
            </div>
          </div>
          <NotasFinalesTable notas={notas} />
        </div>
      ) : (
        <p className="text-sm text-on-surface-muted">No hay notas finales calculadas para esta comisión.</p>
      )}
    </div>
  )
}
