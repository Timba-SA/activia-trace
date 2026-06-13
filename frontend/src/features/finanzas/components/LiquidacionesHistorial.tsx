import type { LiquidacionHistorialResponse } from '../types'

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
  data: LiquidacionHistorialResponse | undefined
  histCohorteId: string
  histPeriodo: string
  onCohorteChange: (v: string) => void
  onPeriodoChange: (v: string) => void
}

export default function LiquidacionesHistorial({ data, histCohorteId, histPeriodo, onCohorteChange, onPeriodoChange }: Props) {
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-on-surface">Historial</h3>
      <div className="flex flex-wrap items-end gap-4">
        <div>
          <label htmlFor="liq-hist-cohorte" className="mb-1 block text-sm text-on-surface">Cohorte ID</label>
          <input
            id="liq-hist-cohorte"
            type="text"
            value={histCohorteId}
            onChange={(e) => onCohorteChange(e.target.value)}
            className="w-full rounded border border-border bg-surface px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label htmlFor="liq-hist-periodo" className="mb-1 block text-sm text-on-surface">Periodo</label>
          <input
            id="liq-hist-periodo"
            type="text"
            value={histPeriodo}
            onChange={(e) => onPeriodoChange(e.target.value)}
            placeholder="Ej: 2025-01"
            className="w-full rounded border border-border bg-surface px-3 py-2 text-sm"
          />
        </div>
      </div>
      {data ? (
        <div className="overflow-x-auto rounded-lg border border-border">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-surface-hover text-left text-xs font-medium text-on-surface-muted uppercase">
                <th className="px-4 py-3">Usuario</th>
                <th className="px-4 py-3">Rol</th>
                <th className="px-4 py-3">Total</th>
                <th className="px-4 py-3">Estado</th>
                <th className="px-4 py-3">Fecha</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {data.items.map((l) => (
                <tr key={l.id} className="bg-surface hover:bg-surface-hover">
                  <td className="px-4 py-3 text-on-surface">{l.usuario_id.slice(0, 8)}...</td>
                  <td className="px-4 py-3 text-on-surface">{l.rol}</td>
                  <td className="px-4 py-3 text-on-surface">${l.total.toFixed(2)}</td>
                  <td className="px-4 py-3">
                    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${estadoColors[l.estado] ?? ''}`}>
                      {estadoLabels[l.estado] ?? l.estado}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-on-surface-muted">{new Date(l.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
              {data.items.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-sm text-on-surface-muted">Sin historial.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="text-sm text-on-surface-muted">Usá los filtros de cohorte y periodo para ver el historial.</p>
      )}
    </div>
  )
}
