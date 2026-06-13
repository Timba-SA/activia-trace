import { useState } from 'react'
import { useSlotsEncuentro, useCrearSlotEncuentro, useInstanciasEncuentro, useCrearInstanciaEncuentro, useActualizarInstanciaEncuentro, useEquipos } from '../hooks/useCoordinacion'
import { useMaterias } from '@/features/admin/hooks/useAdmin'
import type { DiaSemana, EstadoInstancia } from '../types'

const diaLabels: Record<DiaSemana, string> = { Lunes: 'Lun', Martes: 'Mar', Miercoles: 'Mié', Jueves: 'Jue', Viernes: 'Vie', Sabado: 'Sáb', Domingo: 'Dom' }

export default function EncuentrosPage() {
  const [tab, setTab] = useState<'slots' | 'instancias'>('instancias')
  const { data: instancias } = useInstanciasEncuentro()
  const { data: slots } = useSlotsEncuentro()
  const { data: materias } = useMaterias({ limit: 100 })
  const { data: equipos } = useEquipos()
  const crearInstancia = useCrearInstanciaEncuentro()
  const actualizarInstancia = useActualizarInstanciaEncuentro()
  const crearSlot = useCrearSlotEncuentro()
  const [showSlotForm, setShowSlotForm] = useState(false)
  const [showInstForm, setShowInstForm] = useState(false)

  // Slot form state
  const [sMateriaId, setSMateriaId] = useState('')
  const [sAsignacionId, setSAsignacionId] = useState('')
  const [sTitulo, setSTitulo] = useState('')
  const [sHora, setSHora] = useState('08:00')
  const [sDia, setSDia] = useState('Lunes')
  const [sFechaInicio, setSFechaInicio] = useState('')
  const [sCantSemanas, setSCantSemanas] = useState('16')
  const [sVigDesde, setSVigDesde] = useState('')
  const [sVigHasta, setSVigHasta] = useState('')

  // Instancia form state
  const [iMateriaId, setIMateriaId] = useState('')
  const [iSlotId, setISlotId] = useState('')
  const [iFecha, setIFecha] = useState('')
  const [iHora, setIHora] = useState('08:00')
  const [iTitulo, setITitulo] = useState('')

  function handleCrearSlot(e: React.FormEvent) {
    e.preventDefault()
    crearSlot.mutate({
      asignacion_id: sAsignacionId,
      materia_id: sMateriaId,
      titulo: sTitulo,
      hora: sHora,
      dia_semana: sDia as DiaSemana,
      fecha_inicio: sFechaInicio,
      cant_semanas: parseInt(sCantSemanas),
      vig_desde: sVigDesde,
      vig_hasta: sVigHasta,
    }, {
      onSuccess: () => { setShowSlotForm(false); setSTitulo(''); setSMateriaId(''); setSAsignacionId('') }
    })
  }

  function handleCrearInstancia(e: React.FormEvent) {
    e.preventDefault()
    crearInstancia.mutate({
      materia_id: iMateriaId,
      slot_id: iSlotId || null,
      fecha: iFecha,
      hora: iHora,
      titulo: iTitulo,
    }, {
      onSuccess: () => { setShowInstForm(false); setITitulo(''); setIMateriaId('') }
    })
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-primary">Encuentros y Guardias</h2>
        {tab === 'slots' && (
          <button
            onClick={() => setShowSlotForm(!showSlotForm)}
            className={`rounded px-4 py-2 text-sm font-medium transition-colors ${showSlotForm ? 'border border-outline-variant text-on-surface hover:bg-surface-container-high' : 'bg-primary text-on-primary hover:opacity-90'}`}
          >
            {showSlotForm ? 'Cancelar' : 'Nuevo slot'}
          </button>
        )}
        {tab === 'instancias' && (
          <button
            onClick={() => setShowInstForm(!showInstForm)}
            className={`rounded px-4 py-2 text-sm font-medium transition-colors ${showInstForm ? 'border border-outline-variant text-on-surface hover:bg-surface-container-high' : 'bg-primary text-on-primary hover:opacity-90'}`}
          >
            {showInstForm ? 'Cancelar' : 'Nueva instancia'}
          </button>
        )}
      </div>

      <div className="flex border-b border-outline-variant">
        <button
          onClick={() => setTab('instancias')}
          className={`-mb-px border-b-2 px-4 py-2 text-sm font-medium transition-colors ${tab === 'instancias' ? 'border-primary text-primary' : 'border-transparent text-on-surface-variant hover:text-on-surface'}`}
        >
          Instancias
        </button>
        <button
          onClick={() => setTab('slots')}
          className={`-mb-px border-b-2 px-4 py-2 text-sm font-medium transition-colors ${tab === 'slots' ? 'border-primary text-primary' : 'border-transparent text-on-surface-variant hover:text-on-surface'}`}
        >
          Slots
        </button>
      </div>

      {showSlotForm && (
        <form onSubmit={handleCrearSlot} className="max-w-lg space-y-4 rounded-lg border border-border bg-surface p-6">
          <h3 className="text-sm font-semibold text-on-surface">Nuevo slot de encuentro</h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <label htmlFor="s-materia" className="mb-1 block text-sm text-on-surface">Materia</label>
              <select id="s-materia" value={sMateriaId} onChange={(e) => setSMateriaId(e.target.value)} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm">
                <option value="">Seleccionar materia</option>
                {materias?.items.map(m => <option key={m.id} value={m.id}>{m.nombre} ({m.codigo})</option>)}
              </select>
            </div>
            <div className="col-span-2">
              <label htmlFor="s-asignacion" className="mb-1 block text-sm text-on-surface">Asignación docente</label>
              <select id="s-asignacion" value={sAsignacionId} onChange={(e) => setSAsignacionId(e.target.value)} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm">
                <option value="">Seleccionar docente</option>
                {equipos?.items.map(e => (
                  <option key={e.id} value={e.id}>
                    {e.nombre} {e.apellido} — {e.rol}
                  </option>
                ))}
              </select>
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
              <input id="s-semanas" type="number" value={sCantSemanas} onChange={(e) => setSCantSemanas(e.target.value)} min={1} max={52} className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
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
            <button type="submit" disabled={crearSlot.isPending} className="rounded bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:bg-primary-hover disabled:opacity-50">
              {crearSlot.isPending ? 'Creando...' : 'Crear slot'}
            </button>
          </div>
        </form>
      )}

      {showInstForm && (
        <form onSubmit={handleCrearInstancia} className="max-w-lg space-y-4 rounded-lg border border-border bg-surface p-6">
          <h3 className="text-sm font-semibold text-on-surface">Nueva instancia de encuentro</h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <label htmlFor="i-materia" className="mb-1 block text-sm text-on-surface">Materia</label>
              <select id="i-materia" value={iMateriaId} onChange={(e) => setIMateriaId(e.target.value)} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm">
                <option value="">Seleccionar materia</option>
                {materias?.items.map(m => <option key={m.id} value={m.id}>{m.nombre} ({m.codigo})</option>)}
              </select>
            </div>
            <div className="col-span-2">
              <label htmlFor="i-slot" className="mb-1 block text-sm text-on-surface">Slot (opcional)</label>
              <select id="i-slot" value={iSlotId} onChange={(e) => setISlotId(e.target.value)} className="w-full rounded border border-border bg-surface px-3 py-2 text-sm">
                <option value="">Sin slot asociado</option>
                {slots?.items.map(s => (
                  <option key={s.id} value={s.id}>{s.titulo} — {diaLabels[s.dia_semana]} {s.hora}</option>
                ))}
              </select>
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
            <button type="submit" disabled={crearInstancia.isPending} className="rounded bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:bg-primary-hover disabled:opacity-50">
              {crearInstancia.isPending ? 'Creando...' : 'Crear instancia'}
            </button>
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
          {(!slots || slots.items.length === 0) && <p className="text-sm text-on-surface-muted">Sin slots registrados.</p>}
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
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${i.estado === 'Realizado' ? 'bg-success/10 text-success' : i.estado === 'Cancelado' ? 'bg-danger/10 text-danger' : 'bg-warning/10 text-warning'}`}>
                  {i.estado}
                </span>
              </div>
              {i.meet_url && <a href={i.meet_url} className="mt-2 inline-block text-xs text-primary hover:underline">{i.meet_url}</a>}
              {i.comentario && <p className="mt-2 text-xs text-on-surface-muted">{i.comentario}</p>}
              <div className="mt-3 flex gap-2">
                <button
                  onClick={() => actualizarInstancia.mutate({ id: i.id, data: { estado: 'Realizado' as EstadoInstancia } })}
                  className="rounded border border-border px-2 py-1 text-xs hover:bg-surface-hover"
                >
                  ✅ Realizada
                </button>
                <button
                  onClick={() => actualizarInstancia.mutate({ id: i.id, data: { estado: 'Cancelado' as EstadoInstancia } })}
                  className="rounded border border-border px-2 py-1 text-xs hover:bg-surface-hover"
                >
                  ❌ Cancelar
                </button>
              </div>
            </div>
          ))}
          {(!instancias || instancias.items.length === 0) && <p className="text-sm text-on-surface-muted">Sin instancias registradas.</p>}
        </div>
      )}
    </div>
  )
}
