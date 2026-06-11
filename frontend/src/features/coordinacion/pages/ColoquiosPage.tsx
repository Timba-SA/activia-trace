import { useState } from 'react'
import { useConvocatorias, useCrearConvocatoria, useCerrarConvocatoria } from '../hooks/useCoordinacion'
import type { TipoEvaluacion } from '../types'

const tipoLabels: Record<TipoEvaluacion, string> = { Parcial: 'Parcial', TP: 'TP', Coloquio: 'Coloquio', Recuperatorio: 'Recuperatorio' }

export default function ColoquiosPage() {
  const { data: convocatorias } = useConvocatorias()
  const crear = useCrearConvocatoria()
  const cerrar = useCerrarConvocatoria()
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
      onSuccess: () => { setShowForm(false); setInstancia(''); setTurnos([{ fecha: '', hora: '08:00', cupo_total: 30 }]) },
    })
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-primary">Coloquios</h2>
        <button onClick={() => setShowForm(!showForm)}
          className="rounded bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:bg-primary-hover">
          {showForm ? 'Cancelar' : 'Nueva convocatoria'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCrear} className="max-w-xl space-y-4 rounded-lg border border-border bg-surface p-6">
          <h3 className="text-sm font-semibold text-on-surface">Crear convocatoria</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="c-materia" className="mb-1 block text-sm text-on-surface">Materia ID</label>
              <input id="c-materia" type="text" value={materiaId} onChange={(e) => setMateriaId(e.target.value)} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
            <div>
              <label htmlFor="c-cohorte" className="mb-1 block text-sm text-on-surface">Cohorte ID</label>
              <input id="c-cohorte" type="text" value={cohorteId} onChange={(e) => setCohorteId(e.target.value)} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
            <div>
              <label htmlFor="c-tipo" className="mb-1 block text-sm text-on-surface">Tipo</label>
              <select id="c-tipo" value={tipo} onChange={(e) => setTipo(e.target.value as TipoEvaluacion)} className="w-full rounded border border-border bg-surface px-3 py-2 text-sm">
                {Object.entries(tipoLabels).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
              </select>
            </div>
            <div>
              <label htmlFor="c-instancia" className="mb-1 block text-sm text-on-surface">Instancia</label>
              <input id="c-instancia" type="text" value={instancia} onChange={(e) => setInstancia(e.target.value)} placeholder="Ej: 1er Parcial" required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
          </div>

          <div>
            <div className="mb-2 flex items-center justify-between">
              <label className="text-sm font-medium text-on-surface">Turnos</label>
              <button type="button" onClick={agregarTurno} className="text-xs text-primary hover:underline">+ Agregar turno</button>
            </div>
            <div className="space-y-2">
              {turnos.map((t, idx) => (
                <div key={idx} className="flex gap-2 items-center">
                  <input type="date" value={t.fecha} onChange={(e) => actualizarTurno(idx, 'fecha', e.target.value)} required className="flex-1 rounded border border-border bg-surface px-2 py-1.5 text-sm" />
                  <input type="time" value={t.hora} onChange={(e) => actualizarTurno(idx, 'hora', e.target.value)} required className="w-28 rounded border border-border bg-surface px-2 py-1.5 text-sm" />
                  <input type="number" value={t.cupo_total} onChange={(e) => actualizarTurno(idx, 'cupo_total', parseInt(e.target.value))} min={1} className="w-20 rounded border border-border bg-surface px-2 py-1.5 text-sm" />
                  <button type="button" onClick={() => quitarTurno(idx)} className="text-xs text-danger hover:underline">Quitar</button>
                </div>
              ))}
            </div>
          </div>

          <div className="flex justify-end gap-3">
            <button type="button" onClick={() => setShowForm(false)} className="rounded border border-border px-4 py-2 text-sm hover:bg-surface-hover">Cancelar</button>
            <button type="submit" disabled={crear.isPending} className="rounded bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:bg-primary-hover disabled:opacity-50">Crear</button>
          </div>
        </form>
      )}

      <div className="space-y-3">
        {convocatorias?.items?.map((c) => (
          <div key={c.id} className="rounded-lg border border-border bg-surface p-4">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-medium text-on-surface">{tipoLabels[c.tipo]} – {c.instancia}</p>
                <p className="text-xs text-on-surface-muted">{c.turnos?.length ?? 0} turnos</p>
              </div>
              <button onClick={() => cerrar.mutate(c.id)}
                className="rounded border border-border px-3 py-1 text-xs font-medium text-danger hover:bg-surface-hover">Cerrar</button>
            </div>
            {c.turnos && c.turnos.length > 0 && (
              <div className="mt-3 space-y-1">
                {c.turnos.map((t) => (
                  <div key={t.id} className="flex items-center justify-between rounded bg-surface px-3 py-1.5 text-xs">
                    <span>{t.fecha} {t.hora}</span>
                    <span className="text-on-surface-muted">{t.cupos_restantes}/{t.cupo_total} cupos</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
        {(!convocatorias || convocatorias.items.length === 0) && <p className="text-sm text-on-surface-muted">Sin convocatorias.</p>}
      </div>
    </div>
  )
}
