import { useState } from 'react'
import { useUsuarios, useUsuario, useActualizarUsuario } from '../hooks/useAdmin'
import type { UsuarioDetalleResponse, UsuarioUpdateRequest } from '../types'

export default function UsuariosPage() {
  const [filtros, setFiltros] = useState({ nombre: '', apellido: '', email: '', legajo: '', is_active: '' })
  const [expandido, setExpandido] = useState<string | null>(null)
  const [editForm, setEditForm] = useState<{ open: boolean; nombre: string; apellido: string; email: string; telefono: string; is_active: boolean }>({ open: false, nombre: '', apellido: '', email: '', telefono: '', is_active: false })

  const { data, isLoading } = useUsuarios({
    nombre: filtros.nombre || undefined,
    apellido: filtros.apellido || undefined,
    email: filtros.email || undefined,
    legajo: filtros.legajo || undefined,
    is_active: filtros.is_active === '' ? undefined : filtros.is_active === 'true',
  })
  const detalle = useUsuario(expandido)
  const actualizar = useActualizarUsuario()

  function toggleExpand(id: string) {
    if (expandido === id) {
      setExpandido(null)
      setEditForm({ ...editForm, open: false })
    } else {
      setExpandido(id)
      setEditForm({ open: false, nombre: '', apellido: '', email: '', telefono: '', is_active: false })
    }
  }

  function startEdit(u: UsuarioDetalleResponse) {
    setEditForm({
      open: true,
      nombre: u.nombre,
      apellido: u.apellido,
      email: u.email,
      telefono: u.telefono ?? '',
      is_active: u.is_active,
    })
  }

  function cancelEdit() { setEditForm({ ...editForm, open: false }) }

  function handleEditSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!expandido) return
    const payload: UsuarioUpdateRequest = {
      nombre: editForm.nombre.trim() || undefined,
      apellido: editForm.apellido.trim() || undefined,
      email: editForm.email.trim() || undefined,
      telefono: editForm.telefono.trim() || undefined,
      is_active: editForm.is_active,
    }
    actualizar.mutate({ id: expandido, data: payload }, { onSuccess: () => cancelEdit() })
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-primary">Usuarios</h2>
      </div>

      <div className="flex flex-wrap gap-3">
        <div>
          <label htmlFor="usr-nombre" className="text-label-sm block mb-1">Nombre</label>
          <input id="usr-nombre" value={filtros.nombre} onChange={(e) => setFiltros({ ...filtros, nombre: e.target.value })}
            className="w-40 rounded border border-border bg-surface px-3 py-2 text-sm" />
        </div>
        <div>
          <label htmlFor="usr-apellido" className="text-label-sm block mb-1">Apellido</label>
          <input id="usr-apellido" value={filtros.apellido} onChange={(e) => setFiltros({ ...filtros, apellido: e.target.value })}
            className="w-40 rounded border border-border bg-surface px-3 py-2 text-sm" />
        </div>
        <div>
          <label htmlFor="usr-email" className="text-label-sm block mb-1">Email</label>
          <input id="usr-email" value={filtros.email} onChange={(e) => setFiltros({ ...filtros, email: e.target.value })}
            className="w-48 rounded border border-border bg-surface px-3 py-2 text-sm" />
        </div>
        <div>
          <label htmlFor="usr-legajo" className="text-label-sm block mb-1">Legajo</label>
          <input id="usr-legajo" value={filtros.legajo} onChange={(e) => setFiltros({ ...filtros, legajo: e.target.value })}
            className="w-32 rounded border border-border bg-surface px-3 py-2 text-sm" />
        </div>
        <div>
          <label htmlFor="usr-activo" className="text-label-sm block mb-1">Activo</label>
          <select id="usr-activo" value={filtros.is_active} onChange={(e) => setFiltros({ ...filtros, is_active: e.target.value })}
            className="rounded border border-border bg-surface px-3 py-2 text-sm">
            <option value="">Todos</option>
            <option value="true">Sí</option>
            <option value="false">No</option>
          </select>
        </div>
      </div>

      {isLoading ? (
        <div className="h-32 animate-pulse rounded bg-border" />
      ) : data ? (
        <div className="overflow-x-auto rounded-lg border border-border">
          <table className="w-full text-sm">
            <thead className="bg-surface-container text-left">
              <tr>
                <th className="px-4 py-2 font-medium text-on-surface-variant">Nombre</th>
                <th className="px-4 py-2 font-medium text-on-surface-variant">Apellido</th>
                <th className="px-4 py-2 font-medium text-on-surface-variant">Email</th>
                <th className="px-4 py-2 font-medium text-on-surface-variant">Legajo</th>
                <th className="px-4 py-2 font-medium text-on-surface-variant">Activo</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {data.items.map((u) => (
                <tr key={u.id} className="hover:bg-surface-hover cursor-pointer" onClick={() => toggleExpand(u.id)}>
                  <td className="px-4 py-2 text-on-surface">{u.nombre}</td>
                  <td className="px-4 py-2 text-on-surface">{u.apellido}</td>
                  <td className="px-4 py-2 text-on-surface-variant">{u.email}</td>
                  <td className="px-4 py-2 font-mono text-xs text-on-surface-variant">{u.legajo}</td>
                  <td className="px-4 py-2">
                    <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${u.is_active ? 'bg-success/10 text-success' : 'bg-error/10 text-error'}`}>
                      {u.is_active ? 'Sí' : 'No'}
                    </span>
                  </td>
                </tr>
              ))}
              {data.items.length === 0 && (
                <tr><td colSpan={5} className="px-4 py-8 text-center text-sm text-on-surface-muted">Sin usuarios</td></tr>
              )}
            </tbody>
          </table>
        </div>
      ) : null}

      {expandido && (
        <div className="rounded-lg border border-border bg-surface-container-lowest p-4">
          {detalle.isLoading ? (
            <div className="h-20 animate-pulse rounded bg-border" />
          ) : detalle.data ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-on-surface">Detalle del usuario</h3>
                <div className="flex gap-2">
                  {!editForm.open && (
                    <button onClick={() => startEdit(detalle.data!)}
                      className="rounded border border-primary px-3 py-1 text-xs font-medium text-primary hover:bg-primary hover:text-on-primary">
                      Editar
                    </button>
                  )}
                  <button onClick={() => toggleExpand(expandido)}
                    className="text-xs font-medium text-on-surface-muted hover:text-on-surface">Cerrar</button>
                </div>
              </div>

              {!editForm.open ? (
                <div className="grid grid-cols-2 gap-x-6 gap-y-3 text-sm">
                  <div><span className="text-label-sm text-on-surface-variant">Nombre:</span><p className="text-on-surface">{detalle.data.nombre}</p></div>
                  <div><span className="text-label-sm text-on-surface-variant">Apellido:</span><p className="text-on-surface">{detalle.data.apellido}</p></div>
                  <div><span className="text-label-sm text-on-surface-variant">Email:</span><p className="text-on-surface">{detalle.data.email}</p></div>
                  <div><span className="text-label-sm text-on-surface-variant">Legajo:</span><p className="text-on-surface">{detalle.data.legajo}</p></div>
                  <div><span className="text-label-sm text-on-surface-variant">CUIL:</span><p className="text-on-surface">{detalle.data.cuil ?? '—'}</p></div>
                  <div><span className="text-label-sm text-on-surface-variant">DNI:</span><p className="text-on-surface">{detalle.data.dni ?? '—'}</p></div>
                  <div><span className="text-label-sm text-on-surface-variant">Teléfono:</span><p className="text-on-surface">{detalle.data.telefono ?? '—'}</p></div>
                  <div><span className="text-label-sm text-on-surface-variant">Roles:</span><p className="text-on-surface">{(detalle.data.roles ?? []).join(', ') || '—'}</p></div>
                  <div><span className="text-label-sm text-on-surface-variant">Activo:</span>
                    <span className={`ml-1 rounded-full px-2 py-0.5 text-xs font-medium ${detalle.data.is_active ? 'bg-success/10 text-success' : 'bg-error/10 text-error'}`}>
                      {detalle.data.is_active ? 'Sí' : 'No'}
                    </span>
                  </div>
                </div>
              ) : (
                <form onSubmit={handleEditSubmit} className="space-y-3">
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label htmlFor="edit-nombre" className="text-label-sm block mb-1">Nombre</label>
                      <input id="edit-nombre" value={editForm.nombre}
                        onChange={(e) => setEditForm({ ...editForm, nombre: e.target.value })}
                        className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
                    </div>
                    <div>
                      <label htmlFor="edit-apellido" className="text-label-sm block mb-1">Apellido</label>
                      <input id="edit-apellido" value={editForm.apellido}
                        onChange={(e) => setEditForm({ ...editForm, apellido: e.target.value })}
                        className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
                    </div>
                    <div>
                      <label htmlFor="edit-email" className="text-label-sm block mb-1">Email</label>
                      <input id="edit-email" type="email" value={editForm.email}
                        onChange={(e) => setEditForm({ ...editForm, email: e.target.value })}
                        className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
                    </div>
                    <div>
                      <label htmlFor="edit-telefono" className="text-label-sm block mb-1">Teléfono</label>
                      <input id="edit-telefono" value={editForm.telefono}
                        onChange={(e) => setEditForm({ ...editForm, telefono: e.target.value })}
                        className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
                    </div>
                    <div className="flex items-center gap-2">
                      <input id="edit-is-active" type="checkbox" checked={editForm.is_active}
                        onChange={(e) => setEditForm({ ...editForm, is_active: e.target.checked })}
                        className="rounded border-border" />
                      <label htmlFor="edit-is-active" className="text-sm text-on-surface">Activo</label>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button type="submit" disabled={actualizar.isPending}
                      className="rounded bg-primary px-4 py-1.5 text-xs font-medium text-on-primary hover:bg-primary-hover disabled:opacity-50">
                      Guardar cambios
                    </button>
                    <button type="button" onClick={cancelEdit}
                      className="rounded border border-border px-3 py-1.5 text-xs font-medium text-on-surface hover:bg-surface">
                      Cancelar
                    </button>
                  </div>
                </form>
              )}
            </div>
          ) : null}
        </div>
      )}
    </div>
  )
}
