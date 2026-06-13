import { useState } from 'react'
import { useProgramas, useCrearPrograma, useActualizarPrograma, useDesactivarPrograma, useGenerarContenidoPrograma } from '../hooks/useCoordinacion'
import { useCarreras, useMaterias, useCohortes } from '@/features/admin/hooks/useAdmin'

export default function ProgramasPage() {
  const { data: programas } = useProgramas()
  const crear = useCrearPrograma()
  const actualizar = useActualizarPrograma()
  const desactivar = useDesactivarPrograma()
  const generar = useGenerarContenidoPrograma()
  const { data: carreras } = useCarreras({ limit: 100 })
  const { data: materias } = useMaterias({ limit: 100 })
  const [showForm, setShowForm] = useState(false)
  const [editId, setEditId] = useState<string | null>(null)
  const [materiaId, setMateriaId] = useState('')
  const [carreraId, setCarreraId] = useState('')
  const [cohorteId, setCohorteId] = useState('')
  const { data: cohortes } = useCohortes({ carrera_id: carreraId || undefined, limit: 100 })
  const [titulo, setTitulo] = useState('')
  const [contenidoHtml, setContenidoHtml] = useState('')

  function handleCrear(e: React.FormEvent) {
    e.preventDefault()
    crear.mutate({ materia_id: materiaId, carrera_id: carreraId, cohorte_id: cohorteId || null, titulo }, {
      onSuccess: () => { setShowForm(false); setTitulo(''); setMateriaId(''); setCarreraId(''); setCohorteId('') },
    })
  }

  function handleGuardarContenido(id: string) {
    actualizar.mutate({ id, data: { contenido_html: contenidoHtml } })
    setEditId(null)
    setContenidoHtml('')
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-primary">Programas de Materias</h2>
        <button onClick={() => setShowForm(!showForm)}
          className="rounded bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:bg-primary-hover">
          {showForm ? 'Cancelar' : 'Nuevo programa'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCrear} className="max-w-lg space-y-4 rounded-lg border border-border bg-surface p-6">
          <h3 className="text-sm font-semibold text-on-surface">Crear programa</h3>
          <div>
            <label htmlFor="p-titulo" className="mb-1 block text-sm text-on-surface">Título</label>
            <input id="p-titulo" type="text" value={titulo} onChange={(e) => setTitulo(e.target.value)} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label htmlFor="p-carrera" className="mb-1 block text-sm text-on-surface">Carrera</label>
              <select id="p-carrera" value={carreraId} onChange={(e) => { setCarreraId(e.target.value); setCohorteId('') }} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm">
                <option value="">Seleccionar carrera</option>
                {carreras?.items.map(c => <option key={c.id} value={c.id}>{c.nombre} ({c.codigo})</option>)}
              </select>
            </div>
            <div>
              <label htmlFor="p-materia" className="mb-1 block text-sm text-on-surface">Materia</label>
              <select id="p-materia" value={materiaId} onChange={(e) => setMateriaId(e.target.value)} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm">
                <option value="">Seleccionar materia</option>
                {materias?.items.map(m => <option key={m.id} value={m.id}>{m.nombre} ({m.codigo})</option>)}
              </select>
            </div>
            <div>
              <label htmlFor="p-cohorte" className="mb-1 block text-sm text-on-surface">Cohorte (opcional)</label>
              <select id="p-cohorte" value={cohorteId} onChange={(e) => setCohorteId(e.target.value)} disabled={!carreraId} className="w-full rounded border border-border bg-surface px-3 py-2 text-sm disabled:opacity-50">
                <option value="">Sin cohorte</option>
                {cohortes?.items.map(c => <option key={c.id} value={c.id}>{c.nombre} ({c.anio})</option>)}
              </select>
            </div>
          </div>
          <div className="flex justify-end gap-3">
            <button type="button" onClick={() => setShowForm(false)} className="rounded border border-border px-4 py-2 text-sm hover:bg-surface-hover">Cancelar</button>
            <button type="submit" disabled={crear.isPending} className="rounded bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:bg-primary-hover disabled:opacity-50">Crear</button>
          </div>
        </form>
      )}

      <div className="space-y-3">
        {programas?.items?.map((p) => (
          <div key={p.id} className="rounded-lg border border-border bg-surface p-4">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-medium text-on-surface">{p.titulo}</p>
                <p className="text-xs text-on-surface-muted">v{p.version} {p.activo ? '(Activo)' : '(Inactivo)'}</p>
              </div>
              <div className="flex gap-2">
                <button onClick={() => { setEditId(p.id); setContenidoHtml(p.contenido_html ?? '') }}
                  className="rounded border border-border px-2 py-1 text-xs hover:bg-surface-hover">Editar</button>
                <button onClick={() => generar.mutate(p.id)} disabled={generar.isPending}
                  className="rounded border border-border px-2 py-1 text-xs hover:bg-surface-hover disabled:opacity-50">Generar</button>
                {p.activo && <button onClick={() => desactivar.mutate(p.id)}
                  className="rounded border border-border px-2 py-1 text-xs text-danger hover:bg-surface-hover">Desactivar</button>}
              </div>
            </div>
            {editId === p.id && (
              <div className="mt-4 space-y-2">
                <textarea value={contenidoHtml} onChange={(e) => setContenidoHtml(e.target.value)} rows={6}
                  className="w-full rounded border border-border bg-surface px-3 py-2 text-sm font-mono" />
                <div className="flex justify-end gap-2">
                  <button onClick={() => setEditId(null)} className="rounded border border-border px-3 py-1.5 text-xs hover:bg-surface-hover">Cancelar</button>
                  <button onClick={() => handleGuardarContenido(p.id)} disabled={actualizar.isPending}
                    className="rounded bg-primary px-3 py-1.5 text-xs font-medium text-on-primary hover:bg-primary-hover disabled:opacity-50">Guardar</button>
                </div>
              </div>
            )}
          </div>
        ))}
        {(!programas || programas.items.length === 0) && <p className="text-sm text-on-surface-muted">Sin programas.</p>}
      </div>
    </div>
  )
}
