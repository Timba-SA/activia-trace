import { useState } from 'react'
import type { MonitoreoAlumno } from '../types'

interface Props {
  alumnos: MonitoreoAlumno[]
}

export function MonitoreoAlumnos({ alumnos }: Props) {
  const [nombreFiltro, setNombreFiltro] = useState('')
  const [minCumplido, setMinCumplido] = useState(0)

  const filtrados = alumnos.filter((a) => {
    if (nombreFiltro && !a.alumno.nombre.toLowerCase().includes(nombreFiltro.toLowerCase())) return false
    if (minCumplido > 0) {
      const pct = a.total_actividades > 0 ? (a.actividades_completadas / a.total_actividades) * 100 : 0
      if (pct < minCumplido) return false
    }
    return true
  })

  return (
    <div className="space-y-3">
      <div className="flex gap-3">
        <input
          type="text"
          placeholder="Filtrar por nombre..."
          value={nombreFiltro}
          onChange={(e) => setNombreFiltro(e.target.value)}
          className="flex-1 rounded border border-border bg-surface px-3 py-2 text-sm"
        />
        <div className="flex items-center gap-2">
          <label className="text-xs text-on-surface-muted">Mín %:</label>
          <input
            type="number"
            min="0"
            max="100"
            value={minCumplido}
            onChange={(e) => setMinCumplido(Number(e.target.value))}
            className="w-16 rounded border border-border bg-surface px-2 py-2 text-sm"
          />
        </div>
      </div>
      {filtrados.length === 0 ? (
        <p className="py-4 text-center text-sm text-on-surface-muted">Sin resultados</p>
      ) : (
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border text-left text-xs uppercase text-on-surface-muted">
              <th className="px-2 py-2">Alumno</th>
              <th className="px-2 py-2">Completadas</th>
              <th className="px-2 py-2">Total</th>
              <th className="px-2 py-2">%</th>
              <th className="px-2 py-2">Promedio</th>
            </tr>
          </thead>
          <tbody>
            {filtrados.map((a) => {
              const pct = a.total_actividades > 0 ? Math.round((a.actividades_completadas / a.total_actividades) * 100) : 0
              return (
                <tr key={a.alumno.id} className="border-b border-border">
                  <td className="px-2 py-2 font-medium">{a.alumno.nombre}</td>
                  <td className="px-2 py-2">{a.actividades_completadas}</td>
                  <td className="px-2 py-2">{a.total_actividades}</td>
                  <td className="px-2 py-2">
                    <span className={`font-semibold ${pct >= 60 ? 'text-success' : 'text-danger'}`}>{pct}%</span>
                  </td>
                  <td className="px-2 py-2">{a.nota_promedio.toFixed(1)}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      )}
    </div>
  )
}
