import { useState } from 'react'
import type { ComunicacionPreview as PreviewType } from '../types'

interface Props {
  previews: PreviewType[]
  onEnviar: (asunto: string, cuerpo: string) => void
  onClose: () => void
  loading?: boolean
}

export function ComunicacionPreview({ previews, onEnviar, onClose, loading }: Props) {
  const [idx, setIdx] = useState(0)
  const current = previews[idx]

  return (
    <div className="fixed inset-y-0 right-0 z-50 flex w-full max-w-md flex-col bg-surface shadow-xl">
      <div className="flex items-center justify-between border-b border-border p-4">
        <h3 className="text-sm font-semibold text-on-surface">Preview de comunicación</h3>
        <button onClick={onClose} className="text-on-surface-muted hover:text-on-surface">&times;</button>
      </div>
      <div className="flex-1 overflow-y-auto p-4">
        {previews.length > 1 && (
          <p className="mb-3 text-xs text-on-surface-muted">Destinatario {idx + 1} de {previews.length}</p>
        )}
        <div className="space-y-3">
          <div>
            <p className="text-xs font-medium uppercase text-on-surface-muted">Para:</p>
            <p className="text-sm font-medium">{current.alumno_id}</p>
          </div>
          <div>
            <p className="text-xs font-medium uppercase text-on-surface-muted">Asunto:</p>
            <p className="text-sm">{current.asunto}</p>
          </div>
          <div>
            <p className="text-xs font-medium uppercase text-on-surface-muted">Mensaje:</p>
            <p className="whitespace-pre-wrap text-sm">{current.cuerpo}</p>
          </div>
        </div>
      </div>
      <div className="border-t border-border p-4">
        {previews.length > 1 && (
          <div className="mb-3 flex justify-between">
            <button
              onClick={() => setIdx((i) => Math.max(0, i - 1))}
              disabled={idx === 0}
              className="text-xs text-primary hover:underline disabled:text-on-surface-muted disabled:no-underline"
            >
              Anterior
            </button>
            <button
              onClick={() => setIdx((i) => Math.min(previews.length - 1, i + 1))}
              disabled={idx === previews.length - 1}
              className="text-xs text-primary hover:underline disabled:text-on-surface-muted disabled:no-underline"
            >
              Siguiente
            </button>
          </div>
        )}
        <div className="flex gap-2">
          <button onClick={onClose} className="flex-1 rounded border border-border px-4 py-2 text-sm hover:bg-surface-hover">
            Cancelar
          </button>
          <button
            onClick={() => onEnviar(current.asunto, current.cuerpo)}
            disabled={loading}
            className="flex-1 rounded bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:bg-primary-hover disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? 'Enviando...' : 'Enviar'}
          </button>
        </div>
      </div>
    </div>
  )
}
