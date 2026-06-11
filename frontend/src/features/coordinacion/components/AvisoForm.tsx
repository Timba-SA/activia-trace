import { useState } from 'react'
import type { AvisoCreateRequest, AvisoResponse, AvisoUpdateRequest } from '../types'

interface Props {
  aviso?: AvisoResponse
  onSave: (data: AvisoCreateRequest | AvisoUpdateRequest) => void
  onClose: () => void
  loading?: boolean
}

export function AvisoForm({ aviso, onSave, onClose, loading }: Props) {
  const [titulo, setTitulo] = useState(aviso?.titulo ?? '')
  const [cuerpo, setCuerpo] = useState(aviso?.cuerpo ?? '')
  const [alcance, setAlcance] = useState(aviso?.alcance ?? 'GENERAL')
  const [severidad, setSeveridad] = useState(aviso?.severidad ?? 'INFO')
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
    if (alcance === 'ROL') payload.rol_destino = rolDestino || null
    if (alcance === 'MATERIA') payload.materia_id = materiaId || null
    if (alcance === 'COHORTE') payload.cohorte_id = cohorteId || null
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
          <select value={alcance} onChange={(e) => setAlcance(e.target.value)} className="w-full rounded border border-border bg-surface px-3 py-2 text-sm">
            <option value="GENERAL">General</option>
            <option value="MATERIA">Por materia</option>
            <option value="COHORTE">Por cohorte</option>
            <option value="ROL">Por rol</option>
          </select>
        </div>
        <div>
          <label className="mb-1 block text-sm text-on-surface">Severidad</label>
          <select value={severidad} onChange={(e) => setSeveridad(e.target.value)} className="w-full rounded border border-border bg-surface px-3 py-2 text-sm">
            <option value="INFO">Info</option>
            <option value="WARNING">Warning</option>
            <option value="CRITICAL">Critical</option>
          </select>
        </div>
      </div>
      {alcance === 'ROL' && (
        <div>
          <label className="mb-1 block text-sm text-on-surface">Rol destino</label>
          <input type="text" value={rolDestino} onChange={(e) => setRolDestino(e.target.value)} className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
        </div>
      )}
      {alcance === 'MATERIA' && (
        <div>
          <label className="mb-1 block text-sm text-on-surface">Materia ID</label>
          <input type="text" value={materiaId} onChange={(e) => setMateriaId(e.target.value)} className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
        </div>
      )}
      {alcance === 'COHORTE' && (
        <div>
          <label className="mb-1 block text-sm text-on-surface">Cohorte ID</label>
          <input type="text" value={cohorteId} onChange={(e) => setCohorteId(e.target.value)} className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
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
