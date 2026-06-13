import { useState } from 'react'
import type { VigenciaUpdateRequest } from '../types'
import { useCarreras, useMaterias, useCohortes } from '@/features/admin/hooks/useAdmin'

interface Props {
  onUpdate: (data: VigenciaUpdateRequest) => void
  onClose: () => void
  loading?: boolean
}

export function VigenciaForm({ onUpdate, onClose, loading }: Props) {
  const [materiaId, setMateriaId] = useState('')
  const [carreraId, setCarreraId] = useState('')
  const [cohorteId, setCohorteId] = useState('')
  const [fechaInicio, setFechaInicio] = useState('')
  const [fechaFin, setFechaFin] = useState('')

  const { data: carreras } = useCarreras({ limit: 100 })
  const { data: materias } = useMaterias({ limit: 100 })
  const { data: cohortes } = useCohortes({ carrera_id: carreraId || undefined, limit: 100 })

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    onUpdate({
      materia_id: materiaId,
      carrera_id: carreraId,
      cohorte_id: cohorteId,
      fecha_inicio: fechaInicio,
      fecha_fin: fechaFin,
    })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-3 gap-4">
        <div>
          <label className="mb-1 block text-sm text-on-surface">Carrera</label>
          <select value={carreraId} onChange={(e) => { setCarreraId(e.target.value); setCohorteId('') }} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm">
            <option value="">Seleccionar carrera</option>
            {carreras?.items.map(c => <option key={c.id} value={c.id}>{c.nombre} ({c.codigo})</option>)}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-sm text-on-surface">Materia</label>
          <select value={materiaId} onChange={(e) => setMateriaId(e.target.value)} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm">
            <option value="">Seleccionar materia</option>
            {materias?.items.map(m => <option key={m.id} value={m.id}>{m.nombre} ({m.codigo})</option>)}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-sm text-on-surface">Cohorte</label>
          <select value={cohorteId} onChange={(e) => setCohorteId(e.target.value)} required disabled={!carreraId} className="w-full rounded border border-border bg-surface px-3 py-2 text-sm disabled:opacity-50">
            <option value="">Seleccionar cohorte</option>
            {cohortes?.items.map(c => <option key={c.id} value={c.id}>{c.nombre} ({c.anio})</option>)}
          </select>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="mb-1 block text-sm text-on-surface">Nueva fecha inicio</label>
          <input type="date" value={fechaInicio} onChange={(e) => setFechaInicio(e.target.value)} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
        </div>
        <div>
          <label className="mb-1 block text-sm text-on-surface">Nueva fecha fin</label>
          <input type="date" value={fechaFin} onChange={(e) => setFechaFin(e.target.value)} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
        </div>
      </div>
      <div className="flex justify-end gap-3 pt-2">
        <button type="button" onClick={onClose} className="rounded border border-outline-variant px-4 py-2 text-sm text-on-surface hover:bg-surface-container-high transition-colors">Cancelar</button>
        <button type="submit" disabled={loading} className="rounded bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:opacity-90 disabled:opacity-50 transition-colors">
          {loading ? 'Actualizando...' : 'Actualizar vigencia'}
        </button>
      </div>
    </form>
  )
}
