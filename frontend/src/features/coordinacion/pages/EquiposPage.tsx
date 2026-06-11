import { useState } from 'react'
import { useEquipos, useAsignacionMasiva, useClonarEquipo, useUpdateVigencia, useExportarEquipo } from '../hooks/useCoordinacion'
import { EquiposList } from '../components/EquiposList'
import { AsignacionMasivaForm } from '../components/AsignacionMasivaForm'
import { ClonarEquipoForm } from '../components/ClonarEquipoForm'
import { VigenciaForm } from '../components/VigenciaForm'

type Tab = 'ver' | 'asignar' | 'clonar' | 'vigencia'

export default function EquiposPage() {
  const [tab, setTab] = useState<Tab>('ver')
  const [filtroNombre, setFiltroNombre] = useState('')
  const { data, isLoading } = useEquipos({ nombre: filtroNombre || undefined })
  const asignacion = useAsignacionMasiva()
  const clonar = useClonarEquipo()
  const vigencia = useUpdateVigencia()
  const exportar = useExportarEquipo()

  function handleExportar() {
    if (!data?.items.length) return
    const d = data.items[0]
    exportar.mutate({ materia_id: d.materia_id!, carrera_id: d.carrera_id!, cohorte_id: d.cohorte_id! })
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-primary">Equipos docentes</h2>
      </div>

      <nav className="flex gap-1 border-b border-border">
        {([
          { key: 'ver' as const, label: 'Ver equipo' },
          { key: 'asignar' as const, label: 'Asignación masiva' },
          { key: 'clonar' as const, label: 'Clonar equipo' },
          { key: 'vigencia' as const, label: 'Actualizar vigencia' },
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

      {tab === 'ver' && (
        <div className="space-y-4">
          <input
            type="text"
            value={filtroNombre}
            onChange={(e) => setFiltroNombre(e.target.value)}
            placeholder="Buscar por nombre..."
            className="w-full max-w-xs rounded border border-border bg-surface px-3 py-2 text-sm"
          />
          {isLoading ? (
            <div className="h-32 animate-pulse rounded bg-border" />
          ) : data ? (
            <EquiposList items={data.items} onExportar={handleExportar} exporting={exportar.isPending} />
          ) : null}
        </div>
      )}

      {tab === 'asignar' && (
        <div className="max-w-lg rounded-lg border border-border bg-surface p-6">
          <h3 className="mb-4 text-sm font-semibold text-on-surface">Asignación masiva de docentes</h3>
          <AsignacionMasivaForm
            onAsignar={(d) => asignacion.mutate(d)}
            onClose={() => setTab('ver')}
            loading={asignacion.isPending}
          />
          {asignacion.data && (
            <p className="mt-3 text-sm text-success">Se crearon {asignacion.data.creadas} asignaciones.</p>
          )}
        </div>
      )}

      {tab === 'clonar' && (
        <div className="max-w-lg rounded-lg border border-border bg-surface p-6">
          <h3 className="mb-4 text-sm font-semibold text-on-surface">Clonar equipo de cohorte</h3>
          <ClonarEquipoForm
            onClonar={(d) => clonar.mutate(d)}
            onClose={() => setTab('ver')}
            loading={clonar.isPending}
          />
          {clonar.data && (
            <p className="mt-3 text-sm text-success">Se clonaron {clonar.data.creadas} asignaciones.</p>
          )}
        </div>
      )}

      {tab === 'vigencia' && (
        <div className="max-w-lg rounded-lg border border-border bg-surface p-6">
          <h3 className="mb-4 text-sm font-semibold text-on-surface">Actualizar vigencia del equipo</h3>
          <VigenciaForm
            onUpdate={(d) => vigencia.mutate(d)}
            onClose={() => setTab('ver')}
            loading={vigencia.isPending}
          />
          {vigencia.data && (
            <p className="mt-3 text-sm text-success">Se actualizaron {vigencia.data.afectadas} registros.</p>
          )}
        </div>
      )}
    </div>
  )
}
