import { useState } from 'react'
import type { AsignacionMasivaRequest } from '../types'

interface Props {
  onAsignar: (data: AsignacionMasivaRequest) => void
  onClose: () => void
  loading?: boolean
}

export function AsignacionMasivaForm({ onAsignar, onClose, loading }: Props) {
  const [usuarioIds, setUsuarioIds] = useState('')
  const [materiaId, setMateriaId] = useState('')
  const [carreraId, setCarreraId] = useState('')
  const [cohorteId, setCohorteId] = useState('')
  const [rol, setRol] = useState('')
  const [fechaInicio, setFechaInicio] = useState('')
  const [fechaFin, setFechaFin] = useState('')
  const [comisiones, setComisiones] = useState('')

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    onAsignar({
      usuario_ids: usuarioIds.split(',').map((s) => s.trim()).filter(Boolean),
      materia_id: materiaId,
      carrera_id: carreraId,
      cohorte_id: cohorteId,
      rol,
      fecha_inicio: fechaInicio,
      fecha_fin: fechaFin,
      comisiones: comisiones ? comisiones.split(',').map((s) => s.trim()).filter(Boolean) : undefined,
    })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="mb-1 block text-sm text-on-surface">IDs de usuarios (separados por coma)</label>
        <input type="text" value={usuarioIds} onChange={(e) => setUsuarioIds(e.target.value)} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" placeholder="uuid-1, uuid-2, ..." />
      </div>
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
          <label className="mb-1 block text-sm text-on-surface">Cohorte ID</label>
          <input type="text" value={cohorteId} onChange={(e) => setCohorteId(e.target.value)} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
        </div>
        <div>
          <label className="mb-1 block text-sm text-on-surface">Rol</label>
          <select value={rol} onChange={(e) => setRol(e.target.value)} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm">
            <option value="">Seleccionar</option>
            <option value="PROFESOR">PROFESOR</option>
            <option value="TUTOR">TUTOR</option>
            <option value="JTP">JTP</option>
            <option value="AYUDANTE">AYUDANTE</option>
          </select>
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
      <div>
        <label className="mb-1 block text-sm text-on-surface">Comisiones (separadas por coma)</label>
        <input type="text" value={comisiones} onChange={(e) => setComisiones(e.target.value)} className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" placeholder="A, B, C" />
      </div>
      <div className="flex justify-end gap-3 pt-2">
        <button type="button" onClick={onClose} className="rounded border border-border px-4 py-2 text-sm hover:bg-surface-hover">Cancelar</button>
        <button type="submit" disabled={loading} className="rounded bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:bg-primary-hover disabled:opacity-50">
          {loading ? 'Asignando...' : 'Asignar'}
        </button>
      </div>
    </form>
  )
}
