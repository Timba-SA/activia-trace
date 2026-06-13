import { useState } from 'react'
import { useFacturas, useCrearFactura, useCambiarEstadoFactura } from '../hooks/useFinanzas'
import { useUsuarios } from '@/features/admin/hooks/useAdmin'

const estados = ['Pendiente', 'Aprobada', 'Pagada', 'Rechazada', 'Cancelada']

const estadoColors: Record<string, string> = {
  Pendiente: 'bg-warning/10 text-warning',
  Aprobada: 'bg-primary/10 text-primary',
  Pagada: 'bg-success/10 text-success',
  Rechazada: 'bg-danger/10 text-danger',
  Cancelada: 'bg-on-surface-muted/10 text-on-surface-muted',
}

const emptyFactura = { usuario_id: '', periodo: '', detalle: '', referencia_archivo: '', tamano_kb: 0 }

export default function FacturasPage() {
  const [showForm, setShowForm] = useState(false)
  const [filtroPeriodo, setFiltroPeriodo] = useState('')
  const [filtroEstado, setFiltroEstado] = useState('')
  const [facturaForm, setFacturaForm] = useState(emptyFactura)

  const { data, isLoading } = useFacturas({
    periodo: filtroPeriodo || undefined,
    estado: filtroEstado || undefined,
  })
  const { data: usuarios } = useUsuarios({ limit: 100 })
  const crear = useCrearFactura()
  const cambiarEstado = useCambiarEstadoFactura()

  function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    crear.mutate({
      usuario_id: facturaForm.usuario_id,
      periodo: facturaForm.periodo,
      detalle: facturaForm.detalle || null,
      referencia_archivo: facturaForm.referencia_archivo,
      tamano_kb: facturaForm.tamano_kb || null,
    }, {
      onSuccess: () => { setShowForm(false); setFacturaForm(emptyFactura) },
    })
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-primary">Facturas</h2>
        <button
          onClick={() => setShowForm(!showForm)}
          className="rounded bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:bg-primary-hover"
        >
          {showForm ? 'Cancelar' : 'Nueva factura'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="max-w-lg space-y-4 rounded-lg border border-border bg-surface p-6">
          <h3 className="text-sm font-semibold text-on-surface">Registrar factura</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="fac-usuario" className="mb-1 block text-sm text-on-surface">Usuario</label>
              <select id="fac-usuario" value={facturaForm.usuario_id} onChange={(e) => setFacturaForm({ ...facturaForm, usuario_id: e.target.value })} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm">
                <option value="">Seleccionar usuario</option>
                {usuarios?.items.map(u => <option key={u.id} value={u.id}>{u.nombre} {u.apellido} — {u.email}</option>)}
              </select>
            </div>
            <div>
              <label htmlFor="fac-periodo" className="mb-1 block text-sm text-on-surface">Periodo</label>
              <input id="fac-periodo" type="text" value={facturaForm.periodo} onChange={(e) => setFacturaForm({ ...facturaForm, periodo: e.target.value })} required placeholder="Ej: 2025-01" className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
            <div className="col-span-2">
              <label htmlFor="fac-detalle" className="mb-1 block text-sm text-on-surface">Detalle (opcional)</label>
              <textarea id="fac-detalle" value={facturaForm.detalle} onChange={(e) => setFacturaForm({ ...facturaForm, detalle: e.target.value })} rows={2} className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
            <div className="col-span-2">
              <label htmlFor="fac-archivo" className="mb-1 block text-sm text-on-surface">Referencia archivo</label>
              <input id="fac-archivo" type="text" value={facturaForm.referencia_archivo} onChange={(e) => setFacturaForm({ ...facturaForm, referencia_archivo: e.target.value })} required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
            <div>
              <label htmlFor="fac-tamano" className="mb-1 block text-sm text-on-surface">Tamaño KB (opcional)</label>
              <input id="fac-tamano" type="number" value={facturaForm.tamano_kb} onChange={(e) => setFacturaForm({ ...facturaForm, tamano_kb: parseInt(e.target.value) || 0 })} className="w-full rounded border border-border bg-surface px-3 py-2 text-sm" />
            </div>
          </div>
          <div className="flex justify-end gap-3">
            <button type="button" onClick={() => setShowForm(false)} className="rounded border border-border px-4 py-2 text-sm hover:bg-surface-hover">Cancelar</button>
            <button type="submit" disabled={crear.isPending} className="rounded bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:bg-primary-hover disabled:opacity-50">
              {crear.isPending ? 'Creando...' : 'Crear'}
            </button>
          </div>
        </form>
      )}

      <div className="flex flex-wrap items-end gap-4">
        <div>
          <label htmlFor="fac-filtro-periodo" className="mb-1 block text-sm text-on-surface">Periodo</label>
          <input
            id="fac-filtro-periodo"
            type="text"
            value={filtroPeriodo}
            onChange={(e) => setFiltroPeriodo(e.target.value)}
            placeholder="Filtrar por periodo"
            className="w-full rounded border border-border bg-surface px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label htmlFor="fac-filtro-estado" className="mb-1 block text-sm text-on-surface">Estado</label>
          <select
            id="fac-filtro-estado"
            value={filtroEstado}
            onChange={(e) => setFiltroEstado(e.target.value)}
            className="w-full rounded border border-border bg-surface px-3 py-2 text-sm"
          >
            <option value="">Todos</option>
            {estados.map((e) => <option key={e} value={e}>{e}</option>)}
          </select>
        </div>
      </div>

      <div className="overflow-x-auto rounded-lg border border-border">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-surface-hover text-left text-xs font-medium text-on-surface-muted uppercase">
              <th className="px-4 py-3">Usuario</th>
              <th className="px-4 py-3">Periodo</th>
              <th className="px-4 py-3">Detalle</th>
              <th className="px-4 py-3">Archivo</th>
              <th className="px-4 py-3">Estado</th>
              <th className="px-4 py-3">Cargada</th>
              <th className="px-4 py-3">Abonada</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {data?.items.map((f) => (
              <tr key={f.id} className="bg-surface hover:bg-surface-hover">
                <td className="px-4 py-3 text-on-surface">{usuarios?.items.find(u => u.id === f.usuario_id)?.nombre ?? f.usuario_id.slice(0, 8) + '…'}</td>
                <td className="px-4 py-3 text-on-surface">{f.periodo}</td>
                <td className="px-4 py-3 text-on-surface-muted max-w-xs truncate">{f.detalle || '—'}</td>
                <td className="px-4 py-3 text-on-surface font-mono text-xs">{f.referencia_archivo}</td>
                <td className="px-4 py-3">
                  <select
                    value={f.estado}
                    onChange={(e) => cambiarEstado.mutate({ id: f.id, data: { estado: e.target.value } })}
                    className={`rounded px-2 py-0.5 text-xs font-medium border border-border ${estadoColors[f.estado]}`}
                  >
                    {estados.map((e) => <option key={e} value={e}>{e}</option>)}
                  </select>
                </td>
                <td className="px-4 py-3 text-on-surface-muted">{new Date(f.cargada_at).toLocaleDateString()}</td>
                <td className="px-4 py-3 text-on-surface-muted">{f.abonada_at ? new Date(f.abonada_at).toLocaleDateString() : '—'}</td>
              </tr>
            ))}
            {(!data || data.items.length === 0) && (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-sm text-on-surface-muted">
                  {isLoading ? 'Cargando...' : 'Sin facturas.'}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
