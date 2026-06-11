import { useState } from 'react'
import { useSlotsEncuentro, useCrearSlotEncuentro, useInstanciasEncuentro, useCrearInstanciaEncuentro, useActualizarInstanciaEncuentro } from '../hooks/useCoordinacion'
import type { DiaSemana, EstadoInstancia } from '../types'

const diaLabels: Record<DiaSemana, string> = { Lunes: 'Lun', Martes: 'Mar', Miercoles: 'Mié', Jueves: 'Jue', Viernes: 'Vie', Sabado: 'Sáb', Domingo: 'Dom' }

export default function EncuentrosPage() {
  const [tab, setTab] = useState<'slots' | 'instancias'>('instancias')
  const { data: instancias } = useInstanciasEncuentro()
  const { data: slots } = useSlotsEncuentro()
  const crearInstancia = useCrearInstanciaEncuentro()
  const actualizarInstancia = useActualizarInstanciaEncuentro()
  const crearSlot = useCrearSlotEncuentro()
  const [showSlotForm, setShowSlotForm] = useState(false)
  const [showInstForm, setShowInstForm] = useState(false)
  const [sMateriaId, setSMateriaId] = useState('')
  const [sAsignacionId, setSAsignacionId] = useState('')
  const [sTitulo, setSTitulo] = useState('')
  const [sHora, setSHora] = useState('08:00')
  const [sDia, setSDia] = useState('Lunes')
  const [sFechaInicio, setSFechaInicio] = useState('')
  const [sCantSemanas, setSCantSemanas] = useState('16')
  const [sVigDesde, setSVigDesde] = useState('')
  const [sVigHasta, setSVigHasta] = useState('')
  const [iMateriaId, setIMateriaId] = useState('')
  const [iSlotId, setISlotId] = useState('')
  const [iFecha, setIFecha] = useState('')
  const [iHora, setIHora] = useState('08:00')
  const [iTitulo, setITitulo] = useState('')

  function handleCrearSlot(e: React.FormEvent) {
    e.preventDefault()
    crearSlot.mutate({
      asignacion_id: sAsignacionId, materia_id: sMateriaId, titulo: sTitulo,
      hora: sHora, dia_semana: sDia as DiaSemana, fecha_inicio: sFechaInicio,
      cant_semanas: parseInt(sCantSemanas), vig_desde: sVigDesde, vig_hasta: sVigHasta,
    }, { onSuccess: () => { setShowSlotForm(false); setSTitulo('') } })
  }

  function handleCrearInstancia(e: React.FormEvent) {
    e.preventDefault()
    crearInstancia.mutate({
      materia_id: iMateriaId, slot_id: iSlotId || null,
      fecha: iFecha, hora: iHora, titulo: iTitulo,
    }, { onSuccess: () => { setShowInstForm(false); setITitulo('') } })
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-primary">Encuentros y Guardias</h2>
        <div className="flex gap-3">
          <button onClick={() => setTab('instancias')} className={`rounded px-3 py-1.5 text-xs font-medium ${tab === 'instancias' ? 'bg-primary text-on-primary' : 'border border-border hover:bg-surface-hover'}`}>Instancias</button>
          <button onClick={() => setTab('slots')} className={`rounded px-3 py-1.5 text-xs font-medium ${tab === 'slots' ? 'bg-primary text-on-primary' : 'border border-border hover:bg-surface-hover'}`}>Slots</button>
          {tab === 'slots' && <button onClick={() => setShowSlotForm(!showSlotForm)} className="rounded bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:bg-primary-hover">{showSlotForm ? 'Cancelar' : 'Nuevo slot'}</button>}
          {tab === 'instancias' && <button onClick={() => setShowInstForm(!showInstForm)} className="rounded bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:bg-primary-hover">{showInstForm ? 'Cancelar' : 'Nueva instancia'}</button>}
        </div>
      </div>

      {showSlotForm && (
        <form onSubmit={handleCrearSlot} className="max-w-lg space-y-4 rounded-lg border border-border bg-surface p-6">
          <h3 className="text-sm font-semibold text-on-surface">Nuevo slot de encuentro</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="s-materia" className="mb-1 block text-sm text-on-surface">Materia ID</label>
              <input id="s-materia" type="text" value={sMateriaId} onChange={(e) => setSMateriaId(e.target.value)} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
            <div>
              <label htmlFor="s-asignacion" className="mb-1 block text-sm text-on-surface">Asignación ID</label>
              <input id="s-asignacion" type="text" value={sAsignacionId} onChange={(e) => setSAsignacionId(e.target.value)} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
            <div className="col-span-2">
              <label htmlFor="s-titulo" className="mb-1 block text-sm text-on-surface">Título</label>
              <input id="s-titulo" type="text" value={sTitulo} onChange={(e) => setSTitulo(e.target.value)} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
            <div>
              <label htmlFor="s-hora" className="mb-1 block text-sm text-on-surface">Hora</label>
              <input id="s-hora" type="time" value={sHora} onChange={(e) => setSHora(e.target.value)} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
            <div>
              <label htmlFor="s-dia" className="mb-1 block text-sm text-on-surface">Día</label>
              <select id="s-dia" value={sDia} onChange={(e) => setSDia(e.target.value)} className="w-full rounded border border-border bg-surface px-3 py-2 text-sm">
                {Object.entries(diaLabels).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
              </select>
            </div>
            <div>
              <label htmlFor="s-fecha-inicio" className="mb-1 block text-sm text-on-surface">Fecha inicio</label>
              <input id="s-fecha-inicio" type="date" value={sFechaInicio} onChange={(e) => setSFechaInicio(e.target.value)} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
            <div>
              <label htmlFor="s-semanas" className="mb-1 block text-sm text-on-surface">Semanas</label>
              <input id="s-semanas" type="number" value={sCantSemanas} onChange={(e) => setSCantSemanas(e.target.value)} min={0} max={52} className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
            <div>
              <label htmlFor="s-vig-desde" className="mb-1 block text-sm text-on-surface">Vigencia desde</label>
              <input id="s-vig-desde" type="date" value={sVigDesde} onChange={(e) => setSVigDesde(e.target.value)} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
            <div>
              <label htmlFor="s-vig-hasta" className="mb-1 block text-sm text-on-surface">Vigencia hasta</label>
              <input id="s-vig-hasta" type="date" value={sVigHasta} onChange={(e) => setSVigHasta(e.target.value)} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
          </div>
          <div className="flex justify-end gap-3">
            <button type="button" onClick={() => setShowSlotForm(false)} className="rounded border border-border px-4 py-2 text-sm hover:bg-surface-hover">Cancelar</button>
            <button type="submit" disabled={crearSlot.isPending} className="rounded bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:bg-primary-hover disabled:opacity-50">Crear slot</button>
          </div>
        </form>
      )}

      {showInstForm && (
        <form onSubmit={handleCrearInstancia} className="max-w-lg space-y-4 rounded-lg border border-border bg-surface p-6">
          <h3 className="text-sm font-semibold text-on-surface">Nueva instancia</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="i-materia" className="mb-1 block text-sm text-on-surface">Materia ID</label>
              <input id="i-materia" type="text" value={iMateriaId} onChange={(e) => setIMateriaId(e.target.value)} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
            <div>
              <label htmlFor="i-slot" className="mb-1 block text-sm text-on-surface">Slot ID (opcional)</label>
              <input id="i-slot" type="text" value={iSlotId} onChange={(e) => setISlotId(e.target.value)} className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
            <div>
              <label htmlFor="i-fecha" className="mb-1 block text-sm text-on-surface">Fecha</label>
              <input id="i-fecha" type="date" value={iFecha} onChange={(e) => setIFecha(e.target.value)} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
            <div>
              <label htmlFor="i-hora" className="mb-1 block text-sm text-on-surface">Hora</label>
              <input id="i-hora" type="time" value={iHora} onChange={(e) => setIHora(e.target.value)} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
            <div className="col-span-2">
              <label htmlFor="i-titulo" className="mb-1 block text-sm text-on-surface">Título</label>
              <input id="i-titulo" type="text" value={iTitulo} onChange={(e) => setITitulo(e.target.value)} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
          </div>
          <div className="flex justify-end gap-3">
            <button type="button" onClick={() => setShowInstForm(false)} className="rounded border border-border px-4 py-2 text-sm hover:bg-surface-hover">Cancelar</button>
            <button type="submit" disabled={crearInstancia.isPending} className="rounded bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:bg-primary-hover disabled:opacity-50">Crear instancia</button>
          </div>
        </form>
      )}

      {tab === 'slots' && (
        <div className="space-y-3">
          {slots?.items?.map((s) => (
            <div key={s.id} className="rounded-lg border border-border bg-surface p-4">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-medium text-on-surface">{s.titulo}</p>
                  <p className="text-xs text-on-surface-muted">{diaLabels[s.dia_semana]} {s.hora} • {s.fecha_inicio} ({s.cant_semanas} semanas)</p>
                </div>
              </div>
              {s.meet_url && <a href={s.meet_url} className="mt-2 inline-block text-xs text-primary hover:underline">{s.meet_url}</a>}
              <p className="mt-2 text-xs text-on-surface-muted">Vigencia: {s.vig_desde} – {s.vig_hasta}</p>
            </div>
          ))}
          {(!slots || slots.items.length === 0) && <p className="text-sm text-on-surface-muted">Sin slots.</p>}
        </div>
      )}

      {tab === 'instancias' && (
        <div className="space-y-3">
          {instancias?.items?.map((i) => (
            <div key={i.id} className="rounded-lg border border-border bg-surface p-4">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-medium text-on-surface">{i.titulo}</p>
                  <p className="text-xs text-on-surface-muted">{i.fecha} {i.hora}</p>
                </div>
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${i.estado === 'Realizado' ? 'bg-success/10 text-success' : i.estado === 'Cancelado' ? 'bg-danger/10 text-danger' : 'bg-warning/10 text-warning'}`}>{i.estado}</span>
              </div>
              {i.meet_url && <a href={i.meet_url} className="mt-2 inline-block text-xs text-primary hover:underline">{i.meet_url}</a>}
              {i.comentario && <p className="mt-2 text-xs text-on-surface-muted">{i.comentario}</p>}
              <div className="mt-3 flex gap-2">
                <button onClick={() => actualizarInstancia.mutate({ id: i.id, data: { estado: 'Realizado' as EstadoInstancia } })}
                  className="rounded border border-border px-2 py-1 text-xs hover:bg-surface-hover">✅ Realizada</button>
                <button onClick={() => actualizarInstancia.mutate({ id: i.id, data: { estado: 'Cancelado' as EstadoInstancia } })}
                  className="rounded border border-border px-2 py-1 text-xs hover:bg-surface-hover">❌ Cancelar</button>
              </div>
            </div>
          ))}
          {(!instancias || instancias.items.length === 0) && <p className="text-sm text-on-surface-muted">Sin instancias.</p>}
        </div>
      )}
    </div>
  )
}
