import { useState } from 'react'
import type { AlumnoAtrasado } from '../types'

interface Props {
  alumnos: AlumnoAtrasado[]
}

export function AtrasadosTable({ alumnos }: Props) {
  const [filtro, setFiltro] = useState('')

  const filtrados = alumnos.filter((a) =>
    a.alumno.nombre.toLowerCase().includes(filtro.toLowerCase())
  )

  return (
    <div className="space-y-3">
      <input
        type="text"
        placeholder="Filtrar por nombre..."
        value={filtro}
        onChange={(e) => setFiltro(e.target.value)}
        className="w-full rounded border border-border bg-surface px-3 py-2 text-sm"
      />
      <div className="max-h-80 overflow-y-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border text-left text-xs uppercase text-on-surface-muted">
              <th className="px-2 py-2">Alumno</th>
              <th className="px-2 py-2">Email</th>
              <th className="px-2 py-2">Act. faltantes</th>
              <th className="px-2 py-2">Promedio</th>
              <th className="px-2 py-2">Estado</th>
            </tr>
          </thead>
          <tbody>
            {filtrados.map((a) => (
              <tr key={a.alumno.id} className="border-b border-border">
                <td className="px-2 py-2 font-medium">{a.alumno.nombre}</td>
                <td className="px-2 py-2 text-on-surface-muted">{a.alumno.email}</td>
                <td className="px-2 py-2">{a.actividades_faltantes.length}</td>
                <td className="px-2 py-2">{a.nota_promedio.toFixed(1)}</td>
                <td className="px-2 py-2">
                  <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${
                    a.estado === 'aprobado' ? 'bg-success/10 text-success' :
                    a.estado === 'en_riesgo' ? 'bg-warning/10 text-warning' :
                    'bg-danger/10 text-danger'
                  }`}>
                    {a.estado === 'aprobado' ? 'Aprobado' : a.estado === 'en_riesgo' ? 'En riesgo' : 'Atrasado'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {filtrados.length === 0 && (
        <p className="py-4 text-center text-sm text-on-surface-muted">Sin resultados</p>
      )}
    </div>
  )
}
