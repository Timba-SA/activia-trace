import { useState } from 'react'
import type { UsuarioDetalleResponse, UsuarioUpdateRequest } from '../types'

interface Props {
  usuario: UsuarioDetalleResponse
  isPending: boolean
  onSubmit: (payload: UsuarioUpdateRequest) => void
  onClose: () => void
}

interface EditState {
  nombre: string
  apellido: string
  email: string
  telefono: string
  is_active: boolean
}

export default function UsuarioDetalle({ usuario, isPending, onSubmit, onClose }: Props) {
  const [editing, setEditing] = useState(false)
  const [form, setForm] = useState<EditState>({
    nombre: '',
    apellido: '',
    email: '',
    telefono: '',
    is_active: false,
  })

  function startEdit() {
    setForm({
      nombre: usuario.nombre,
      apellido: usuario.apellido,
      email: usuario.email,
      telefono: usuario.telefono ?? '',
      is_active: usuario.is_active,
    })
    setEditing(true)
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    onSubmit({
      nombre: form.nombre.trim() || undefined,
      apellido: form.apellido.trim() || undefined,
      email: form.email.trim() || undefined,
      telefono: form.telefono.trim() || undefined,
      is_active: form.is_active,
    })
    setEditing(false)
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-on-surface">Detalle del usuario</h3>
        <div className="flex gap-2">
          {!editing && (
            <button onClick={startEdit}
              className="rounded border border-primary px-3 py-1 text-xs font-medium text-primary hover:bg-primary hover:text-on-primary">
              Editar
            </button>
          )}
          <button onClick={onClose}
            className="text-xs font-medium text-on-surface-muted hover:text-on-surface">Cerrar</button>
        </div>
      </div>

      {!editing ? (
        <div className="grid grid-cols-2 gap-x-6 gap-y-3 text-sm">
          <div><span className="text-label-sm text-on-surface-variant">Nombre:</span><p className="text-on-surface">{usuario.nombre}</p></div>
          <div><span className="text-label-sm text-on-surface-variant">Apellido:</span><p className="text-on-surface">{usuario.apellido}</p></div>
          <div><span className="text-label-sm text-on-surface-variant">Email:</span><p className="text-on-surface">{usuario.email}</p></div>
          <div><span className="text-label-sm text-on-surface-variant">Legajo:</span><p className="text-on-surface">{usuario.legajo}</p></div>
          <div><span className="text-label-sm text-on-surface-variant">CUIL:</span><p className="text-on-surface">{usuario.cuil ?? '—'}</p></div>
          <div><span className="text-label-sm text-on-surface-variant">DNI:</span><p className="text-on-surface">{usuario.dni ?? '—'}</p></div>
          <div><span className="text-label-sm text-on-surface-variant">Teléfono:</span><p className="text-on-surface">{usuario.telefono ?? '—'}</p></div>
          <div><span className="text-label-sm text-on-surface-variant">Roles:</span><p className="text-on-surface">{(usuario.roles ?? []).join(', ') || '—'}</p></div>
          <div>
            <span className="text-label-sm text-on-surface-variant">Activo:</span>
            <span className={`ml-1 rounded-full px-2 py-0.5 text-xs font-medium ${usuario.is_active ? 'bg-success/10 text-success' : 'bg-error/10 text-error'}`}>
              {usuario.is_active ? 'Sí' : 'No'}
            </span>
          </div>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label htmlFor="edit-nombre" className="text-label-sm block mb-1">Nombre</label>
              <input id="edit-nombre" value={form.nombre}
                onChange={(e) => setForm({ ...form, nombre: e.target.value })}
                className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
            <div>
              <label htmlFor="edit-apellido" className="text-label-sm block mb-1">Apellido</label>
              <input id="edit-apellido" value={form.apellido}
                onChange={(e) => setForm({ ...form, apellido: e.target.value })}
                className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
            <div>
              <label htmlFor="edit-email" className="text-label-sm block mb-1">Email</label>
              <input id="edit-email" type="email" value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
            <div>
              <label htmlFor="edit-telefono" className="text-label-sm block mb-1">Teléfono</label>
              <input id="edit-telefono" value={form.telefono}
                onChange={(e) => setForm({ ...form, telefono: e.target.value })}
                className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
            <div className="flex items-center gap-2">
              <input id="edit-is-active" type="checkbox" checked={form.is_active}
                onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
                className="rounded border-border" />
              <label htmlFor="edit-is-active" className="text-sm text-on-surface">Activo</label>
            </div>
          </div>
          <div className="flex gap-2">
            <button type="submit" disabled={isPending}
              className="rounded bg-primary px-4 py-1.5 text-xs font-medium text-on-primary hover:bg-primary-hover disabled:opacity-50">
              Guardar cambios
            </button>
            <button type="button" onClick={() => setEditing(false)}
              className="rounded border border-border px-3 py-1.5 text-xs font-medium text-on-surface hover:bg-surface">
              Cancelar
            </button>
          </div>
        </form>
      )}
    </div>
  )
}
