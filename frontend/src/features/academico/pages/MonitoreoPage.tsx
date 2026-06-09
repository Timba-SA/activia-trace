import { useMonitoreo } from '../hooks/useAcademico'
import { MonitoreoAlumnos } from '../components/MonitoreoAlumnos'

export default function MonitoreoPage() {
  const { data: alumnos, isLoading } = useMonitoreo()

  return (
    <div className="space-y-6">
      <h2 className="text-lg font-semibold text-primary">Monitoreo de alumnos</h2>
      {isLoading ? (
        <div className="h-24 animate-pulse rounded bg-border" />
      ) : alumnos && alumnos.length > 0 ? (
        <MonitoreoAlumnos alumnos={alumnos} />
      ) : (
        <p className="text-sm text-on-surface-muted">No hay datos de monitoreo para esta comisión.</p>
      )}
    </div>
  )
}
