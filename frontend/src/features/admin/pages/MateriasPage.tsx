import { useState } from 'react'
import { useMaterias, useCrearMateria, useActualizarMateria } from '../hooks/useAdmin'
import type { MateriaResponse, MateriaCreateRequest } from '../types'

type FormState = { open: boolean; editing: MateriaResponse | null; carrera_id: string; codigo: string; nombre: string; descripcion: string; carga_horaria: string }

const emptyForm = (overrides?: Partial<FormState>): FormState => ({
  open: false, editing: null, carrera_id: '', codigo: '', nombre: '', descripcion: '', carga_horaria: '', ...overrides,
})

export default function MateriasPage() {
  const [filtroCarrera, setFiltroCarrera] = useState('')
  const [form, setForm] = useState<FormState>(emptyForm())
  const { data, isLoading } = useMaterias({ carrera_id: filtroCarrera || undefined })
  const crear = useCrearMateria()
  const actualizar = useActualizarMateria()

  function reset() { setForm(emptyForm()) }

  function startEdit(m: MateriaResponse) {
    setForm({
      open: true, editing: m,
      carrera_id: m.carrera_id ?? '', codigo: m.codigo, nombre: m.nombre,
      descripcion: m.descripcion ?? '', carga_horaria: m.carga_horaria?.toString() ?? '',
    })
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!form.codigo.trim() || !form.nombre.trim()) return
    const payload: MateriaCreateRequest = {
      carrera_id: form.carrera_id.trim() || null,
      codigo: form.codigo.trim(),
      nombre: form.nombre.trim(),
      descripcion: form.descripcion.trim() || null,
      carga_horaria: form.carga_horaria ? Number(form.carga_horaria) : null,
    }
    if (form.editing) {
      actualizar.mutate({ id: form.editing.id, data: payload }, { onSuccess: reset })
    } else {
      crear.mutate(payload, { onSuccess: reset })
    }
  }

  function toggleActive(m: MateriaResponse) {
    actualizar.mutate({ id: m.id, data: { is_active: !m.is_active } })
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-primary">Materias</h2>
        <button
          onClick={() => setForm(emptyForm({ open: !form.open }))}
          className="rounded border border-primary px-3 py-1.5 text-xs font-medium text-primary hover:bg-primary hover:text-on-primary"
        >
          {form.open && !form.editing ? 'Cancelar' : 'Nueva materia'}
        </button>
      </div>

      <div>
        <label htmlFor="materia-filtro-carrera" className="text-label-sm block mb-1">Filtrar por carrera</label>
        <input id="materia-filtro-carrera" value={filtroCarrera} onChange={(e) => setFiltroCarrera(e.target.value)}
          placeholder="ID de carrera..."
          className="w-full max-w-xs rounded border border-border bg-surface px-3 py-2 text-sm" />
      </div>

      {form.open && (
        <form onSubmit={handleSubmit} className="space-y-3 rounded-lg border border-border bg-surface-container-lowest p-4">
          <div className="grid grid-cols-5 gap-3">
            <div>
              <label htmlFor="materia-carrera" className="text-label-sm block mb-1">Carrera ID</label>
              <input id="materia-carrera" value={form.carrera_id} onChange={(e) => setForm({ ...form, carrera_id: e.target.value })}
                className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
            <div>
              <label htmlFor="materia-codigo" className="text-label-sm block mb-1">Código</label>
              <input id="materia-codigo" value={form.codigo} onChange={(e) => setForm({ ...form, codigo: e.target.value })} required
                className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
            <div>
              <label htmlFor="materia-nombre" className="text-label-sm block mb-1">Nombre</label>
              <input id="materia-nombre" value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} required
                className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
            <div>
              <label htmlFor="materia-descripcion" className="text-label-sm block mb-1">Descripción</label>
              <input id="materia-descripcion" value={form.descripcion} onChange={(e) => setForm({ ...form, descripcion: e.target.value })}
                className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
            <div>
              <label htmlFor="materia-carga" className="text-label-sm block mb-1">Carga horaria</label>
              <input id="materia-carga" type="number" min={0} value={form.carga_horaria}
                onChange={(e) => setForm({ ...form, carga_horaria: e.target.value })}
                className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
          </div>
          <div className="flex gap-2">
            <button type="submit" disabled={crear.isPending || actualizar.isPending}
              className="rounded bg-primary px-4 py-1.5 text-xs font-medium text-on-primary hover:bg-primary-hover disabled:opacity-50">
              {form.editing ? 'Guardar cambios' : 'Crear materia'}
            </button>
            <button type="button" onClick={reset}
              className="rounded border border-border px-3 py-1.5 text-xs font-medium text-on-surface hover:bg-surface">
              Cancelar
            </button>
          </div>
        </form>
      )}

      {isLoading ? (
        <div className="h-32 animate-pulse rounded bg-border" />
      ) : data ? (
        <div className="overflow-x-auto rounded-lg border border-border">
          <table className="w-full text-sm">
            <thead className="bg-surface-container text-left">
              <tr>
                <th className="px-4 py-2 font-medium text-on-surface-variant">Carrera ID</th>
                <th className="px-4 py-2 font-medium text-on-surface-variant">Código</th>
                <th className="px-4 py-2 font-medium text-on-surface-variant">Nombre</th>
                <th className="px-4 py-2 font-medium text-on-surface-variant">Descripción</th>
                <th className="px-4 py-2 font-medium text-on-surface-variant">Carga horaria</th>
                <th className="px-4 py-2 font-medium text-on-surface-variant">Activa</th>
                <th className="px-4 py-2 font-medium text-on-surface-variant" />
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {data.items.map((m) => (
                <tr key={m.id} className="hover:bg-surface-hover">
                  <td className="px-4 py-2 font-mono text-xs text-on-surface-variant">{m.carrera_id ?? '—'}</td>
                  <td className="px-4 py-2 font-mono text-xs text-on-surface-variant">{m.codigo}</td>
                  <td className="px-4 py-2 text-on-surface">{m.nombre}</td>
                  <td className="px-4 py-2 text-on-surface-variant">{m.descripcion ?? '—'}</td>
                  <td className="px-4 py-2 text-on-surface-variant">{m.carga_horaria ?? '—'}</td>
                  <td className="px-4 py-2">
                    <button onClick={() => toggleActive(m)}
                      className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${m.is_active ? 'bg-success/10 text-success' : 'bg-error/10 text-error'}`}>
                      {m.is_active ? 'Sí' : 'No'}
                    </button>
                  </td>
                  <td className="px-4 py-2 text-right">
                    <button onClick={() => startEdit(m)}
                      className="text-xs font-medium text-primary hover:underline">Editar</button>
                  </td>
                </tr>
              ))}
              {data.items.length === 0 && (
                <tr><td colSpan={7} className="px-4 py-8 text-center text-sm text-on-surface-muted">Sin materias</td></tr>
              )}
            </tbody>
          </table>
        </div>
      ) : null}
    </div>
  )
}
