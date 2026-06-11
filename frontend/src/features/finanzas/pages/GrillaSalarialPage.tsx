import { useState } from 'react'
import { useSalariosBase, useCrearSalarioBase, useActualizarSalarioBase, useEliminarSalarioBase, useSalariosPlus, useCrearSalarioPlus, useActualizarSalarioPlus, useEliminarSalarioPlus } from '../hooks/useFinanzas'

type Tab = 'base' | 'plus' | 'materia-grupo'

const emptyBase = { rol: '', monto: 0, desde: '', hasta: '' }
const emptyPlus = { grupo: '', rol: '', descripcion: '', monto: 0, tope_acumulacion: 0, desde: '', hasta: '' }

export default function GrillaSalarialPage() {
  const [tab, setTab] = useState<Tab>('base')
  const [editId, setEditId] = useState<string | null>(null)

  const salariosBase = useSalariosBase()
  const crearBase = useCrearSalarioBase()
  const actualizarBase = useActualizarSalarioBase()
  const eliminarBase = useEliminarSalarioBase()

  const salariosPlus = useSalariosPlus()
  const crearPlus = useCrearSalarioPlus()
  const actualizarPlus = useActualizarSalarioPlus()
  const eliminarPlus = useEliminarSalarioPlus()

  const [baseForm, setBaseForm] = useState(emptyBase)
  const [plusForm, setPlusForm] = useState(emptyPlus)

  function resetBaseForm() {
    setBaseForm(emptyBase)
    setEditId(null)
  }

  function resetPlusForm() {
    setPlusForm(emptyPlus)
    setEditId(null)
  }

  function handleCreateBase(e: React.FormEvent) {
    e.preventDefault()
    const data = { rol: baseForm.rol, monto: baseForm.monto, desde: baseForm.desde, hasta: baseForm.hasta || null }
    if (editId) {
      actualizarBase.mutate({ id: editId, data: { monto: data.monto, desde: data.desde, hasta: data.hasta } }, { onSuccess: resetBaseForm })
    } else {
      crearBase.mutate(data as any, { onSuccess: resetBaseForm })
    }
  }

  function handleEditBase(item: { id: string; rol: string; monto: number; desde: string; hasta: string | null }) {
    setEditId(item.id)
    setBaseForm({ rol: item.rol, monto: item.monto, desde: item.desde, hasta: item.hasta || '' })
  }

  function handleCreatePlus(e: React.FormEvent) {
    e.preventDefault()
    const data = {
      grupo: plusForm.grupo, rol: plusForm.rol, descripcion: plusForm.descripcion || null,
      monto: plusForm.monto, tope_acumulacion: plusForm.tope_acumulacion || null,
      desde: plusForm.desde, hasta: plusForm.hasta || null,
    }
    if (editId) {
      actualizarPlus.mutate({ id: editId, data }, { onSuccess: resetPlusForm })
    } else {
      crearPlus.mutate(data as any, { onSuccess: resetPlusForm })
    }
  }

  function handleEditPlus(item: { id: string; grupo: string; rol: string; descripcion: string | null; monto: number; tope_acumulacion: number | null; desde: string; hasta: string | null }) {
    setEditId(item.id)
    setPlusForm({
      grupo: item.grupo, rol: item.rol, descripcion: item.descripcion || '',
      monto: item.monto, tope_acumulacion: item.tope_acumulacion || 0,
      desde: item.desde, hasta: item.hasta || '',
    })
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-primary">Grilla Salarial</h2>
      </div>

      <nav className="flex gap-1 border-b border-border">
        {([
          { key: 'base' as const, label: 'Salarios Base' },
          { key: 'plus' as const, label: 'Plus' },
          { key: 'materia-grupo' as const, label: 'Materia-Grupo' },
        ]).map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`-mb-px border-b-2 px-4 py-2 text-sm transition-colors ${
              tab === t.key
                ? 'border-primary text-primary'
                : 'border-transparent text-on-surface-muted hover:text-on-surface'
            }`}
          >
            {t.label}
          </button>
        ))}
      </nav>

      {tab === 'base' && (
        <div className="space-y-6">
          <form onSubmit={handleCreateBase} className="max-w-lg space-y-4 rounded-lg border border-border bg-surface p-6">
            <h3 className="text-sm font-semibold text-on-surface">
              {editId ? 'Editar salario base' : 'Nuevo salario base'}
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="sb-rol" className="mb-1 block text-sm text-on-surface">Rol</label>
                <input id="sb-rol" type="text" value={baseForm.rol} onChange={(e) => setBaseForm({ ...baseForm, rol: e.target.value })} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
              </div>
              <div>
                <label htmlFor="sb-monto" className="mb-1 block text-sm text-on-surface">Monto</label>
                <input id="sb-monto" type="number" step="0.01" value={baseForm.monto} onChange={(e) => setBaseForm({ ...baseForm, monto: parseFloat(e.target.value) || 0 })} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
              </div>
              <div>
                <label htmlFor="sb-desde" className="mb-1 block text-sm text-on-surface">Desde</label>
                <input id="sb-desde" type="date" value={baseForm.desde} onChange={(e) => setBaseForm({ ...baseForm, desde: e.target.value })} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
              </div>
              <div>
                <label htmlFor="sb-hasta" className="mb-1 block text-sm text-on-surface">Hasta (opcional)</label>
                <input id="sb-hasta" type="date" value={baseForm.hasta} onChange={(e) => setBaseForm({ ...baseForm, hasta: e.target.value })} className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
              </div>
            </div>
            <div className="flex justify-end gap-3">
              {editId && (
                <button type="button" onClick={resetBaseForm} className="rounded border border-border px-4 py-2 text-sm hover:bg-surface-hover">Cancelar</button>
              )}
              <button type="submit" disabled={crearBase.isPending || actualizarBase.isPending} className="rounded bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:bg-primary-hover disabled:opacity-50">
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
                        <button onClick={() => handleEditBase(sb)} className="rounded border border-border px-2 py-1 text-xs hover:bg-surface-hover">Editar</button>
                        <button onClick={() => { if (window.confirm('¿Eliminar este salario base?')) eliminarBase.mutate(sb.id) }} className="rounded border border-danger px-2 py-1 text-xs text-danger hover:bg-danger/5">Eliminar</button>
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
      )}

      {tab === 'plus' && (
        <div className="space-y-6">
          <form onSubmit={handleCreatePlus} className="max-w-lg space-y-4 rounded-lg border border-border bg-surface p-6">
            <h3 className="text-sm font-semibold text-on-surface">
              {editId ? 'Editar salario plus' : 'Nuevo salario plus'}
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="sp-grupo" className="mb-1 block text-sm text-on-surface">Grupo</label>
                <input id="sp-grupo" type="text" value={plusForm.grupo} onChange={(e) => setPlusForm({ ...plusForm, grupo: e.target.value })} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
              </div>
              <div>
                <label htmlFor="sp-rol" className="mb-1 block text-sm text-on-surface">Rol</label>
                <input id="sp-rol" type="text" value={plusForm.rol} onChange={(e) => setPlusForm({ ...plusForm, rol: e.target.value })} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
              </div>
              <div className="col-span-2">
                <label htmlFor="sp-desc" className="mb-1 block text-sm text-on-surface">Descripción (opcional)</label>
                <input id="sp-desc" type="text" value={plusForm.descripcion} onChange={(e) => setPlusForm({ ...plusForm, descripcion: e.target.value })} className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
              </div>
              <div>
                <label htmlFor="sp-monto" className="mb-1 block text-sm text-on-surface">Monto</label>
                <input id="sp-monto" type="number" step="0.01" value={plusForm.monto} onChange={(e) => setPlusForm({ ...plusForm, monto: parseFloat(e.target.value) || 0 })} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
              </div>
              <div>
                <label htmlFor="sp-tope" className="mb-1 block text-sm text-on-surface">Tope acumulación</label>
                <input id="sp-tope" type="number" step="0.01" value={plusForm.tope_acumulacion} onChange={(e) => setPlusForm({ ...plusForm, tope_acumulacion: parseFloat(e.target.value) || 0 })} className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
              </div>
              <div>
                <label htmlFor="sp-desde" className="mb-1 block text-sm text-on-surface">Desde</label>
                <input id="sp-desde" type="date" value={plusForm.desde} onChange={(e) => setPlusForm({ ...plusForm, desde: e.target.value })} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
              </div>
              <div>
                <label htmlFor="sp-hasta" className="mb-1 block text-sm text-on-surface">Hasta (opcional)</label>
                <input id="sp-hasta" type="date" value={plusForm.hasta} onChange={(e) => setPlusForm({ ...plusForm, hasta: e.target.value })} className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
              </div>
            </div>
            <div className="flex justify-end gap-3">
              {editId && (
                <button type="button" onClick={resetPlusForm} className="rounded border border-border px-4 py-2 text-sm hover:bg-surface-hover">Cancelar</button>
              )}
              <button type="submit" disabled={crearPlus.isPending || actualizarPlus.isPending} className="rounded bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:bg-primary-hover disabled:opacity-50">
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
                        <button onClick={() => handleEditPlus(sp)} className="rounded border border-border px-2 py-1 text-xs hover:bg-surface-hover">Editar</button>
                        <button onClick={() => { if (window.confirm('¿Eliminar este salario plus?')) eliminarPlus.mutate(sp.id) }} className="rounded border border-danger px-2 py-1 text-xs text-danger hover:bg-danger/5">Eliminar</button>
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
      )}

      {tab === 'materia-grupo' && (
        <p className="text-sm text-on-surface-muted">
          La gestión de Materia-Grupo Plus está disponible en el endpoint <code className="rounded bg-surface-hover px-1 py-0.5 font-mono text-xs">/liquidaciones/materias-grupo</code>.
          Consultá la documentación de la API para más detalles.
        </p>
      )}
    </div>
  )
}
