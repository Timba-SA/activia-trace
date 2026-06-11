import { useState } from 'react'
import { useGuardias, useMisGuardias, useCrearGuardia, useActualizarEstadoGuardia } from '../hooks/useCoordinacion'
import type { DiaSemanaGuardia, EstadoGuardia } from '../types'

const diaLabels: Record<DiaSemanaGuardia, string> = { Lunes: 'Lunes', Martes: 'Martes', Miercoles: 'Miércoles', Jueves: 'Jueves', Viernes: 'Viernes', Sabado: 'Sábado', Domingo: 'Domingo' }
const estadoLabels: Record<EstadoGuardia, string> = { Pendiente: 'Pendiente', Realizada: 'Realizada', Cancelada: 'Cancelada' }

export default function GuardiasPage() {
  const [view, setView] = useState<'admin' | 'mis-guardias'>('admin')
  const { data: guardias } = useGuardias()
  const { data: misGuardias } = useMisGuardias()
  const crear = useCrearGuardia()
  const actualizarEstado = useActualizarEstadoGuardia()
  const [showForm, setShowForm] = useState(false)
  const [asignacionId, setAsignacionId] = useState('')
  const [materiaId, setMateriaId] = useState('')
  const [carreraId, setCarreraId] = useState('')
  const [cohorteId, setCohorteId] = useState('')
  const [dia, setDia] = useState<DiaSemanaGuardia>('Lunes')
  const [horario, setHorario] = useState('')
  const [comentarios, setComentarios] = useState('')

  function handleCrear(e: React.FormEvent) {
    e.preventDefault()
    crear.mutate({
      asignacion_id: asignacionId, materia_id: materiaId, carrera_id: carreraId,
      cohorte_id: cohorteId, dia, horario, comentarios: comentarios || null,
    }, { onSuccess: () => { setShowForm(false); setHorario(''); setComentarios('') } })
  }

  const items = view === 'admin' ? guardias?.items : misGuardias?.items

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-primary">Guardias</h2>
        <div className="flex gap-3">
          <button onClick={() => setView(view === 'admin' ? 'mis-guardias' : 'admin')}
            className="rounded border border-border px-3 py-1.5 text-xs font-medium hover:bg-surface-hover">
            {view === 'admin' ? 'Mis guardias' : 'Admin'}
          </button>
          <button onClick={() => setShowForm(!showForm)}
            className="rounded bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:bg-primary-hover">
            {showForm ? 'Cancelar' : 'Nueva guardia'}
          </button>
        </div>
      </div>

      {showForm && (
        <form onSubmit={handleCrear} className="max-w-lg space-y-4 rounded-lg border border-border bg-surface p-6">
          <h3 className="text-sm font-semibold text-on-surface">Registrar guardia</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="g-asignacion" className="mb-1 block text-sm text-on-surface">Asignación ID</label>
              <input id="g-asignacion" type="text" value={asignacionId} onChange={(e) => setAsignacionId(e.target.value)} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
            <div>
              <label htmlFor="g-materia" className="mb-1 block text-sm text-on-surface">Materia ID</label>
              <input id="g-materia" type="text" value={materiaId} onChange={(e) => setMateriaId(e.target.value)} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
            <div>
              <label htmlFor="g-carrera" className="mb-1 block text-sm text-on-surface">Carrera ID</label>
              <input id="g-carrera" type="text" value={carreraId} onChange={(e) => setCarreraId(e.target.value)} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
            <div>
              <label htmlFor="g-cohorte" className="mb-1 block text-sm text-on-surface">Cohorte ID</label>
              <input id="g-cohorte" type="text" value={cohorteId} onChange={(e) => setCohorteId(e.target.value)} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
            <div>
              <label htmlFor="g-dia" className="mb-1 block text-sm text-on-surface">Día</label>
              <select id="g-dia" value={dia} onChange={(e) => setDia(e.target.value as DiaSemanaGuardia)} className="w-full rounded border border-border bg-surface px-3 py-2 text-sm">
                {Object.entries(diaLabels).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
              </select>
            </div>
            <div>
              <label htmlFor="g-horario" className="mb-1 block text-sm text-on-surface">Horario</label>
              <input id="g-horario" type="text" value={horario} onChange={(e) => setHorario(e.target.value)} placeholder="Ej: 18:00–20:00" required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
            <div className="col-span-2">
              <label htmlFor="g-comentarios" className="mb-1 block text-sm text-on-surface">Comentarios (opcional)</label>
              <textarea id="g-comentarios" value={comentarios} onChange={(e) => setComentarios(e.target.value)} rows={2} className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
          </div>
          <div className="flex justify-end gap-3">
            <button type="button" onClick={() => setShowForm(false)} className="rounded border border-border px-4 py-2 text-sm hover:bg-surface-hover">Cancelar</button>
            <button type="submit" disabled={crear.isPending} className="rounded bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:bg-primary-hover disabled:opacity-50">Registrar</button>
          </div>
        </form>
      )}

      {items && items.length > 0 ? (
        <div className="space-y-3">
          {items.map((g) => (
            <div key={g.id} className="rounded-lg border border-border bg-surface p-4">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-medium text-on-surface">{diaLabels[g.dia]} – {g.horario}</p>
                  <p className="text-xs text-on-surface-muted">Materia: {g.materia_id.slice(0, 8)}...</p>
                </div>
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                  g.estado === 'Realizada' ? 'bg-success/10 text-success' :
                  g.estado === 'Cancelada' ? 'bg-danger/10 text-danger' : 'bg-warning/10 text-warning'
                }`}>{estadoLabels[g.estado]}</span>
              </div>
              {g.comentarios && <p className="mt-2 text-xs text-on-surface-muted">{g.comentarios}</p>}
              <div className="mt-3 flex gap-2">
                <button onClick={() => actualizarEstado.mutate({ id: g.id, estado: 'Realizada' })}
                  className="rounded border border-border px-2 py-1 text-xs hover:bg-surface-hover">Realizada</button>
                <button onClick={() => actualizarEstado.mutate({ id: g.id, estado: 'Cancelada' })}
                  className="rounded border border-border px-2 py-1 text-xs hover:bg-surface-hover">Cancelar</button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-sm text-on-surface-muted">Sin guardias.</p>
      )}
    </div>
  )
}
