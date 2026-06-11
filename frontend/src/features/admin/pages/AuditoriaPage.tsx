import { useState } from 'react'
import { useUltimasAcciones, useMetricasAccionesPorDia, useMetricasPorDocente, useMetricasPorMateria, useMetricasComunicaciones } from '../hooks/useAdmin'

type Tab = 'dashboard' | 'log'

export default function AuditoriaPage() {
  const [tab, setTab] = useState<Tab>('dashboard')
  const [filtros, setFiltros] = useState({ accion: '', actor_id: '', materia_id: '', desde: '', hasta: '' })

  const metricasDia = useMetricasAccionesPorDia()
  const metricasDocente = useMetricasPorDocente()
  const metricasMateria = useMetricasPorMateria()
  const metricasComms = useMetricasComunicaciones()

  const { data, isLoading } = useUltimasAcciones({
    accion: filtros.accion || undefined,
    actor_id: filtros.actor_id || undefined,
    materia_id: filtros.materia_id || undefined,
    desde: filtros.desde || undefined,
    hasta: filtros.hasta || undefined,
  })

  const totalAcciones = metricasDia.data?.items.reduce((s, i) => s + i.total, 0) ?? 0
  const totalDocentes = metricasDocente.data?.items.length ?? 0
  const totalMaterias = metricasMateria.data?.items.length ?? 0
  const totalComms = metricasComms.data?.items.reduce((s, i) => s + i.total_enviadas + i.total_recibidas, 0) ?? 0

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-primary">Auditoría</h2>
      </div>

      <nav className="flex gap-1 border-b border-border">
        {([
          { key: 'dashboard' as const, label: 'Dashboard' },
          { key: 'log' as const, label: 'Log' },
        ]).map((t) => (
          <button key={t.key} onClick={() => setTab(t.key)}
            className={`-mb-px border-b-2 px-4 py-2 text-sm transition-colors ${tab === t.key ? 'border-primary text-primary' : 'border-transparent text-on-surface-muted hover:text-on-surface'}`}>
            {t.label}
          </button>
        ))}
      </nav>

      {tab === 'dashboard' && (
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
      )}

      {tab === 'log' && (
        <div className="space-y-4">
          <div className="flex flex-wrap gap-3">
            <div>
              <label htmlFor="log-accion" className="text-label-sm block mb-1">Acción</label>
              <input id="log-accion" value={filtros.accion} onChange={(e) => setFiltros({ ...filtros, accion: e.target.value })}
                className="w-40 rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
            <div>
              <label htmlFor="log-actor" className="text-label-sm block mb-1">Actor ID</label>
              <input id="log-actor" value={filtros.actor_id} onChange={(e) => setFiltros({ ...filtros, actor_id: e.target.value })}
                className="w-40 rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
            <div>
              <label htmlFor="log-materia" className="text-label-sm block mb-1">Materia ID</label>
              <input id="log-materia" value={filtros.materia_id} onChange={(e) => setFiltros({ ...filtros, materia_id: e.target.value })}
                className="w-40 rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
            <div>
              <label htmlFor="log-desde" className="text-label-sm block mb-1">Desde</label>
              <input id="log-desde" type="date" value={filtros.desde} onChange={(e) => setFiltros({ ...filtros, desde: e.target.value })}
                className="rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
            <div>
              <label htmlFor="log-hasta" className="text-label-sm block mb-1">Hasta</label>
              <input id="log-hasta" type="date" value={filtros.hasta} onChange={(e) => setFiltros({ ...filtros, hasta: e.target.value })}
                className="rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
          </div>

          {isLoading ? (
            <div className="h-32 animate-pulse rounded bg-border" />
          ) : data ? (
            <div className="overflow-x-auto rounded-lg border border-border">
              <table className="w-full text-sm">
                <thead className="bg-surface-container text-left">
                  <tr>
                    <th className="px-4 py-2 font-medium text-on-surface-variant">Acción</th>
                    <th className="px-4 py-2 font-medium text-on-surface-variant">Actor ID</th>
                    <th className="px-4 py-2 font-medium text-on-surface-variant">Materia ID</th>
                    <th className="px-4 py-2 font-medium text-on-surface-variant">Detalles</th>
                    <th className="px-4 py-2 font-medium text-on-surface-variant">IP</th>
                    <th className="px-4 py-2 font-medium text-on-surface-variant">Fecha</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {data.items.map((a) => (
                    <tr key={a.id} className="hover:bg-surface-hover">
                      <td className="px-4 py-2 text-on-surface font-medium">{a.accion}</td>
                      <td className="px-4 py-2 font-mono text-xs text-on-surface-variant">{a.actor_id}</td>
                      <td className="px-4 py-2 font-mono text-xs text-on-surface-variant">{a.materia_id ?? '—'}</td>
                      <td className="px-4 py-2 text-on-surface-variant max-w-[200px] truncate" title={a.detalles ? JSON.stringify(a.detalles) : ''}>
                        {a.detalles ? JSON.stringify(a.detalles).slice(0, 60) : '—'}
                      </td>
                      <td className="px-4 py-2 font-mono text-xs text-on-surface-variant">{a.ip ?? '—'}</td>
                      <td className="px-4 py-2 text-on-surface-variant whitespace-nowrap">
                        {new Date(a.created_at).toLocaleString('es-AR')}
                      </td>
                    </tr>
                  ))}
                  {data.items.length === 0 && (
                    <tr><td colSpan={6} className="px-4 py-8 text-center text-sm text-on-surface-muted">Sin registros</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          ) : null}
        </div>
      )}
    </div>
  )
}
