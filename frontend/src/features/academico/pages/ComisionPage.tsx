import { Link } from 'react-router-dom'
import { useComision } from '../hooks/useAcademico'
import { useCalificaciones } from '../hooks/useAcademico'
import { DashboardMetrics } from '../components/DashboardMetrics'

export default function ComisionPage() {
  const { materiaId, cohorteId } = useComision()
  const { data: calificaciones, isLoading } = useCalificaciones()

  if (isLoading) {
    return <div className="h-32 animate-pulse rounded bg-border" />
  }

  if (!calificaciones || calificaciones.length === 0) {
    return (
      <div className="space-y-4">
        <h2 className="text-lg font-semibold text-primary">Comisión sin datos</h2>
        <p className="text-sm text-on-surface-muted">Importá las calificaciones para empezar a trabajar.</p>
        <Link to={`/academico/${materiaId}/${cohorteId}/calificaciones`} className="inline-block rounded bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:bg-primary-hover">
          Ir a importar
        </Link>
      </div>
    )
  }

  const atrasados = calificaciones.filter((c) => c.atrasado).length
  const actividades = Object.keys(calificaciones[0]?.actividades ?? {}).length

  return (
    <div className="space-y-6">
      <h2 className="text-lg font-semibold text-primary">Dashboard</h2>
      <DashboardMetrics total={calificaciones.length} atrasados={atrasados} actividades={actividades} />
    </div>
  )
}
