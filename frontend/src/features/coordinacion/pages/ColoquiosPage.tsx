import { useState } from 'react'
import { useConvocatorias, useCrearConvocatoria, useCerrarConvocatoria } from '../hooks/useCoordinacion'
import { useMaterias, useCohortes } from '@/features/admin/hooks/useAdmin'
import type { TipoEvaluacion } from '../types'

const tipoLabels: Record<TipoEvaluacion, string> = { Parcial: 'Parcial', TP: 'TP', Coloquio: 'Coloquio', Recuperatorio: 'Recuperatorio' }

export default function ColoquiosPage() {
  const { data: convocatorias } = useConvocatorias()
  const crear = useCrearConvocatoria()
  const cerrar = useCerrarConvocatoria()
  const { data: materias } = useMaterias({ limit: 100 })
  const { data: cohortes } = useCohortes({ limit: 100 })

  const [showForm, setShowForm] = useState(false)
  const [materiaId, setMateriaId] = useState('')
  const [cohorteId, setCohorteId] = useState('')
  const [tipo, setTipo] = useState<TipoEvaluacion>('Parcial')
  const [instancia, setInstancia] = useState('')
  const [turnos, setTurnos] = useState<{ fecha: string; hora: string; cupo_total: number }[]>([{ fecha: '', hora: '08:00', cupo_total: 30 }])

  function agregarTurno() {
    setTurnos([...turnos, { fecha: '', hora: '08:00', cupo_total: 30 }])
  }

  function actualizarTurno(idx: number, field: string, value: string | number) {
    setTurnos(turnos.map((t, i) => i === idx ? { ...t, [field]: value } : t))
  }

  function quitarTurno(idx: number) {
    setTurnos(turnos.filter((_, i) => i !== idx))
  }

  function handleCrear(e: React.FormEvent) {
    e.preventDefault()
    crear.mutate({ materia_id: materiaId, cohorte_id: cohorteId, tipo, instancia, turnos }, {
      onSuccess: () => {
        setShowForm(false)
        setInstancia(''); setMateriaId(''); setCohorteId('')
        setTurnos([{ fecha: '', hora: '08:00', cupo_total: 30 }])
      },
    })
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-primary">Coloquios</h2>
        <button
          onClick={() => setShowForm(!showForm)}
          className={`rounded px-4 py-2 text-sm font-medium transition-colors ${showForm ? 'border border-outline-variant text-on-surface hover:bg-surface-container-high' : 'bg-primary text-on-primary hover:opacity-90'}`}
        >
          {showForm ? 'Cancelar' : 'Nueva convocatoria'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCrear} className="max-w-xl space-y-4 rounded-lg border border-outline-variant bg-surface p-6">
          <h3 className="text-sm font-semibold text-on-surface">Crear convocatoria</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-1 block text-sm text-on-surface">Materia</label>
              <select value={materiaId} onChange={(e) => setMateriaId(e.target.value)} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm">
                <option value="">Seleccionar materia</option>
                {materias?.items.map(m => <option key={m.id} value={m.id}>{m.nombre} ({m.codigo})</option>)}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm text-on-surface">Cohorte</label>
              <select value={cohorteId} onChange={(e) => setCohorteId(e.target.value)} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm">
                <option value="">Seleccionar cohorte</option>
                {cohortes?.items.map(c => <option key={c.id} value={c.id}>{c.nombre} ({c.anio})</option>)}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm text-on-surface">Tipo</label>
              <select value={tipo} onChange={(e) => setTipo(e.target.value as TipoEvaluacion)} className="w-full rounded border border-border bg-surface px-3 py-2 text-sm">
                {Object.entries(tipoLabels).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm text-on-surface">Instancia</label>
              <input type="text" value={instancia} onChange={(e) => setInstancia(e.target.value)} placeholder="Ej: 1er Parcial" required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
          </div>

          <div>
            <div className="mb-2 flex items-center justify-between">
              <label className="text-sm font-medium text-on-surface">Turnos</label>
              <button type="button" onClick={agregarTurno} className="text-xs text-primary hover:underline">+ Agregar turno</button>
            </div>
            <div className="space-y-2">
              {turnos.map((t, idx) => (
                <div key={idx} className="flex items-center gap-2">
                  <input type="date" value={t.fecha} onChange={(e) => actualizarTurno(idx, 'fecha', e.target.value)} required className="flex-1 rounded border border-border bg-surface px-2 py-1.5 text-sm" />
                  <input type="time" value={t.hora} onChange={(e) => actualizarTurno(idx, 'hora', e.target.value)} required className="w-28 rounded border border-border bg-surface px-2 py-1.5 text-sm" />
                  <input type="number" value={t.cupo_total} onChange={(e) => actualizarTurno(idx, 'cupo_total', parseInt(e.target.value))} min={1} placeholder="Cupo" className="w-20 rounded border border-border bg-surface px-2 py-1.5 text-sm" />
                  {turnos.length > 1 && (
                    <button type="button" onClick={() => quitarTurno(idx)} className="text-xs text-danger hover:underline">Quitar</button>
                  )}
                </div>
              ))}
            </div>
          </div>

          {crear.error && <p className="text-sm text-danger">Error al crear la convocatoria. Verificá los datos.</p>}
          <div className="flex justify-end gap-3">
            <button type="button" onClick={() => setShowForm(false)} className="rounded border border-outline-variant px-4 py-2 text-sm text-on-surface hover:bg-surface-container-high transition-colors">Cancelar</button>
            <button type="submit" disabled={crear.isPending} className="rounded bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:opacity-90 disabled:opacity-50 transition-colors">
              {crear.isPending ? 'Creando...' : 'Crear'}
            </button>
          </div>
        </form>
      )}

      <div className="space-y-3">
        {convocatorias?.items?.map((c) => (
          <div key={c.id} className="rounded-lg border border-outline-variant bg-surface p-4">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-medium text-on-surface">{tipoLabels[c.tipo]} – {c.instancia}</p>
                <p className="text-xs text-on-surface-variant">{c.turnos?.length ?? 0} turnos</p>
              </div>
              <button
                onClick={() => cerrar.mutate(c.id)}
                className="rounded border border-outline-variant px-3 py-1 text-xs font-medium text-danger hover:bg-surface-container-high transition-colors"
              >
                Cerrar
              </button>
            </div>
            {c.turnos && c.turnos.length > 0 && (
              <div className="mt-3 space-y-1">
                {c.turnos.map((t) => (
                  <div key={t.id} className="flex items-center justify-between rounded bg-surface-container-low px-3 py-1.5 text-xs">
                    <span className="text-on-surface">{t.fecha} {t.hora}</span>
                    <span className="text-on-surface-variant">{t.cupos_restantes}/{t.cupo_total} cupos</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
        {(!convocatorias || convocatorias.items.length === 0) && (
          <p className="text-sm text-on-surface-variant">Sin convocatorias.</p>
        )}
      </div>
    </div>
  )
}
