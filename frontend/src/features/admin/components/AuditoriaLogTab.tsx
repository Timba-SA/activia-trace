import type { AuditLogListResponse } from '../types'

interface Filtros {
  accion: string
  actor_id: string
  materia_id: string
  desde: string
  hasta: string
}

interface Props {
  data: AuditLogListResponse | undefined
  isLoading: boolean
  filtros: Filtros
  onFiltrosChange: (filtros: Filtros) => void
}

export default function AuditoriaLogTab({ data, isLoading, filtros, onFiltrosChange }: Props) {
  function set(key: keyof Filtros, value: string) {
    onFiltrosChange({ ...filtros, [key]: value })
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-3">
        <div>
          <label htmlFor="log-accion" className="text-label-sm block mb-1">Acción</label>
          <input id="log-accion" value={filtros.accion} onChange={(e) => set('accion', e.target.value)}
            className="w-40 rounded border border-border bg-surface px-3 py-2 text-sm" />
        </div>
        <div>
          <label htmlFor="log-actor" className="text-label-sm block mb-1">Actor ID</label>
          <input id="log-actor" value={filtros.actor_id} onChange={(e) => set('actor_id', e.target.value)}
            className="w-40 rounded border border-border bg-surface px-3 py-2 text-sm" />
        </div>
        <div>
          <label htmlFor="log-materia" className="text-label-sm block mb-1">Materia ID</label>
          <input id="log-materia" value={filtros.materia_id} onChange={(e) => set('materia_id', e.target.value)}
            className="w-40 rounded border border-border bg-surface px-3 py-2 text-sm" />
        </div>
        <div>
          <label htmlFor="log-desde" className="text-label-sm block mb-1">Desde</label>
          <input id="log-desde" type="date" value={filtros.desde} onChange={(e) => set('desde', e.target.value)}
            className="rounded border border-border bg-surface px-3 py-2 text-sm" />
        </div>
        <div>
          <label htmlFor="log-hasta" className="text-label-sm block mb-1">Hasta</label>
          <input id="log-hasta" type="date" value={filtros.hasta} onChange={(e) => set('hasta', e.target.value)}
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
  )
}
