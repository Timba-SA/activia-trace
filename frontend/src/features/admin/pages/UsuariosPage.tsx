import { useState } from 'react'
import { useUsuarios, useUsuario, useActualizarUsuario } from '../hooks/useAdmin'
import type { UsuarioUpdateRequest } from '../types'
import UsuarioDetalle from '../components/UsuarioDetalle'

export default function UsuariosPage() {
  const [filtros, setFiltros] = useState({ nombre: '', apellido: '', email: '', legajo: '', is_active: '' })
  const [expandido, setExpandido] = useState<string | null>(null)

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
    setExpandido(expandido === id ? null : id)
  }

  function handleEditSubmit(payload: UsuarioUpdateRequest) {
    if (!expandido) return
    actualizar.mutate({ id: expandido, data: payload })
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
            <UsuarioDetalle
              usuario={detalle.data}
              isPending={actualizar.isPending}
              onSubmit={handleEditSubmit}
              onClose={() => toggleExpand(expandido)}
            />
          ) : null}
        </div>
      )}
    </div>
  )
}
