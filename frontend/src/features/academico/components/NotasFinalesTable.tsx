import type { NotaFinal } from '../types'

interface Props {
  notas: NotaFinal[]
}

export function NotasFinalesTable({ notas }: Props) {
  return (
    <table className="w-full text-sm">
      <thead>
        <tr className="border-b border-border text-left text-xs uppercase text-on-surface-muted">
          <th className="px-2 py-2">Alumno</th>
          <th className="px-2 py-2">Nota final</th>
          <th className="px-2 py-2">Actividades</th>
        </tr>
      </thead>
      <tbody>
        {notas.map((n) => (
          <tr key={n.alumno.id} className="border-b border-border">
            <td className="px-2 py-2 font-medium">{n.alumno.nombre}</td>
            <td className="px-2 py-2">
              <span className={`font-semibold ${n.nota_final >= 60 ? 'text-success' : 'text-danger'}`}>
                {n.nota_final.toFixed(1)}
              </span>
            </td>
            <td className="px-2 py-2 text-on-surface-muted">{n.actividades_incluidas}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
