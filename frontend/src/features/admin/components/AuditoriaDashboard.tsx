import type { UseQueryResult } from '@tanstack/react-query'
import type { MetricaPorDocente, MetricaPorMateria, MetricaAccionesPorDia } from '../types'

interface Props {
  metricasDia: UseQueryResult<{ items: MetricaAccionesPorDia[] }>
  metricasDocente: UseQueryResult<{ items: MetricaPorDocente[] }>
  metricasMateria: UseQueryResult<{ items: MetricaPorMateria[] }>
  totalAcciones: number
  totalDocentes: number
  totalMaterias: number
  totalComms: number
}

export default function AuditoriaDashboard({
  metricasDia,
  metricasDocente,
  metricasMateria,
  totalAcciones,
  totalDocentes,
  totalMaterias,
  totalComms,
}: Props) {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-4 gap-4">
        <div className="rounded-lg border border-border bg-surface-container-lowest p-4 shadow-kpi">
          <p className="text-label-sm text-on-surface-muted">Acciones totales</p>
          <p className="mt-1 text-headline-sm text-primary">{totalAcciones.toLocaleString()}</p>
        </div>
        <div className="rounded-lg border border-border bg-surface-container-lowest p-4 shadow-kpi">
          <p className="text-label-sm text-on-surface-muted">Docentes activos</p>
          <p className="mt-1 text-headline-sm text-primary">{totalDocentes}</p>
        </div>
        <div className="rounded-lg border border-border bg-surface-container-lowest p-4 shadow-kpi">
          <p className="text-label-sm text-on-surface-muted">Materias con actividad</p>
          <p className="mt-1 text-headline-sm text-primary">{totalMaterias}</p>
        </div>
        <div className="rounded-lg border border-border bg-surface-container-lowest p-4 shadow-kpi">
          <p className="text-label-sm text-on-surface-muted">Comunicaciones</p>
          <p className="mt-1 text-headline-sm text-primary">{totalComms.toLocaleString()}</p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="rounded-lg border border-border bg-surface-container-lowest p-4">
          <h3 className="text-sm font-semibold text-on-surface mb-3">Acciones por docente</h3>
          {metricasDocente.isLoading ? (
            <div className="h-24 animate-pulse rounded bg-border" />
          ) : metricasDocente.data ? (
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {metricasDocente.data.items.slice(0, 10).map((d) => (
                <div key={d.docente_id} className="flex items-center justify-between text-sm">
                  <span className="text-on-surface truncate">{d.nombre}</span>
                  <span className="font-mono text-xs text-on-surface-variant">{d.total_acciones}</span>
                </div>
              ))}
              {metricasDocente.data.items.length === 0 && (
                <p className="text-sm text-on-surface-muted">Sin datos</p>
              )}
            </div>
          ) : null}
        </div>

        <div className="rounded-lg border border-border bg-surface-container-lowest p-4">
          <h3 className="text-sm font-semibold text-on-surface mb-3">Acciones por materia</h3>
          {metricasMateria.isLoading ? (
            <div className="h-24 animate-pulse rounded bg-border" />
          ) : metricasMateria.data ? (
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {metricasMateria.data.items.slice(0, 10).map((m) => (
                <div key={m.materia_id} className="flex items-center justify-between text-sm">
                  <span className="text-on-surface truncate">{m.nombre}</span>
                  <span className="font-mono text-xs text-on-surface-variant">{m.total_acciones}</span>
                </div>
              ))}
              {metricasMateria.data.items.length === 0 && (
                <p className="text-sm text-on-surface-muted">Sin datos</p>
              )}
            </div>
          ) : null}
        </div>
      </div>

      <div className="rounded-lg border border-border bg-surface-container-lowest p-4">
        <h3 className="text-sm font-semibold text-on-surface mb-3">Acciones por día</h3>
        {metricasDia.isLoading ? (
          <div className="h-24 animate-pulse rounded bg-border" />
        ) : metricasDia.data ? (
          <div className="space-y-1 max-h-64 overflow-y-auto">
            {metricasDia.data.items.slice(0, 30).map((d) => (
              <div key={d.fecha} className="flex items-center gap-3 text-sm">
                <span className="w-24 text-on-surface-variant font-mono text-xs">{d.fecha}</span>
                <div className="flex-1 h-4 rounded bg-surface-container">
                  <div className="h-4 rounded bg-primary" style={{ width: `${Math.min(100, (d.total / (metricasDia.data!.items[0]?.total || 1)) * 100)}%` }} />
                </div>
                <span className="w-12 text-right font-mono text-xs text-on-surface-variant">{d.total}</span>
              </div>
            ))}
            {metricasDia.data.items.length === 0 && (
              <p className="text-sm text-on-surface-muted">Sin datos</p>
            )}
          </div>
        ) : null}
      </div>
    </div>
  )
}
