import type { EntregaSinCorregir } from '../types'

interface Props {
  entregas: EntregaSinCorregir[]
}

export function EntregasSinCorregir({ entregas }: Props) {
  function exportarCSV() {
    const headers = ['Alumno', 'Email', 'Actividad', 'Fecha de entrega']
    const rows = entregas.map((e) => [e.alumno.nombre, e.alumno.email, e.actividad, e.fecha_entrega])
    const csv = [headers.join(','), ...rows.map((r) => r.map((v) => `"${v}"`).join(','))].join('\n')
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'entregas-sin-corregir.csv'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-on-surface">Entregas sin corregir ({entregas.length})</h3>
        <button onClick={exportarCSV} className="rounded border border-border px-3 py-1.5 text-xs font-medium hover:bg-surface-hover">
          Exportar CSV
        </button>
      </div>
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border text-left text-xs uppercase text-on-surface-muted">
            <th className="px-2 py-2">Alumno</th>
            <th className="px-2 py-2">Actividad</th>
            <th className="px-2 py-2">Fecha entrega</th>
          </tr>
        </thead>
        <tbody>
          {entregas.map((e, i) => (
            <tr key={i} className="border-b border-border">
              <td className="px-2 py-2 font-medium">{e.alumno.nombre}</td>
              <td className="px-2 py-2">{e.actividad}</td>
              <td className="px-2 py-2 text-on-surface-muted">{new Date(e.fecha_entrega).toLocaleDateString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
