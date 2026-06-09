import { useState } from 'react'
import type { ActividadDetectada } from '../types'

interface Props {
  actividades: ActividadDetectada[]
  onConfirm: (seleccionadas: string[]) => void
  loading?: boolean
}

export function ImportPreview({ actividades, onConfirm, loading }: Props) {
  const [seleccionadas, setSeleccionadas] = useState<string[]>(actividades.filter((a) => a.incluida).map((a) => a.nombre))

  function toggle(nombre: string) {
    setSeleccionadas((prev) => prev.includes(nombre) ? prev.filter((n) => n !== nombre) : [...prev, nombre])
  }

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-on-surface">Actividades detectadas ({actividades.length})</h3>
      <div className="max-h-64 overflow-y-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border text-left text-xs uppercase text-on-surface-muted">
              <th className="w-10 px-2 py-2">Incluir</th>
              <th className="px-2 py-2">Actividad</th>
              <th className="px-2 py-2">Tipo</th>
            </tr>
          </thead>
          <tbody>
            {actividades.map((a) => (
              <tr key={a.nombre} className="border-b border-border">
                <td className="px-2 py-2">
                  <input type="checkbox" checked={seleccionadas.includes(a.nombre)} onChange={() => toggle(a.nombre)} className="size-4" />
                </td>
                <td className="px-2 py-2">{a.nombre}</td>
                <td className="px-2 py-2 text-on-surface-muted">{a.tipo_valor === 'numerico' ? 'Numérico' : 'Textual'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <button
        onClick={() => onConfirm(seleccionadas)}
        disabled={loading || seleccionadas.length === 0}
        className="rounded bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:bg-primary-hover disabled:cursor-not-allowed disabled:opacity-50"
      >
        {loading ? 'Confirmando...' : `Confirmar (${seleccionadas.length} actividades)`}
      </button>
    </div>
  )
}
