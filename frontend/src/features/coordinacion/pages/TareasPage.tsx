import { useState } from 'react'
import { useTareas, useTareasAdmin, useCrearTarea, useActualizarTarea, useComentarios, useAgregarComentario } from '../hooks/useCoordinacion'
import type { TareaResponse, EstadoTarea } from '../types'

const estadoLabels: Record<string, string> = { Pendiente: 'Pendiente', 'En progreso': 'En progreso', Resuelta: 'Resuelta', Cancelada: 'Cancelada' }
const estadoColors: Record<string, string> = {
  Pendiente: 'bg-warning/10 text-warning',
  'En progreso': 'bg-primary/10 text-primary',
  Resuelta: 'bg-success/10 text-success',
  Cancelada: 'bg-on-surface-muted/10 text-on-surface-muted',
}

function TareaCard({ tarea, onOpen }: { tarea: TareaResponse; onOpen: (id: string) => void }) {
  return (
    <div className="rounded-lg border border-border bg-surface p-4 hover:shadow-sm">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-on-surface">{tarea.descripcion}</p>
          <p className="mt-1 text-xs text-on-surface-muted">
            Creada: {new Date(tarea.created_at).toLocaleDateString()}
          </p>
        </div>
        <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${estadoColors[tarea.estado]}`}>
          {estadoLabels[tarea.estado]}
        </span>
      </div>
      <div className="mt-3 flex items-center justify-between">
        <p className="text-xs text-on-surface-muted">ID: {tarea.id.slice(0, 8)}...</p>
        <button onClick={() => onOpen(tarea.id)} className="text-xs text-primary hover:underline">Ver detalle</button>
      </div>
    </div>
  )
}

export default function TareasPage() {
  const [view, setView] = useState<'mis-tareas' | 'admin'>('mis-tareas')
  const { data: tareas, isLoading } = useTareas()
  const { data: tareasAdmin } = useTareasAdmin()
  const crear = useCrearTarea()
  const actualizar = useActualizarTarea()
  const [showForm, setShowForm] = useState(false)
  const [descripcion, setDescripcion] = useState('')
  const [asignadoA, setAsignadoA] = useState('')
  const [materiaId, setMateriaId] = useState('')
  const [detailId, setDetailId] = useState<string | null>(null)
  const { data: comentarios } = useComentarios(detailId)
  const agregarComentario = useAgregarComentario()
  const [comentarioTexto, setComentarioTexto] = useState('')

  function handleCrear(e: React.FormEvent) {
    e.preventDefault()
    crear.mutate({ asignado_a: asignadoA, descripcion, materia_id: materiaId || null }, {
      onSuccess: () => { setShowForm(false); setDescripcion(''); setAsignadoA(''); setMateriaId('') },
    })
  }

  function handleCambiarEstado(id: string, estado: EstadoTarea) {
    actualizar.mutate({ id, data: { estado } })
  }

  function handleComentario(e: React.FormEvent) {
    e.preventDefault()
    if (!detailId || !comentarioTexto) return
    agregarComentario.mutate({ tareaId: detailId, data: { texto: comentarioTexto } }, {
      onSuccess: () => setComentarioTexto(''),
    })
  }

  const items = view === 'admin' ? tareasAdmin?.items : tareas?.items

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-primary">Tareas internas</h2>
        <div className="flex gap-3">
          <button
            onClick={() => setView(view === 'admin' ? 'mis-tareas' : 'admin')}
            className="rounded border border-border px-3 py-1.5 text-xs font-medium hover:bg-surface-hover"
          >
            {view === 'admin' ? 'Mis tareas' : 'Admin'}
          </button>
          <button
            onClick={() => setShowForm(!showForm)}
            className="rounded bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:bg-primary-hover"
          >
            {showForm ? 'Cancelar' : 'Nueva tarea'}
          </button>
        </div>
      </div>

      {showForm && (
        <form onSubmit={handleCrear} className="max-w-lg space-y-4 rounded-lg border border-border bg-surface p-6">
          <h3 className="text-sm font-semibold text-on-surface">Crear tarea</h3>
          <div>
            <label htmlFor="asignado-a" className="mb-1 block text-sm text-on-surface">Asignado a (usuario ID)</label>
            <input id="asignado-a" type="text" value={asignadoA} onChange={(e) => setAsignadoA(e.target.value)} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
          </div>
          <div>
            <label htmlFor="descripcion" className="mb-1 block text-sm text-on-surface">Descripción</label>
            <textarea id="descripcion" value={descripcion} onChange={(e) => setDescripcion(e.target.value)} required rows={3} className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
          </div>
          <div>
            <label htmlFor="materia-id" className="mb-1 block text-sm text-on-surface">Materia ID (opcional)</label>
            <input id="materia-id" type="text" value={materiaId} onChange={(e) => setMateriaId(e.target.value)} className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
          </div>
          <div className="flex justify-end gap-3">
            <button type="button" onClick={() => setShowForm(false)} className="rounded border border-border px-4 py-2 text-sm hover:bg-surface-hover">Cancelar</button>
            <button type="submit" disabled={crear.isPending} className="rounded bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:bg-primary-hover disabled:opacity-50">
              {crear.isPending ? 'Creando...' : 'Crear'}
            </button>
          </div>
          {crear.data && <p className="text-sm text-success">Tarea creada correctamente.</p>}
        </form>
      )}

      {detailId && (
        <div className="rounded-lg border border-border bg-surface p-6">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-on-surface">Detalle de tarea</h3>
            <button onClick={() => setDetailId(null)} className="text-xs text-on-surface-muted hover:text-on-surface">Cerrar</button>
          </div>
          <p className="mt-2 text-xs text-on-surface-muted">ID: {detailId}</p>
          <div className="mt-3 flex gap-2">
            {(['Pendiente', 'En progreso', 'Resuelta', 'Cancelada'] as EstadoTarea[]).map((estado) => (
              <button key={estado} onClick={() => handleCambiarEstado(detailId, estado)}
                className="rounded border border-border px-2 py-1 text-xs hover:bg-surface-hover"
              >{estadoLabels[estado]}</button>
            ))}
          </div>
          <div className="mt-4">
            <h4 className="mb-2 text-xs font-semibold text-on-surface-muted uppercase">Comentarios</h4>
            <div className="space-y-2">
              {comentarios?.map((c) => (
                <div key={c.id} className="rounded bg-surface px-3 py-2 text-sm">
                  <p className="text-xs text-on-surface-muted">{new Date(c.creado_at).toLocaleString()}</p>
                  <p className="text-on-surface">{c.texto}</p>
                </div>
              ))}
              {(!comentarios || comentarios.length === 0) && (
                <p className="text-xs text-on-surface-muted">Sin comentarios</p>
              )}
            </div>
            <form onSubmit={handleComentario} className="mt-3 flex gap-2">
              <input type="text" value={comentarioTexto} onChange={(e) => setComentarioTexto(e.target.value)} placeholder="Agregar comentario..." required className="flex-1 rounded border border-border bg-surface px-3 py-2 text-sm" />
              <button type="submit" disabled={agregarComentario.isPending} className="rounded bg-primary px-3 py-2 text-sm font-medium text-on-primary hover:bg-primary-hover disabled:opacity-50">Enviar</button>
            </form>
          </div>
        </div>
      )}

      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => <div key={i} className="h-24 animate-pulse rounded bg-border" />)}
        </div>
      ) : items && items.length > 0 ? (
        <div className="space-y-3">
          {items.map((t) => <TareaCard key={t.id} tarea={t} onOpen={(id) => setDetailId(id)} />)}
        </div>
      ) : (
        <p className="text-sm text-on-surface-muted">Sin tareas.</p>
      )}
    </div>
  )
}
