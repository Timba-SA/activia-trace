import { useState } from 'react'
import { useUltimasAcciones, useMetricasAccionesPorDia, useMetricasPorDocente, useMetricasPorMateria, useMetricasComunicaciones } from '../hooks/useAdmin'
import AuditoriaDashboard from '../components/AuditoriaDashboard'
import AuditoriaLogTab from '../components/AuditoriaLogTab'

type Tab = 'dashboard' | 'log'

export default function AuditoriaPage() {
  const [tab, setTab] = useState<Tab>('dashboard')
  const [filtros, setFiltros] = useState({ accion: '', actor_id: '', materia_id: '', desde: '', hasta: '' })

  const metricasDia = useMetricasAccionesPorDia()
  const metricasDocente = useMetricasPorDocente()
  const metricasMateria = useMetricasPorMateria()
  const metricasComms = useMetricasComunicaciones()

  const { data, isLoading } = useUltimasAcciones({
    accion: filtros.accion || undefined,
    actor_id: filtros.actor_id || undefined,
    materia_id: filtros.materia_id || undefined,
    desde: filtros.desde || undefined,
    hasta: filtros.hasta || undefined,
  })

  const totalAcciones = metricasDia.data?.items.reduce((s, i) => s + i.total, 0) ?? 0
  const totalDocentes = metricasDocente.data?.items.length ?? 0
  const totalMaterias = metricasMateria.data?.items.length ?? 0
  const totalComms = metricasComms.data?.items.reduce((s, i) => s + i.total_enviadas + i.total_recibidas, 0) ?? 0

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-primary">Auditoría</h2>
      </div>

      <nav className="flex gap-1 border-b border-border">
        {([
          { key: 'dashboard' as const, label: 'Dashboard' },
          { key: 'log' as const, label: 'Log' },
        ]).map((t) => (
          <button key={t.key} onClick={() => setTab(t.key)}
            className={`-mb-px border-b-2 px-4 py-2 text-sm transition-colors ${tab === t.key ? 'border-primary text-primary' : 'border-transparent text-on-surface-muted hover:text-on-surface'}`}>
            {t.label}
          </button>
        ))}
      </nav>

      {tab === 'dashboard' && (
        <AuditoriaDashboard
          metricasDia={metricasDia}
          metricasDocente={metricasDocente}
          metricasMateria={metricasMateria}
          totalAcciones={totalAcciones}
          totalDocentes={totalDocentes}
          totalMaterias={totalMaterias}
          totalComms={totalComms}
        />
      )}

      {tab === 'log' && (
        <AuditoriaLogTab
          data={data}
          isLoading={isLoading}
          filtros={filtros}
          onFiltrosChange={setFiltros}
        />
      )}
    </div>
  )
}
