import { useState } from 'react'
import { useLiquidaciones, useCalcularLiquidacion, useCerrarLiquidacion, useHistorialLiquidaciones, useExportarLiquidaciones } from '../hooks/useFinanzas'
import type { LiquidacionResponse } from '../types'

type Tab = 'general' | 'nexo' | 'factura'

const estadoLabels: Record<string, string> = {
  Pendiente: 'Pendiente',
  Calculada: 'Calculada',
  Cerrada: 'Cerrada',
}

const estadoColors: Record<string, string> = {
  Pendiente: 'bg-warning/10 text-warning',
  Calculada: 'bg-primary/10 text-primary',
  Cerrada: 'bg-success/10 text-success',
}

export default function LiquidacionesPage() {
  const [tab, setTab] = useState<Tab>('general')
  const [cohorteId, setCohorteId] = useState('')
  const [periodo, setPeriodo] = useState('')
  const [histCohorteId, setHistCohorteId] = useState('')
  const [histPeriodo, setHistPeriodo] = useState('')

  const params = { cohorte_id: cohorteId || undefined, periodo: periodo || undefined }
  const { data, isLoading } = useLiquidaciones(params)
  const historial = useHistorialLiquidaciones({ cohorte_id: histCohorteId || undefined, periodo: histPeriodo || undefined })
  const calcular = useCalcularLiquidacion()
  const cerrar = useCerrarLiquidacion()
  const exportar = useExportarLiquidaciones()

  function handleCalcular() {
    if (!cohorteId || !periodo) return
    calcular.mutate({ cohorte_id: cohorteId, periodo })
  }

  function handleExportar() {
    if (!cohorteId || !periodo) return
    exportar.mutate({ cohorte_id: cohorteId, periodo })
  }

  const filtrados = data?.items.filter((l) => {
    if (tab === 'nexo') return l.es_nexo
    if (tab === 'factura') return l.excluido_por_factura
    return !l.es_nexo && !l.excluido_por_factura
  })

  function renderTable(items: LiquidacionResponse[]) {
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
                  <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${estadoColors[l.estado]}`}>
                    {estadoLabels[l.estado] || l.estado}
                  </span>
                </td>
                <td className="px-4 py-3">
                  {l.estado !== 'Cerrada' && (
                    <button
                      onClick={() => cerrar.mutate(l.id)}
                      disabled={cerrar.isPending}
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

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-primary">Liquidaciones</h2>
      </div>

      <nav className="flex gap-1 border-b border-border">
        {([
          { key: 'general' as const, label: 'General' },
          { key: 'nexo' as const, label: 'NEXO' },
          { key: 'factura' as const, label: 'Factura' },
        ]).map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`-mb-px border-b-2 px-4 py-2 text-sm transition-colors ${
              tab === t.key
                ? 'border-primary text-primary'
                : 'border-transparent text-on-surface-muted hover:text-on-surface'
            }`}
          >
            {t.label}
          </button>
        ))}
      </nav>

      <div className="flex flex-wrap items-end gap-4 rounded-lg border border-border bg-surface p-4">
        <div>
          <label htmlFor="liq-cohorte" className="mb-1 block text-sm text-on-surface">Cohorte ID</label>
          <input
            id="liq-cohorte"
            type="text"
            value={cohorteId}
            onChange={(e) => setCohorteId(e.target.value)}
            className="w-full rounded border border-border bg-surface px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label htmlFor="liq-periodo" className="mb-1 block text-sm text-on-surface">Periodo</label>
          <input
            id="liq-periodo"
            type="text"
            value={periodo}
            onChange={(e) => setPeriodo(e.target.value)}
            placeholder="Ej: 2025-01"
            className="w-full rounded border border-border bg-surface px-3 py-2 text-sm"
          />
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleCalcular}
            disabled={calcular.isPending || !cohorteId || !periodo}
            className="rounded bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:bg-primary-hover disabled:opacity-50"
          >
            {calcular.isPending ? 'Calculando...' : 'Calcular'}
          </button>
          <button
            onClick={handleExportar}
            disabled={exportar.isPending || !cohorteId || !periodo}
            className="rounded border border-border px-4 py-2 text-sm hover:bg-surface-hover disabled:opacity-50"
          >
            {exportar.isPending ? 'Exportando...' : 'Exportar CSV'}
          </button>
        </div>
      </div>

      {calcular.data && (
        <p className="text-sm text-success">Liquidaciones calculadas correctamente ({calcular.data.items.length} registros).</p>
      )}

      {isLoading ? (
        <div className="h-32 animate-pulse rounded bg-border" />
      ) : (
        renderTable(filtrados || [])
      )}

      <div className="space-y-4">
        <h3 className="text-sm font-semibold text-on-surface">Historial</h3>
        <div className="flex flex-wrap items-end gap-4">
          <div>
            <label htmlFor="liq-hist-cohorte" className="mb-1 block text-sm text-on-surface">Cohorte ID</label>
            <input
              id="liq-hist-cohorte"
              type="text"
              value={histCohorteId}
              onChange={(e) => setHistCohorteId(e.target.value)}
              className="w-full rounded border border-border bg-surface px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label htmlFor="liq-hist-periodo" className="mb-1 block text-sm text-on-surface">Periodo</label>
            <input
              id="liq-hist-periodo"
              type="text"
              value={histPeriodo}
              onChange={(e) => setHistPeriodo(e.target.value)}
              placeholder="Ej: 2025-01"
              className="w-full rounded border border-border bg-surface px-3 py-2 text-sm"
            />
          </div>
        </div>
        {historial.data ? (
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
                {historial.data.items.map((l) => (
                  <tr key={l.id} className="bg-surface hover:bg-surface-hover">
                    <td className="px-4 py-3 text-on-surface">{l.usuario_id.slice(0, 8)}...</td>
                    <td className="px-4 py-3 text-on-surface">{l.rol}</td>
                    <td className="px-4 py-3 text-on-surface">${l.total.toFixed(2)}</td>
                    <td className="px-4 py-3">
                      <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${estadoColors[l.estado]}`}>
                        {estadoLabels[l.estado] || l.estado}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-on-surface-muted">{new Date(l.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
                {historial.data.items.length === 0 && (
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
    </div>
  )
}
