import { useAtrasados, useRanking } from '../hooks/useAcademico'
import { UmbralConfig } from '../components/UmbralConfig'
import { AtrasadosTable } from '../components/AtrasadosTable'
import { RankingTable } from '../components/RankingTable'

export default function AtrasadosPage() {
  const { data: atrasados, isLoading: loadingAtrasados } = useAtrasados()
  const { data: ranking, isLoading: loadingRanking } = useRanking()

  return (
    <div className="space-y-6">
      <h2 className="text-lg font-semibold text-primary">Análisis de alumnos</h2>

      <UmbralConfig />

      <div>
        <h3 className="mb-3 text-sm font-semibold text-on-surface">Alumnos atrasados</h3>
        {loadingAtrasados ? (
          <div className="h-24 animate-pulse rounded bg-border" />
        ) : atrasados && atrasados.length > 0 ? (
          <AtrasadosTable alumnos={atrasados} />
        ) : (
          <p className="text-sm text-on-surface-muted">No hay alumnos atrasados en esta comisión.</p>
        )}
      </div>

      <div>
        <h3 className="mb-3 text-sm font-semibold text-on-surface">Ranking de actividades aprobadas</h3>
        {loadingRanking ? (
          <div className="h-24 animate-pulse rounded bg-border" />
        ) : ranking && ranking.length > 0 ? (
          <RankingTable entries={ranking} />
        ) : (
          <p className="text-sm text-on-surface-muted">Sin datos suficientes para mostrar ranking.</p>
        )}
      </div>
    </div>
  )
}
