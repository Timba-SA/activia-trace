import { useState } from 'react'
import { useCrearSalarioPlus, useActualizarSalarioPlus, useEliminarSalarioPlus, useSalariosPlus } from '../hooks/useFinanzas'

const emptyForm = { grupo: '', rol: '', descripcion: '', monto: 0, tope_acumulacion: 0, desde: '', hasta: '' }

export default function SalarioPlusTab() {
  const salariosPlus = useSalariosPlus()
  const crear = useCrearSalarioPlus()
  const actualizar = useActualizarSalarioPlus()
  const eliminar = useEliminarSalarioPlus()

  const [editId, setEditId] = useState<string | null>(null)
  const [form, setForm] = useState(emptyForm)

  function reset() {
    setForm(emptyForm)
    setEditId(null)
  }

  function handleEdit(item: { id: string; grupo: string; rol: string; descripcion: string | null; monto: number; tope_acumulacion: number | null; desde: string; hasta: string | null }) {
    setEditId(item.id)
    setForm({
      grupo: item.grupo, rol: item.rol, descripcion: item.descripcion || '',
      monto: item.monto, tope_acumulacion: item.tope_acumulacion || 0,
      desde: item.desde, hasta: item.hasta || '',
    })
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (editId) {
      actualizar.mutate({
        id: editId,
        data: {
          grupo: form.grupo, rol: form.rol,
          descripcion: form.descripcion || undefined,
          monto: form.monto,
          tope_acumulacion: form.tope_acumulacion || null,
          desde: form.desde, hasta: form.hasta || null,
        },
      }, { onSuccess: reset })
    } else {
      crear.mutate({
        grupo: form.grupo, rol: form.rol,
        descripcion: form.descripcion || null,
        monto: form.monto,
        tope_acumulacion: form.tope_acumulacion || null,
        desde: form.desde, hasta: form.hasta || null,
      }, { onSuccess: reset })
    }
  }

  return (
    <div className="space-y-6">
      <form onSubmit={handleSubmit} className="max-w-lg space-y-4 rounded-lg border border-border bg-surface p-6">
        <h3 className="text-sm font-semibold text-on-surface">
          {editId ? 'Editar salario plus' : 'Nuevo salario plus'}
        </h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label htmlFor="sp-grupo" className="mb-1 block text-sm text-on-surface">Grupo</label>
            <input id="sp-grupo" type="text" value={form.grupo} onChange={(e) => setForm({ ...form, grupo: e.target.value })} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
          </div>
          <div>
            <label htmlFor="sp-rol" className="mb-1 block text-sm text-on-surface">Rol</label>
            <select id="sp-rol" value={form.rol} onChange={(e) => setForm({ ...form, rol: e.target.value })} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm">
              <option value="">Seleccionar rol</option>
              {['TUTOR', 'PROFESOR', 'COORDINADOR', 'NEXO', 'ADMIN', 'FINANZAS'].map(r => <option key={r} value={r}>{r}</option>)}
            </select>
          </div>
          <div className="col-span-2">
            <label htmlFor="sp-desc" className="mb-1 block text-sm text-on-surface">Descripción (opcional)</label>
            <input id="sp-desc" type="text" value={form.descripcion} onChange={(e) => setForm({ ...form, descripcion: e.target.value })} className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
          </div>
          <div>
            <label htmlFor="sp-monto" className="mb-1 block text-sm text-on-surface">Monto</label>
            <input id="sp-monto" type="number" step="0.01" value={form.monto} onChange={(e) => setForm({ ...form, monto: parseFloat(e.target.value) || 0 })} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
          </div>
          <div>
            <label htmlFor="sp-tope" className="mb-1 block text-sm text-on-surface">Tope acumulación</label>
            <input id="sp-tope" type="number" step="0.01" value={form.tope_acumulacion} onChange={(e) => setForm({ ...form, tope_acumulacion: parseFloat(e.target.value) || 0 })} className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
          </div>
          <div>
            <label htmlFor="sp-desde" className="mb-1 block text-sm text-on-surface">Desde</label>
            <input id="sp-desde" type="date" value={form.desde} onChange={(e) => setForm({ ...form, desde: e.target.value })} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
          </div>
          <div>
            <label htmlFor="sp-hasta" className="mb-1 block text-sm text-on-surface">Hasta (opcional)</label>
            <input id="sp-hasta" type="date" value={form.hasta} onChange={(e) => setForm({ ...form, hasta: e.target.value })} className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
          </div>
        </div>
        <div className="flex justify-end gap-3">
          {editId && (
            <button type="button" onClick={reset} className="rounded border border-border px-4 py-2 text-sm hover:bg-surface-hover">Cancelar</button>
          )}
          <button type="submit" disabled={crear.isPending || actualizar.isPending} className="rounded bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:bg-primary-hover disabled:opacity-50">
            {editId ? 'Actualizar' : 'Crear'}
          </button>
        </div>
      </form>

      <div className="overflow-x-auto rounded-lg border border-border">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-surface-hover text-left text-xs font-medium text-on-surface-muted uppercase">
              <th className="px-4 py-3">Grupo</th>
              <th className="px-4 py-3">Rol</th>
              <th className="px-4 py-3">Descripción</th>
              <th className="px-4 py-3">Monto</th>
              <th className="px-4 py-3">Tope</th>
              <th className="px-4 py-3">Desde</th>
              <th className="px-4 py-3">Hasta</th>
              <th className="px-4 py-3">Acción</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {salariosPlus.data?.map((sp) => (
              <tr key={sp.id} className="bg-surface hover:bg-surface-hover">
                <td className="px-4 py-3 text-on-surface">{sp.grupo}</td>
                <td className="px-4 py-3 text-on-surface">{sp.rol}</td>
                <td className="px-4 py-3 text-on-surface-muted">{sp.descripcion || '—'}</td>
                <td className="px-4 py-3 text-on-surface">${sp.monto.toFixed(2)}</td>
                <td className="px-4 py-3 text-on-surface">{sp.tope_acumulacion ? `$${sp.tope_acumulacion.toFixed(2)}` : '—'}</td>
                <td className="px-4 py-3 text-on-surface">{sp.desde}</td>
                <td className="px-4 py-3 text-on-surface-muted">{sp.hasta || '—'}</td>
                <td className="px-4 py-3">
                  <div className="flex gap-2">
                    <button onClick={() => handleEdit(sp)} className="rounded border border-border px-2 py-1 text-xs hover:bg-surface-hover">Editar</button>
                    <button onClick={() => { if (window.confirm('¿Eliminar este salario plus?')) eliminar.mutate(sp.id) }} className="rounded border border-danger px-2 py-1 text-xs text-danger hover:bg-danger/5">Eliminar</button>
                  </div>
                </td>
              </tr>
            ))}
            {(!salariosPlus.data || salariosPlus.data.length === 0) && (
              <tr>
                <td colSpan={8} className="px-4 py-8 text-center text-sm text-on-surface-muted">Sin salarios plus.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
