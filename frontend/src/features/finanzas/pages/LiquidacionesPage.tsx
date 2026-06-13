import { useState } from 'react'
import { useLiquidaciones, useCalcularLiquidacion, useCerrarLiquidacion, useHistorialLiquidaciones, useExportarLiquidaciones } from '../hooks/useFinanzas'
import LiquidacionesTabla from '../components/LiquidacionesTabla'
import LiquidacionesHistorial from '../components/LiquidacionesHistorial'

type Tab = 'general' | 'nexo' | 'factura'

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
          <input id="liq-cohorte" type="text" value={cohorteId} onChange={(e) => setCohorteId(e.target.value)}
            className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
        </div>
        <div>
          <label htmlFor="liq-periodo" className="mb-1 block text-sm text-on-surface">Periodo</label>
          <input id="liq-periodo" type="text" value={periodo} onChange={(e) => setPeriodo(e.target.value)}
            placeholder="Ej: 2025-01" className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
        </div>
        <div className="flex gap-2">
          <button onClick={handleCalcular} disabled={calcular.isPending || !cohorteId || !periodo}
            className="rounded bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:bg-primary-hover disabled:opacity-50">
            {calcular.isPending ? 'Calculando...' : 'Calcular'}
          </button>
          <button onClick={handleExportar} disabled={exportar.isPending || !cohorteId || !periodo}
            className="rounded border border-border px-4 py-2 text-sm hover:bg-surface-hover disabled:opacity-50">
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
        <LiquidacionesTabla
          items={filtrados ?? []}
          isLoading={isLoading}
          onCerrar={(id) => cerrar.mutate(id)}
          isPending={cerrar.isPending}
        />
      )}

      <LiquidacionesHistorial
        data={historial.data}
        histCohorteId={histCohorteId}
        histPeriodo={histPeriodo}
        onCohorteChange={setHistCohorteId}
        onPeriodoChange={setHistPeriodo}
      />
    </div>
  )
}
