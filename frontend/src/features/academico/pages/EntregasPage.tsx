import { useState } from 'react'
import { useEntregasSinCorregir, useSubirReporteFinalizacion } from '../hooks/useAcademico'
import { EntregasSinCorregir } from '../components/EntregasSinCorregir'

export default function EntregasPage() {
  const { data: entregas, isLoading } = useEntregasSinCorregir()
  const subirReporte = useSubirReporteFinalizacion()
  const [error, setError] = useState('')

  function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    setError('')
    subirReporte.mutate(file, { onError: () => setError('Error al procesar el reporte.') })
  }

  return (
    <div className="space-y-6">
      <h2 className="text-lg font-semibold text-primary">Entregas sin corregir</h2>

      <label className="inline-flex cursor-pointer items-center gap-2 rounded border border-border px-4 py-2 text-sm hover:bg-surface-hover">
        <input type="file" accept=".csv,.xlsx,.xls" onChange={handleFile} className="hidden" />
        Subir reporte de finalización
      </label>

      {subirReporte.isPending && (
        <div className="flex items-center gap-2 text-sm text-on-surface-muted">
          <div className="size-4 animate-spin rounded-full border-2 border-primary border-t-transparent" />
          Procesando reporte...
        </div>
      )}

      {error && <div className="rounded bg-danger/10 p-3 text-sm text-danger">{error}</div>}

      {isLoading ? (
        <div className="h-24 animate-pulse rounded bg-border" />
      ) : entregas && entregas.length > 0 ? (
        <EntregasSinCorregir entregas={entregas} />
      ) : (
        <p className="text-sm text-on-surface-muted">No hay entregas sin corregir. Subí un reporte de finalización para detectarlas.</p>
      )}
    </div>
  )
}
