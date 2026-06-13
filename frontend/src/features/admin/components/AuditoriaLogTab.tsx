import type { AuditLogListResponse } from '../types'
import { useUsuarios, useMaterias } from '../hooks/useAdmin'

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
  const { data: usuarios } = useUsuarios({ limit: 100 })
  const { data: materias } = useMaterias({ limit: 100 })

  function set(key: keyof Filtros, value: string) {
    onFiltrosChange({ ...filtros, [key]: value })
  }

  function nombreUsuario(id: string) {
    const u = usuarios?.items.find(u => u.id === id)
    return u ? `${u.nombre} ${u.apellido}` : id.slice(0, 8) + '…'
  }

  function nombreMateria(id: string | null) {
    if (!id) return '—'
    const m = materias?.items.find(m => m.id === id)
    return m ? m.nombre : id.slice(0, 8) + '…'
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-3">
        <div>
          <label htmlFor="log-accion" className="text-label-sm block mb-1">Acción</label>
          <input id="log-accion" value={filtros.accion} onChange={(e) => set('accion', e.target.value)}
            placeholder="ej: login" className="w-40 rounded border border-border bg-surface px-3 py-2 text-sm" />
        </div>
        <div>
          <label htmlFor="log-actor" className="text-label-sm block mb-1">Actor</label>
          <select id="log-actor" value={filtros.actor_id} onChange={(e) => set('actor_id', e.target.value)}
            className="w-48 rounded border border-border bg-surface px-3 py-2 text-sm">
            <option value="">Todos los usuarios</option>
            {usuarios?.items.map(u => (
              <option key={u.id} value={u.id}>{u.nombre} {u.apellido}</option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="log-materia" className="text-label-sm block mb-1">Materia</label>
          <select id="log-materia" value={filtros.materia_id} onChange={(e) => set('materia_id', e.target.value)}
            className="w-48 rounded border border-border bg-surface px-3 py-2 text-sm">
            <option value="">Todas las materias</option>
            {materias?.items.map(m => (
              <option key={m.id} value={m.id}>{m.nombre}</option>
            ))}
          </select>
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
                <th className="px-4 py-2 font-medium text-on-surface-variant">Actor</th>
                <th className="px-4 py-2 font-medium text-on-surface-variant">Materia</th>
                <th className="px-4 py-2 font-medium text-on-surface-variant">Detalles</th>
                <th className="px-4 py-2 font-medium text-on-surface-variant">IP</th>
                <th className="px-4 py-2 font-medium text-on-surface-variant">Fecha</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {data.items.map((a) => (
                <tr key={a.id} className="hover:bg-surface-hover">
                  <td className="px-4 py-2 text-on-surface font-medium">{a.accion}</td>
                  <td className="px-4 py-2 text-on-surface-variant">{nombreUsuario(a.actor_id)}</td>
                  <td className="px-4 py-2 text-on-surface-variant">{nombreMateria(a.materia_id)}</td>
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
                <tr><td colSpan={6} className="px-4 py-8 text-center text-sm text-on-surface-muted">Sin registros de auditoría</td></tr>
              )}
            </tbody>
          </table>
        </div>
      ) : null}
    </div>
  )
}
