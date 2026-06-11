import { useState } from 'react'
import { useAvisos, useCrearAviso, useActualizarAviso, useEliminarAviso, useStatsAviso } from '../hooks/useCoordinacion'
import { AvisosList } from '../components/AvisosList'
import { AvisoForm } from '../components/AvisoForm'
import type { AvisoResponse, AvisoCreateRequest, AvisoUpdateRequest } from '../types'

export default function AvisosPage() {
  const { data, isLoading } = useAvisos()
  const crear = useCrearAviso()
  const actualizar = useActualizarAviso()
  const eliminar = useEliminarAviso()
  const [showForm, setShowForm] = useState(false)
  const [editing, setEditing] = useState<AvisoResponse | null>(null)
  const [statsId, setStatsId] = useState<string | null>(null)
  const { data: stats } = useStatsAviso(statsId)

  function handleSave(payload: AvisoCreateRequest | AvisoUpdateRequest) {
    if (editing) {
      actualizar.mutate({ id: editing.id, data: payload as AvisoUpdateRequest }, {
        onSuccess: () => { setShowForm(false); setEditing(null) },
      })
    } else {
      crear.mutate(payload as AvisoCreateRequest, {
        onSuccess: () => { setShowForm(false) },
      })
    }
  }

  function handleDelete(id: string) {
    if (window.confirm('¿Eliminar este aviso?')) {
      eliminar.mutate(id)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-primary">Avisos</h2>
        <button
          onClick={() => { setEditing(null); setShowForm(!showForm) }}
          className="rounded bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:bg-primary-hover"
        >
          {showForm ? 'Cancelar' : 'Nuevo aviso'}
        </button>
      </div>

      {showForm && (
        <div className="max-w-lg rounded-lg border border-border bg-surface p-6">
          <h3 className="mb-4 text-sm font-semibold text-on-surface">
            {editing ? 'Editar aviso' : 'Crear nuevo aviso'}
          </h3>
          <AvisoForm aviso={editing || undefined} onSave={handleSave} onClose={() => { setShowForm(false); setEditing(null) }} loading={crear.isPending || actualizar.isPending} />
          {(crear.data || actualizar.data) && (
            <p className="mt-3 text-sm text-success">Aviso guardado correctamente.</p>
          )}
        </div>
      )}

      {statsId && stats && (
        <div className="rounded-lg border border-border bg-surface p-4">
          <div className="flex items-center justify-between">
            <p className="text-sm text-on-surface">Confirmaciones: <span className="font-semibold text-primary">{stats.total_confirmaciones}</span></p>
            <button onClick={() => setStatsId(null)} className="text-xs text-on-surface-muted hover:text-on-surface">Cerrar</button>
          </div>
        </div>
      )}

      {isLoading ? (
        <div className="h-32 animate-pulse rounded bg-border" />
      ) : data ? (
        <AvisosList
          items={data.items}
          onEdit={(a) => { setEditing(a); setShowForm(true) }}
          onDelete={handleDelete}
          onStats={(id) => setStatsId(id)}
        />
      ) : null}
    </div>
  )
}
