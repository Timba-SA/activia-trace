import { useState } from 'react'
import type { AvisoCreateRequest, AvisoResponse, AvisoUpdateRequest, AlcanceAviso, SeveridadAviso } from '../types'
import { useMaterias, useCohortes } from '@/features/admin/hooks/useAdmin'

interface Props {
  aviso?: AvisoResponse
  onSave: (data: AvisoCreateRequest | AvisoUpdateRequest) => void
  onClose: () => void
  loading?: boolean
}

export function AvisoForm({ aviso, onSave, onClose, loading }: Props) {
  const { data: materias } = useMaterias({ limit: 100 })
  const { data: cohortes } = useCohortes({ limit: 100 })
  const [titulo, setTitulo] = useState(aviso?.titulo ?? '')
  const [cuerpo, setCuerpo] = useState(aviso?.cuerpo ?? '')
  const [alcance, setAlcance] = useState(aviso?.alcance ?? 'Global')
  const [severidad, setSeveridad] = useState(aviso?.severidad ?? 'Info')
  const [inicioEn, setInicioEn] = useState(aviso?.inicio_en ? aviso.inicio_en.slice(0, 16) : '')
  const [finEn, setFinEn] = useState(aviso?.fin_en ? aviso.fin_en.slice(0, 16) : '')
  const [requiereAck, setRequiereAck] = useState(aviso?.requiere_ack ?? false)
  const [activo, setActivo] = useState(aviso?.activo ?? true)
  const [rolDestino, setRolDestino] = useState(aviso?.rol_destino ?? '')
  const [materiaId, setMateriaId] = useState(aviso?.materia_id ?? '')
  const [cohorteId, setCohorteId] = useState(aviso?.cohorte_id ?? '')

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const payload: Record<string, unknown> = {
      titulo, cuerpo, alcance, severidad,
      inicio_en: new Date(inicioEn).toISOString(),
      fin_en: new Date(finEn).toISOString(),
      requiere_ack: requiereAck, activo, orden: aviso?.orden ?? 0,
    }
    if (alcance === 'PorRol') payload.rol_destino = rolDestino || null
    if (alcance === 'PorMateria') payload.materia_id = materiaId || null
    if (alcance === 'PorCohorte') payload.cohorte_id = cohorteId || null
    onSave(payload)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="mb-1 block text-sm text-on-surface">Título</label>
        <input type="text" value={titulo} onChange={(e) => setTitulo(e.target.value)} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
      </div>
      <div>
        <label className="mb-1 block text-sm text-on-surface">Cuerpo</label>
        <textarea value={cuerpo} onChange={(e) => setCuerpo(e.target.value)} required rows={4} className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="mb-1 block text-sm text-on-surface">Alcance</label>
          <select value={alcance} onChange={(e) => setAlcance(e.target.value as AlcanceAviso)} className="w-full rounded border border-border bg-surface px-3 py-2 text-sm">
            <option value="Global">General</option>
            <option value="PorMateria">Por materia</option>
            <option value="PorCohorte">Por cohorte</option>
            <option value="PorRol">Por rol</option>
          </select>
        </div>
        <div>
          <label className="mb-1 block text-sm text-on-surface">Severidad</label>
          <select value={severidad} onChange={(e) => setSeveridad(e.target.value as SeveridadAviso)} className="w-full rounded border border-border bg-surface px-3 py-2 text-sm">
            <option value="Info">Info</option>
            <option value="Advertencia">Advertencia</option>
            <option value="Critico">Crítico</option>
          </select>
        </div>
      </div>
      {alcance === 'PorRol' && (
        <div>
          <label className="mb-1 block text-sm text-on-surface">Rol destino</label>
          <input type="text" value={rolDestino} onChange={(e) => setRolDestino(e.target.value)} className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
        </div>
      )}
      {alcance === 'PorMateria' && (
        <div>
          <label className="mb-1 block text-sm text-on-surface">Materia</label>
          <select value={materiaId} onChange={(e) => setMateriaId(e.target.value)} className="w-full rounded border border-border bg-surface px-3 py-2 text-sm">
            <option value="">Seleccionar materia</option>
            {materias?.items.map(m => <option key={m.id} value={m.id}>{m.nombre} ({m.codigo})</option>)}
          </select>
        </div>
      )}
      {alcance === 'PorCohorte' && (
        <div>
          <label className="mb-1 block text-sm text-on-surface">Cohorte</label>
          <select value={cohorteId} onChange={(e) => setCohorteId(e.target.value)} className="w-full rounded border border-border bg-surface px-3 py-2 text-sm">
            <option value="">Seleccionar cohorte</option>
            {cohortes?.items.map(c => <option key={c.id} value={c.id}>{c.nombre} ({c.anio})</option>)}
          </select>
        </div>
      )}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="mb-1 block text-sm text-on-surface">Inicio</label>
          <input type="datetime-local" value={inicioEn} onChange={(e) => setInicioEn(e.target.value)} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
        </div>
        <div>
          <label className="mb-1 block text-sm text-on-surface">Fin</label>
          <input type="datetime-local" value={finEn} onChange={(e) => setFinEn(e.target.value)} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
        </div>
      </div>
      <div className="flex items-center gap-6">
        <label className="flex items-center gap-2 text-sm text-on-surface">
          <input type="checkbox" checked={activo} onChange={(e) => setActivo(e.target.checked)} />
          Activo
        </label>
        <label className="flex items-center gap-2 text-sm text-on-surface">
          <input type="checkbox" checked={requiereAck} onChange={(e) => setRequiereAck(e.target.checked)} />
          Requiere acknowledgment
        </label>
      </div>
      <div className="flex justify-end gap-3 pt-2">
        <button type="button" onClick={onClose} className="rounded border border-border px-4 py-2 text-sm hover:bg-surface-hover">Cancelar</button>
        <button type="submit" disabled={loading} className="rounded bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:bg-primary-hover disabled:opacity-50">
          {loading ? 'Guardando...' : aviso ? 'Actualizar' : 'Crear aviso'}
        </button>
      </div>
    </form>
  )
}
