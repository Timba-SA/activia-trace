import { useState } from 'react'
import { useGuardias, useMisGuardias, useCrearGuardia, useActualizarEstadoGuardia, useEquipos } from '../hooks/useCoordinacion'
import { useCarreras, useCohortes, useMaterias } from '@/features/admin/hooks/useAdmin'
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

  const { data: carreras } = useCarreras({ limit: 100 })
  const { data: cohortes } = useCohortes({ carrera_id: carreraId || undefined, limit: 100 })
  const { data: materias } = useMaterias({ limit: 100 })
  const { data: equipos } = useEquipos()

  function handleCrear(e: React.FormEvent) {
    e.preventDefault()
    crear.mutate({
      asignacion_id: asignacionId, materia_id: materiaId,
      carrera_id: carreraId, cohorte_id: cohorteId,
      dia, horario, comentarios: comentarios || null,
    }, {
      onSuccess: () => {
        setShowForm(false)
        setHorario(''); setComentarios('')
        setAsignacionId(''); setMateriaId(''); setCarreraId(''); setCohorteId('')
      },
    })
  }

  const items = view === 'admin' ? guardias?.items : misGuardias?.items

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-primary">Guardias</h2>
        <div className="flex gap-3">
          <button
            onClick={() => setView(view === 'admin' ? 'mis-guardias' : 'admin')}
            className="rounded border border-outline-variant px-3 py-1.5 text-xs font-medium text-on-surface hover:bg-surface-container-high transition-colors"
          >
            {view === 'admin' ? 'Mis guardias' : 'Admin'}
          </button>
          <button
            onClick={() => setShowForm(!showForm)}
            className={`rounded px-4 py-2 text-sm font-medium transition-colors ${showForm ? 'border border-outline-variant text-on-surface hover:bg-surface-container-high' : 'bg-primary text-on-primary hover:opacity-90'}`}
          >
            {showForm ? 'Cancelar' : 'Nueva guardia'}
          </button>
        </div>
      </div>

      {showForm && (
        <form onSubmit={handleCrear} className="max-w-lg space-y-4 rounded-lg border border-outline-variant bg-surface p-6">
          <h3 className="text-sm font-semibold text-on-surface">Registrar guardia</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-1 block text-sm text-on-surface">Carrera</label>
              <select value={carreraId} onChange={(e) => { setCarreraId(e.target.value); setCohorteId('') }} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm">
                <option value="">Seleccionar carrera</option>
                {carreras?.items.map(c => <option key={c.id} value={c.id}>{c.nombre} ({c.codigo})</option>)}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm text-on-surface">Cohorte</label>
              <select value={cohorteId} onChange={(e) => setCohorteId(e.target.value)} required disabled={!carreraId} className="w-full rounded border border-border bg-surface px-3 py-2 text-sm disabled:opacity-50">
                <option value="">Seleccionar cohorte</option>
                {cohortes?.items.map(c => <option key={c.id} value={c.id}>{c.nombre} ({c.anio})</option>)}
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
              <label className="mb-1 block text-sm text-on-surface">Docente asignado</label>
              <select value={asignacionId} onChange={(e) => setAsignacionId(e.target.value)} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm">
                <option value="">Seleccionar docente</option>
                {equipos?.items.map(e => <option key={e.id} value={e.id}>{e.nombre} {e.apellido} — {e.rol}</option>)}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm text-on-surface">Día</label>
              <select value={dia} onChange={(e) => setDia(e.target.value as DiaSemanaGuardia)} className="w-full rounded border border-border bg-surface px-3 py-2 text-sm">
                {Object.entries(diaLabels).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm text-on-surface">Horario</label>
              <input type="text" value={horario} onChange={(e) => setHorario(e.target.value)} placeholder="18:00–20:00" required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
            <div className="col-span-2">
              <label className="mb-1 block text-sm text-on-surface">Comentarios (opcional)</label>
              <textarea value={comentarios} onChange={(e) => setComentarios(e.target.value)} rows={2} className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
          </div>
          {crear.error && <p className="text-sm text-danger">Error al registrar la guardia. Verificá los datos.</p>}
          <div className="flex justify-end gap-3">
            <button type="button" onClick={() => setShowForm(false)} className="rounded border border-outline-variant px-4 py-2 text-sm text-on-surface hover:bg-surface-container-high transition-colors">Cancelar</button>
            <button type="submit" disabled={crear.isPending} className="rounded bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:opacity-90 disabled:opacity-50 transition-colors">
              {crear.isPending ? 'Registrando...' : 'Registrar'}
            </button>
          </div>
        </form>
      )}

      {items && items.length > 0 ? (
        <div className="space-y-3">
          {items.map((g) => (
            <div key={g.id} className="rounded-lg border border-outline-variant bg-surface p-4">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-medium text-on-surface">{diaLabels[g.dia]} – {g.horario}</p>
                  <p className="text-xs text-on-surface-variant">Materia: {materias?.items.find(m => m.id === g.materia_id)?.nombre ?? g.materia_id.slice(0, 8) + '…'}</p>
                </div>
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                  g.estado === 'Realizada' ? 'bg-success/10 text-success' :
                  g.estado === 'Cancelada' ? 'bg-danger/10 text-danger' : 'bg-warning/10 text-warning'
                }`}>{estadoLabels[g.estado]}</span>
              </div>
              {g.comentarios && <p className="mt-2 text-xs text-on-surface-variant">{g.comentarios}</p>}
              <div className="mt-3 flex gap-2">
                <button onClick={() => actualizarEstado.mutate({ id: g.id, estado: 'Realizada' })} className="rounded border border-outline-variant px-2 py-1 text-xs text-on-surface hover:bg-surface-container-high transition-colors">Realizada</button>
                <button onClick={() => actualizarEstado.mutate({ id: g.id, estado: 'Cancelada' })} className="rounded border border-outline-variant px-2 py-1 text-xs text-on-surface hover:bg-surface-container-high transition-colors">Cancelar</button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-sm text-on-surface-variant">Sin guardias registradas.</p>
      )}
    </div>
  )
}
