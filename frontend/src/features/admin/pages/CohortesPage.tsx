import { useState } from 'react'
import { useCohortes, useCrearCohorte, useActualizarCohorte, useCarreras } from '../hooks/useAdmin'
import type { CohorteResponse, CohorteCreateRequest } from '../types'

type FormState = { open: boolean; editing: CohorteResponse | null; carrera_id: string; nombre: string; anio: string }

const emptyForm = (overrides?: Partial<FormState>): FormState => ({
  open: false, editing: null, carrera_id: '', nombre: '', anio: new Date().getFullYear().toString(), ...overrides,
})

export default function CohortesPage() {
  const [filtroCarrera, setFiltroCarrera] = useState('')
  const [form, setForm] = useState<FormState>(emptyForm())
  const { data, isLoading } = useCohortes({ carrera_id: filtroCarrera || undefined })
  const { data: carreras } = useCarreras({ limit: 100 })
  const crear = useCrearCohorte()
  const actualizar = useActualizarCohorte()

  function reset() { setForm(emptyForm()) }

  function startEdit(c: CohorteResponse) {
    setForm({
      open: true, editing: c,
      carrera_id: c.carrera_id, nombre: c.nombre, anio: c.anio.toString(),
    })
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!form.carrera_id.trim() || !form.nombre.trim() || !form.anio) return
    const payload: CohorteCreateRequest = {
      carrera_id: form.carrera_id.trim(),
      nombre: form.nombre.trim(),
      anio: Number(form.anio),
    }
    if (form.editing) {
      actualizar.mutate({ id: form.editing.id, data: payload }, { onSuccess: reset })
    } else {
      crear.mutate(payload, { onSuccess: reset })
    }
  }

  function toggleActive(c: CohorteResponse) {
    actualizar.mutate({ id: c.id, data: { is_active: !c.is_active } })
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-primary">Cohortes</h2>
        <button
          onClick={() => setForm(emptyForm({ open: !form.open }))}
          className="rounded border border-primary px-3 py-1.5 text-xs font-medium text-primary hover:bg-primary hover:text-on-primary"
        >
          {form.open && !form.editing ? 'Cancelar' : 'Nuevo cohorte'}
        </button>
      </div>

      <div>
        <label htmlFor="cohorte-filtro-carrera" className="text-label-sm block mb-1">Filtrar por carrera</label>
        <select id="cohorte-filtro-carrera" value={filtroCarrera} onChange={(e) => setFiltroCarrera(e.target.value)}
          className="w-full max-w-xs rounded border border-border bg-surface px-3 py-2 text-sm">
          <option value="">Todas las carreras</option>
          {carreras?.items.map(c => <option key={c.id} value={c.id}>{c.nombre} ({c.codigo})</option>)}
        </select>
      </div>

      {form.open && (
        <form onSubmit={handleSubmit} className="space-y-3 rounded-lg border border-border bg-surface-container-lowest p-4">
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label htmlFor="cohorte-carrera" className="text-label-sm block mb-1">Carrera</label>
              <select id="cohorte-carrera" value={form.carrera_id} onChange={(e) => setForm({ ...form, carrera_id: e.target.value })} required
                className="w-full rounded border border-border bg-surface px-3 py-2 text-sm">
                <option value="">Seleccionar carrera</option>
                {carreras?.items.map(c => <option key={c.id} value={c.id}>{c.nombre} ({c.codigo})</option>)}
              </select>
            </div>
            <div>
              <label htmlFor="cohorte-nombre" className="text-label-sm block mb-1">Nombre</label>
              <input id="cohorte-nombre" value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} required
                className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
            <div>
              <label htmlFor="cohorte-anio" className="text-label-sm block mb-1">Año</label>
              <input id="cohorte-anio" type="number" min={2000} max={2100} value={form.anio}
                onChange={(e) => setForm({ ...form, anio: e.target.value })} required
                className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
          </div>
          <div className="flex gap-2">
            <button type="submit" disabled={crear.isPending || actualizar.isPending}
              className="rounded bg-primary px-4 py-1.5 text-xs font-medium text-on-primary hover:bg-primary-hover disabled:opacity-50">
              {form.editing ? 'Guardar cambios' : 'Crear cohorte'}
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
                <th className="px-4 py-2 font-medium text-on-surface-variant">Carrera</th>
                <th className="px-4 py-2 font-medium text-on-surface-variant">Nombre</th>
                <th className="px-4 py-2 font-medium text-on-surface-variant">Año</th>
                <th className="px-4 py-2 font-medium text-on-surface-variant">Activo</th>
                <th className="px-4 py-2 font-medium text-on-surface-variant" />
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {data.items.map((c) => (
                <tr key={c.id} className="hover:bg-surface-hover">
                  <td className="px-4 py-2 text-xs text-on-surface-variant">{carreras?.items.find(car => car.id === c.carrera_id)?.nombre ?? c.carrera_id.slice(0, 8) + '…'}</td>
                  <td className="px-4 py-2 text-on-surface">{c.nombre}</td>
                  <td className="px-4 py-2 text-on-surface-variant">{c.anio}</td>
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
                <tr><td colSpan={5} className="px-4 py-8 text-center text-sm text-on-surface-muted">Sin cohortes</td></tr>
              )}
            </tbody>
          </table>
        </div>
      ) : null}
    </div>
  )
}
