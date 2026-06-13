import type { LiquidacionResponse } from '../types'

const estadoColors: Record<string, string> = {
  Pendiente: 'bg-warning/10 text-warning',
  Calculada: 'bg-primary/10 text-primary',
  Cerrada: 'bg-success/10 text-success',
}

const estadoLabels: Record<string, string> = {
  Pendiente: 'Pendiente',
  Calculada: 'Calculada',
  Cerrada: 'Cerrada',
}

interface Props {
  items: LiquidacionResponse[]
  isLoading: boolean
  onCerrar: (id: string) => void
  isPending: boolean
}

export default function LiquidacionesTabla({ items, isLoading, onCerrar, isPending }: Props) {
  return (
    <div className="overflow-x-auto rounded-lg border border-border">
      <table className="w-full text-sm">
        <thead>
          <tr className="bg-surface-hover text-left text-xs font-medium text-on-surface-muted uppercase">
            <th className="px-4 py-3">Usuario</th>
            <th className="px-4 py-3">Rol</th>
            <th className="px-4 py-3">Comisiones</th>
            <th className="px-4 py-3">Base</th>
            <th className="px-4 py-3">Plus</th>
            <th className="px-4 py-3">Total</th>
            <th className="px-4 py-3">Estado</th>
            <th className="px-4 py-3">Acción</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {items.map((l) => (
            <tr key={l.id} className="bg-surface hover:bg-surface-hover">
              <td className="px-4 py-3 text-on-surface">{l.usuario_id.slice(0, 8)}...</td>
              <td className="px-4 py-3 text-on-surface">{l.rol}</td>
              <td className="px-4 py-3 text-on-surface">{l.comisiones.join(', ') || '—'}</td>
              <td className="px-4 py-3 text-on-surface">${l.monto_base.toFixed(2)}</td>
              <td className="px-4 py-3 text-on-surface">${l.monto_plus.toFixed(2)}</td>
              <td className="px-4 py-3 font-medium text-on-surface">${l.total.toFixed(2)}</td>
              <td className="px-4 py-3">
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${estadoColors[l.estado] ?? ''}`}>
                  {estadoLabels[l.estado] ?? l.estado}
                </span>
              </td>
              <td className="px-4 py-3">
                {l.estado !== 'Cerrada' && (
                  <button
                    onClick={() => onCerrar(l.id)}
                    disabled={isPending}
                    className="rounded border border-danger px-2 py-1 text-xs font-medium text-danger hover:bg-danger/5 disabled:opacity-50"
                  >
                    Cerrar
                  </button>
                )}
              </td>
            </tr>
          ))}
          {items.length === 0 && (
            <tr>
              <td colSpan={8} className="px-4 py-8 text-center text-sm text-on-surface-muted">
                {isLoading ? 'Cargando...' : 'Sin liquidaciones.'}
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  )
}
