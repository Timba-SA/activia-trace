import type { DocenteEquipo } from '../types'

interface Props {
  items: DocenteEquipo[]
  onExportar?: () => void
  exporting?: boolean
}

export function EquiposList({ items, onExportar, exporting }: Props) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-on-surface-muted">{items.length} docentes</p>
        {onExportar && (
          <button
            onClick={onExportar}
            disabled={exporting}
            className="rounded border border-border px-3 py-1.5 text-xs font-medium hover:bg-surface-hover disabled:opacity-50"
          >
            {exporting ? 'Exportando...' : 'Exportar CSV'}
          </button>
        )}
      </div>
      <div className="overflow-x-auto rounded-lg border border-border">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-border bg-surface text-xs uppercase text-on-surface-muted">
              <th className="px-4 py-3">Nombre</th>
              <th className="px-4 py-3">Rol</th>
              <th className="px-4 py-3">Comisiones</th>
              <th className="px-4 py-3">Inicio</th>
              <th className="px-4 py-3">Fin</th>
              <th className="px-4 py-3">Estado</th>
            </tr>
          </thead>
          <tbody>
            {items.map((d) => (
              <tr key={d.id} className="border-b border-border last:border-b-0 hover:bg-surface-hover">
                <td className="px-4 py-3 font-medium text-on-surface">
                  {[d.apellido, d.nombre].filter(Boolean).join(', ') || '—'}
                </td>
                <td className="px-4 py-3 text-on-surface-muted">{d.rol}</td>
                <td className="px-4 py-3 text-on-surface-muted">{d.comisiones.join(', ') || '—'}</td>
                <td className="px-4 py-3 text-on-surface-muted">{d.fecha_inicio}</td>
                <td className="px-4 py-3 text-on-surface-muted">{d.fecha_fin || '—'}</td>
                <td className="px-4 py-3">
                  <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${d.is_active ? 'bg-success/10 text-success' : 'bg-on-surface-muted/10 text-on-surface-muted'}`}>
                    {d.is_active ? 'Activo' : 'Inactivo'}
                  </span>
                </td>
              </tr>
            ))}
            {items.length === 0 && (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-sm text-on-surface-muted">
                  Sin resultados
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
