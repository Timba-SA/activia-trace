import { useState } from 'react'
import { useCarreras, useCrearCarrera, useActualizarCarrera } from '../hooks/useAdmin'
import type { CarreraResponse, CarreraCreateRequest } from '../types'

type FormState = { open: boolean; editing: CarreraResponse | null; nombre: string; codigo: string; descripcion: string; duracion_anios: string }

const emptyForm = (overrides?: Partial<FormState>): FormState => ({
  open: false, editing: null, nombre: '', codigo: '', descripcion: '', duracion_anios: '', ...overrides,
})

export default function CarrerasPage() {
  const [form, setForm] = useState<FormState>(emptyForm())
  const { data, isLoading } = useCarreras()
  const crear = useCrearCarrera()
  const actualizar = useActualizarCarrera()

  function reset() { setForm(emptyForm()) }

  function startEdit(c: CarreraResponse) {
    setForm({
      open: true, editing: c,
      nombre: c.nombre, codigo: c.codigo,
      descripcion: c.descripcion ?? '',
      duracion_anios: c.duracion_anios?.toString() ?? '',
    })
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!form.nombre.trim() || !form.codigo.trim()) return
    const payload: CarreraCreateRequest = {
      nombre: form.nombre.trim(),
      codigo: form.codigo.trim(),
      descripcion: form.descripcion.trim() || null,
      duracion_anios: form.duracion_anios ? Number(form.duracion_anios) : null,
    }
    if (form.editing) {
      actualizar.mutate({ id: form.editing.id, data: payload }, { onSuccess: reset })
    } else {
      crear.mutate(payload, { onSuccess: reset })
    }
  }

  function toggleActive(c: CarreraResponse) {
    actualizar.mutate({ id: c.id, data: { is_active: !c.is_active } })
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-primary">Carreras</h2>
        <button
          onClick={() => setForm(emptyForm({ open: !form.open }))}
          className="rounded border border-primary px-3 py-1.5 text-xs font-medium text-primary hover:bg-primary hover:text-on-primary"
        >
          {form.open && !form.editing ? 'Cancelar' : 'Nueva carrera'}
        </button>
      </div>

      {form.open && (
        <form onSubmit={handleSubmit} className="space-y-3 rounded-lg border border-border bg-surface-container-lowest p-4">
          <div className="grid grid-cols-4 gap-3">
            <div>
              <label htmlFor="carrera-nombre" className="text-label-sm block mb-1">Nombre</label>
              <input id="carrera-nombre" value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} required
                className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
            <div>
              <label htmlFor="carrera-codigo" className="text-label-sm block mb-1">Código</label>
              <input id="carrera-codigo" value={form.codigo} onChange={(e) => setForm({ ...form, codigo: e.target.value })} required
                className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
            <div>
              <label htmlFor="carrera-descripcion" className="text-label-sm block mb-1">Descripción</label>
              <input id="carrera-descripcion" value={form.descripcion} onChange={(e) => setForm({ ...form, descripcion: e.target.value })}
                className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
            <div>
              <label htmlFor="carrera-duracion" className="text-label-sm block mb-1">Duración (años)</label>
              <input id="carrera-duracion" type="number" min={1} value={form.duracion_anios}
                onChange={(e) => setForm({ ...form, duracion_anios: e.target.value })}
                className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
          </div>
          <div className="flex gap-2">
            <button type="submit" disabled={crear.isPending || actualizar.isPending}
              className="rounded bg-primary px-4 py-1.5 text-xs font-medium text-on-primary hover:bg-primary-hover disabled:opacity-50">
              {form.editing ? 'Guardar cambios' : 'Crear carrera'}
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
                <th className="px-4 py-2 font-medium text-on-surface-variant">Nombre</th>
                <th className="px-4 py-2 font-medium text-on-surface-variant">Código</th>
                <th className="px-4 py-2 font-medium text-on-surface-variant">Descripción</th>
                <th className="px-4 py-2 font-medium text-on-surface-variant">Duración</th>
                <th className="px-4 py-2 font-medium text-on-surface-variant">Activa</th>
                <th className="px-4 py-2 font-medium text-on-surface-variant" />
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {data.items.map((c) => (
                <tr key={c.id} className="hover:bg-surface-hover">
                  <td className="px-4 py-2 text-on-surface">{c.nombre}</td>
                  <td className="px-4 py-2 font-mono text-xs text-on-surface-variant">{c.codigo}</td>
                  <td className="px-4 py-2 text-on-surface-variant">{c.descripcion ?? '—'}</td>
                  <td className="px-4 py-2 text-on-surface-variant">{c.duracion_anios ?? '—'}</td>
                  <td className="px-4 py-2">
                    <button onClick={() => toggleActive(c)}
                      className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${c.is_active ? 'bg-success/10 text-success' : 'bg-error/10 text-error'}`}>
                      {c.is_active ? 'Sí' : 'No'}
                    </button>
                  </td>
                  <td className="px-4 py-2 text-right">
                    <button onClick={() => startEdit(c)}
                      className="text-xs font-medium text-primary hover:underline">Editar</button>
                  </td>
                </tr>
              ))}
              {data.items.length === 0 && (
                <tr><td colSpan={6} className="px-4 py-8 text-center text-sm text-on-surface-muted">Sin carreras</td></tr>
              )}
            </tbody>
          </table>
        </div>
      ) : null}
    </div>
  )
}
