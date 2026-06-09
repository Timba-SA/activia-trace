import type { RankingEntry } from '../types'

export function RankingTable({ entries }: { entries: RankingEntry[] }) {
  return (
    <table className="w-full text-sm">
      <thead>
        <tr className="border-b border-border text-left text-xs uppercase text-on-surface-muted">
          <th className="px-2 py-2">#</th>
          <th className="px-2 py-2">Alumno</th>
          <th className="px-2 py-2">Act. aprobadas</th>
          <th className="px-2 py-2">Total</th>
        </tr>
      </thead>
      <tbody>
        {entries.map((e, i) => (
          <tr key={e.alumno.id} className="border-b border-border">
            <td className="px-2 py-2 text-on-surface-muted">{i + 1}</td>
            <td className="px-2 py-2 font-medium">{e.alumno.nombre}</td>
            <td className="px-2 py-2">{e.actividades_aprobadas}</td>
            <td className="px-2 py-2">{e.total_actividades}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
