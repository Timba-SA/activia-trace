import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useComision } from '../hooks/useAcademico'
import { useImportarCalificaciones, useConfirmarCalificaciones, useVaciarCalificaciones } from '../hooks/useAcademico'
import { ImportPreview } from '../components/ImportPreview'

export default function CalificacionesPage() {
  const navigate = useNavigate()
  const { materiaId, cohorteId } = useComision()
  const importar = useImportarCalificaciones()
  const confirmar = useConfirmarCalificaciones()
  const vaciar = useVaciarCalificaciones()

  const [previewActividades, setPreviewActividades] = useState<{ nombre: string; tipo_valor: 'numerico' | 'textual'; incluida: boolean }[] | null>(null)
  const [error, setError] = useState('')

  function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    setError('')
    importar.mutate(file, {
      onSuccess: (data) => setPreviewActividades(data.actividades),
      onError: () => setError('Error al procesar el archivo. Verificá el formato e intentá de nuevo.'),
    })
  }

  function handleConfirm(actividades: string[]) {
    confirmar.mutate(actividades, {
      onSuccess: () => navigate(`/academico/${materiaId}/${cohorteId}`),
      onError: () => setError('Error al confirmar las actividades.'),
    })
  }

  function handleVaciar() {
    if (window.confirm('¿Estás seguro de eliminar todos los datos de calificaciones de esta comisión?')) {
      vaciar.mutate(undefined, {
        onSuccess: () => navigate(`/academico/${materiaId}/${cohorteId}`),
      })
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-primary">Importar calificaciones</h2>
        <button onClick={handleVaciar} className="rounded border border-danger px-3 py-1.5 text-xs font-medium text-danger hover:bg-danger/5">
          Vaciar datos
        </button>
      </div>

      {!previewActividades && (
        <div className="rounded-lg border-2 border-dashed border-border p-8 text-center">
          <label className="cursor-pointer">
            <input type="file" accept=".csv,.xlsx,.xls" onChange={handleFile} className="hidden" />
            <div className="space-y-2">
              <p className="text-sm font-medium text-on-surface">Hacé clic para subir el archivo</p>
              <p className="text-xs text-on-surface-muted">Formatos aceptados: CSV, XLSX, XLS</p>
            </div>
          </label>
        </div>
      )}

      {importar.isPending && (
        <div className="flex items-center gap-2 text-sm text-on-surface-muted">
          <div className="size-4 animate-spin rounded-full border-2 border-primary border-t-transparent" />
          Procesando archivo...
        </div>
      )}

      {error && (
        <div className="rounded bg-danger/10 p-3 text-sm text-danger">{error}</div>
      )}

      {previewActividades && (
        <ImportPreview
          actividades={previewActividades}
          onConfirm={handleConfirm}
          loading={confirmar.isPending}
        />
      )}
    </div>
  )
}
