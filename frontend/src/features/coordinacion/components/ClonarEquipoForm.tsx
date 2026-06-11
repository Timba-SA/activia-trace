import { useState } from 'react'
import type { CloneRequest } from '../types'

interface Props {
  onClonar: (data: CloneRequest) => void
  onClose: () => void
  loading?: boolean
}

export function ClonarEquipoForm({ onClonar, onClose, loading }: Props) {
  const [materiaId, setMateriaId] = useState('')
  const [carreraId, setCarreraId] = useState('')
  const [cohorteOrigen, setCohorteOrigen] = useState('')
  const [cohorteDestino, setCohorteDestino] = useState('')
  const [fechaInicio, setFechaInicio] = useState('')
  const [fechaFin, setFechaFin] = useState('')

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    onClonar({
      materia_id: materiaId,
      carrera_id: carreraId,
      cohorte_origen_id: cohorteOrigen,
      cohorte_destino_id: cohorteDestino,
      fecha_inicio: fechaInicio,
      fecha_fin: fechaFin,
    })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="mb-1 block text-sm text-on-surface">Materia ID</label>
          <input type="text" value={materiaId} onChange={(e) => setMateriaId(e.target.value)} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
        </div>
        <div>
          <label className="mb-1 block text-sm text-on-surface">Carrera ID</label>
          <input type="text" value={carreraId} onChange={(e) => setCarreraId(e.target.value)} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="mb-1 block text-sm text-on-surface">Cohorte origen ID</label>
          <input type="text" value={cohorteOrigen} onChange={(e) => setCohorteOrigen(e.target.value)} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
        </div>
        <div>
          <label className="mb-1 block text-sm text-on-surface">Cohorte destino ID</label>
          <input type="text" value={cohorteDestino} onChange={(e) => setCohorteDestino(e.target.value)} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="mb-1 block text-sm text-on-surface">Fecha inicio</label>
          <input type="date" value={fechaInicio} onChange={(e) => setFechaInicio(e.target.value)} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
        </div>
        <div>
          <label className="mb-1 block text-sm text-on-surface">Fecha fin</label>
          <input type="date" value={fechaFin} onChange={(e) => setFechaFin(e.target.value)} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
        </div>
      </div>
      <div className="flex justify-end gap-3 pt-2">
        <button type="button" onClick={onClose} className="rounded border border-border px-4 py-2 text-sm hover:bg-surface-hover">Cancelar</button>
        <button type="submit" disabled={loading} className="rounded bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:bg-primary-hover disabled:opacity-50">
          {loading ? 'Clonando...' : 'Clonar equipo'}
        </button>
      </div>
    </form>
  )
}
