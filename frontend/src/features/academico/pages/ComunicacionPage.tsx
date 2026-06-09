import { useState } from 'react'
import { useAtrasados, usePreviewComunicacion, useEnviarComunicacion, useComunicacionTracking } from '../hooks/useAcademico'
import { AtrasadosTable } from '../components/AtrasadosTable'
import { ComunicacionPreview } from '../components/ComunicacionPreview'
import { ComunicacionTracking } from '../components/ComunicacionTracking'

export default function ComunicacionPage() {
  const { data: atrasados } = useAtrasados()
  const preview = usePreviewComunicacion()
  const enviar = useEnviarComunicacion()
  const [loteId, setLoteId] = useState<string | null>(null)
  const tracking = useComunicacionTracking(loteId)
  const [showPreview, setShowPreview] = useState(false)

  if (loteId && tracking.data) {
    return (
      <div className="space-y-6">
        <h2 className="text-lg font-semibold text-primary">Tracking de comunicación</h2>
        <ComunicacionTracking data={tracking.data} />
      </div>
    )
  }

  function handlePreview() {
    if (!atrasados || atrasados.length === 0) return
    preview.mutate(atrasados.map((a) => a.alumno.id), {
      onSuccess: () => setShowPreview(true),
    })
  }

  function handleEnviar(asunto: string, cuerpo: string) {
    if (!atrasados) return
    enviar.mutate(
      { alumnoIds: atrasados.map((a) => a.alumno.id), asunto, cuerpo },
      { onSuccess: (data) => setLoteId(data.lote_id) },
    )
  }

  return (
    <div className="space-y-6">
      <h2 className="text-lg font-semibold text-primary">Comunicaciones</h2>

      {atrasados && atrasados.length > 0 ? (
        <div className="space-y-4">
          <p className="text-sm text-on-surface-muted">
            {atrasados.length} alumnos atrasados. Podés enviarles un recordatorio.
          </p>
          <AtrasadosTable alumnos={atrasados} />
          <button
            onClick={handlePreview}
            disabled={preview.isPending}
            className="rounded bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:bg-primary-hover disabled:cursor-not-allowed disabled:opacity-50"
          >
            {preview.isPending ? 'Generando preview...' : 'Previsualizar mensaje'}
          </button>
        </div>
      ) : (
        <p className="text-sm text-on-surface-muted">No hay alumnos atrasados para comunicar.</p>
      )}

      {showPreview && preview.data && (
        <ComunicacionPreview
          previews={preview.data}
          onEnviar={handleEnviar}
          onClose={() => setShowPreview(false)}
          loading={enviar.isPending}
        />
      )}
    </div>
  )
}
