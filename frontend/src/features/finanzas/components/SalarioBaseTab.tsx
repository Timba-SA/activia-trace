import { useState } from 'react'
import { useCrearSalarioBase, useActualizarSalarioBase, useEliminarSalarioBase, useSalariosBase } from '../hooks/useFinanzas'

const emptyForm = { rol: '', monto: 0, desde: '', hasta: '' }

export default function SalarioBaseTab() {
  const salariosBase = useSalariosBase()
  const crear = useCrearSalarioBase()
  const actualizar = useActualizarSalarioBase()
  const eliminar = useEliminarSalarioBase()

  const [editId, setEditId] = useState<string | null>(null)
  const [form, setForm] = useState(emptyForm)

  function reset() {
    setForm(emptyForm)
    setEditId(null)
  }

  function handleEdit(item: { id: string; rol: string; monto: number; desde: string; hasta: string | null }) {
    setEditId(item.id)
    setForm({ rol: item.rol, monto: item.monto, desde: item.desde, hasta: item.hasta || '' })
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const data = { rol: form.rol, monto: form.monto, desde: form.desde, hasta: form.hasta || null }
    if (editId) {
      actualizar.mutate({ id: editId, data: { monto: data.monto, desde: data.desde, hasta: data.hasta } }, { onSuccess: reset })
    } else {
      crear.mutate(data, { onSuccess: reset })
    }
  }

  return (
    <div className="space-y-6">
      <form onSubmit={handleSubmit} className="max-w-lg space-y-4 rounded-lg border border-border bg-surface p-6">
        <h3 className="text-sm font-semibold text-on-surface">
          {editId ? 'Editar salario base' : 'Nuevo salario base'}
        </h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label htmlFor="sb-rol" className="mb-1 block text-sm text-on-surface">Rol</label>
            <input id="sb-rol" type="text" value={form.rol} onChange={(e) => setForm({ ...form, rol: e.target.value })} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
          </div>
          <div>
            <label htmlFor="sb-monto" className="mb-1 block text-sm text-on-surface">Monto</label>
            <input id="sb-monto" type="number" step="0.01" value={form.monto} onChange={(e) => setForm({ ...form, monto: parseFloat(e.target.value) || 0 })} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
          </div>
          <div>
            <label htmlFor="sb-desde" className="mb-1 block text-sm text-on-surface">Desde</label>
            <input id="sb-desde" type="date" value={form.desde} onChange={(e) => setForm({ ...form, desde: e.target.value })} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
          </div>
          <div>
            <label htmlFor="sb-hasta" className="mb-1 block text-sm text-on-surface">Hasta (opcional)</label>
            <input id="sb-hasta" type="date" value={form.hasta} onChange={(e) => setForm({ ...form, hasta: e.target.value })} className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
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
              <th className="px-4 py-3">Rol</th>
              <th className="px-4 py-3">Monto</th>
              <th className="px-4 py-3">Desde</th>
              <th className="px-4 py-3">Hasta</th>
              <th className="px-4 py-3">Acción</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {salariosBase.data?.map((sb) => (
              <tr key={sb.id} className="bg-surface hover:bg-surface-hover">
                <td className="px-4 py-3 text-on-surface">{sb.rol}</td>
                <td className="px-4 py-3 text-on-surface">${sb.monto.toFixed(2)}</td>
                <td className="px-4 py-3 text-on-surface">{sb.desde}</td>
                <td className="px-4 py-3 text-on-surface-muted">{sb.hasta || '—'}</td>
                <td className="px-4 py-3">
                  <div className="flex gap-2">
                    <button onClick={() => handleEdit(sb)} className="rounded border border-border px-2 py-1 text-xs hover:bg-surface-hover">Editar</button>
                    <button onClick={() => { if (window.confirm('¿Eliminar este salario base?')) eliminar.mutate(sb.id) }} className="rounded border border-danger px-2 py-1 text-xs text-danger hover:bg-danger/5">Eliminar</button>
                  </div>
                </td>
              </tr>
            ))}
            {(!salariosBase.data || salariosBase.data.length === 0) && (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-sm text-on-surface-muted">Sin salarios base.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
