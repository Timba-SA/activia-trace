import { useState } from 'react'
import { useCarreras, useCohortes, useMaterias, useUsuarios } from '@/features/admin/hooks/useAdmin'
import type { AsignacionMasivaRequest } from '../types'

interface Props {
  onAsignar: (data: AsignacionMasivaRequest) => void
  onClose: () => void
  loading?: boolean
}

export function AsignacionMasivaForm({ onAsignar, onClose, loading }: Props) {
  const [carreraId, setCarreraId] = useState('')
  const [cohorteId, setCohorteId] = useState('')
  const [materiaId, setMateriaId] = useState('')
  const [usuarioIds, setUsuarioIds] = useState<string[]>([])
  const [rol, setRol] = useState('')
  const [fechaInicio, setFechaInicio] = useState('')
  const [fechaFin, setFechaFin] = useState('')
  const [comisiones, setComisiones] = useState('')

  const { data: carreras } = useCarreras({ limit: 100 })
  const { data: cohortes } = useCohortes({ carrera_id: carreraId || undefined, limit: 100 })
  const { data: materias } = useMaterias({ limit: 100 })
  const { data: usuarios } = useUsuarios({ limit: 100 })

  function toggleUsuario(id: string) {
    setUsuarioIds(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id])
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    onAsignar({
      usuario_ids: usuarioIds,
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
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="mb-1 block text-sm text-on-surface">Carrera</label>
          <select
            value={carreraId}
            onChange={(e) => { setCarreraId(e.target.value); setCohorteId('') }}
            required
            className="w-full rounded border border-border bg-surface px-3 py-2 text-sm"
          >
            <option value="">Seleccionar carrera</option>
            {carreras?.items.map(c => <option key={c.id} value={c.id}>{c.nombre} ({c.codigo})</option>)}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-sm text-on-surface">Cohorte</label>
          <select
            value={cohorteId}
            onChange={(e) => setCohorteId(e.target.value)}
            required
            disabled={!carreraId}
            className="w-full rounded border border-border bg-surface px-3 py-2 text-sm disabled:opacity-50"
          >
            <option value="">Seleccionar cohorte</option>
            {cohortes?.items.map(c => <option key={c.id} value={c.id}>{c.nombre} ({c.anio})</option>)}
          </select>
        </div>
      </div>

      <div>
        <label className="mb-1 block text-sm text-on-surface">Materia</label>
        <select
          value={materiaId}
          onChange={(e) => setMateriaId(e.target.value)}
          required
          className="w-full rounded border border-border bg-surface px-3 py-2 text-sm"
        >
          <option value="">Seleccionar materia</option>
          {materias?.items.map(m => <option key={m.id} value={m.id}>{m.nombre} ({m.codigo})</option>)}
        </select>
      </div>

      <div>
        <label className="mb-1 block text-sm text-on-surface">Docentes a asignar</label>
        <div className="max-h-32 overflow-y-auto rounded border border-border bg-surface p-2 space-y-1">
          {usuarios?.items.map(u => (
            <label key={u.id} className="flex items-center gap-2 cursor-pointer rounded px-1 py-0.5 hover:bg-surface-container-low">
              <input
                type="checkbox"
                checked={usuarioIds.includes(u.id)}
                onChange={() => toggleUsuario(u.id)}
                className="accent-primary"
              />
              <span className="text-sm text-on-surface">{u.nombre} {u.apellido} — <span className="text-on-surface-variant">{u.email}</span></span>
            </label>
          ))}
        </div>
        {usuarioIds.length === 0 && (
          <p className="mt-1 text-xs text-error">Seleccioná al menos un docente</p>
        )}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="mb-1 block text-sm text-on-surface">Rol</label>
          <select
            value={rol}
            onChange={(e) => setRol(e.target.value)}
            required
            className="w-full rounded border border-border bg-surface px-3 py-2 text-sm"
          >
            <option value="">Seleccionar</option>
            <option value="PROFESOR">PROFESOR</option>
            <option value="TUTOR">TUTOR</option>
            <option value="JTP">JTP</option>
            <option value="AYUDANTE">AYUDANTE</option>
          </select>
        </div>
        <div>
          <label className="mb-1 block text-sm text-on-surface">Comisiones (separadas por coma)</label>
          <input
            type="text"
            value={comisiones}
            onChange={(e) => setComisiones(e.target.value)}
            className="w-full rounded border border-border bg-surface px-3 py-2 text-sm"
            placeholder="A, B, C"
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="mb-1 block text-sm text-on-surface">Fecha inicio</label>
          <input
            type="date"
            value={fechaInicio}
            onChange={(e) => setFechaInicio(e.target.value)}
            required
            className="w-full rounded border border-border bg-surface px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm text-on-surface">Fecha fin</label>
          <input
            type="date"
            value={fechaFin}
            onChange={(e) => setFechaFin(e.target.value)}
            required
            className="w-full rounded border border-border bg-surface px-3 py-2 text-sm"
          />
        </div>
      </div>

      <div className="flex justify-end gap-3 pt-2">
        <button type="button" onClick={onClose} className="rounded border border-border px-4 py-2 text-sm hover:bg-surface-hover">
          Cancelar
        </button>
        <button
          type="submit"
          disabled={loading || usuarioIds.length === 0}
          className="rounded bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:bg-primary-hover disabled:opacity-50"
        >
          {loading ? 'Asignando...' : 'Asignar docentes'}
        </button>
      </div>
    </form>
  )
}
