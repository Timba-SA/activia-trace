export interface StudentAlert {
  initials: string
  name: string
  carrera: string
  cohorte: string
  status: 'CRITICO' | 'ATRASADO' | 'REGULAR'
  ultimaActividad: string
  legajo: string
}

const statusConfig: Record<StudentAlert['status'], { className: string; label: string }> = {
  CRITICO: { className: 'border border-error/20 bg-error-container text-on-error-container', label: 'CRÍTICO' },
  ATRASADO: { className: 'border border-[#fef3c7] bg-[#fff8e1] text-[#b45309]', label: 'ATRASADO' },
  REGULAR: { className: 'border border-[#dcfce7] bg-[#f0fdf4] text-[#15803d]', label: 'REGULAR' },
}

interface Props {
  alertas: StudentAlert[]
  onSelect: (student: StudentAlert) => void
}

export default function AlertasTable({ alertas, onSelect }: Props) {
  return (
    <div className="flex flex-col overflow-hidden rounded-xl border border-outline-variant bg-surface-container-lowest shadow-kpi">
      <div className="flex items-center justify-between border-b border-outline-variant bg-surface-container-lowest p-md">
        <h3 className="text-headline-sm text-on-background">Mapeo de Alertas Recientes</h3>
        <button type="button" className="flex items-center gap-1 text-label-sm text-primary transition-colors hover:text-primary-container">
          Ver reporte completo
          <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
        </button>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-left">
          <thead>
            <tr className="border-b border-outline-variant bg-surface">
              <th className="px-md py-sm text-label-sm uppercase text-on-surface-variant">Alumno</th>
              <th className="px-md py-sm text-label-sm uppercase text-on-surface-variant">Carrera</th>
              <th className="px-md py-sm text-label-sm uppercase text-on-surface-variant">Cohorte</th>
              <th className="px-md py-sm text-label-sm uppercase text-on-surface-variant">Estado</th>
              <th className="px-md py-sm text-right text-label-sm uppercase text-on-surface-variant">Última Actividad</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-outline-variant/50 text-body-md text-on-background">
            {alertas.map((alumno) => (
              <tr
                key={alumno.name}
                onClick={() => onSelect(alumno)}
                className="cursor-pointer transition-colors hover:bg-slate-50"
              >
                <td className="h-[48px] px-md py-2">
                  <div className="flex items-center gap-2">
                    <div className={`flex size-8 items-center justify-center rounded-full text-label-sm ${
                      alumno.status === 'CRITICO'
                        ? 'bg-primary-container text-on-primary-container'
                        : 'bg-surface-variant text-on-surface-variant'
                    }`}>
                      {alumno.initials}
                    </div>
                    <span className="font-semibold text-primary">{alumno.name}</span>
                  </div>
                </td>
                <td className="px-md py-2">{alumno.carrera}</td>
                <td className="px-md py-2 font-mono-code text-mono-code text-on-surface-variant">{alumno.cohorte}</td>
                <td className="px-md py-2">
                  <span className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[11px] font-bold ${statusConfig[alumno.status].className}`}>
                    {statusConfig[alumno.status].label}
                  </span>
                </td>
                <td className="px-md py-2 text-right font-mono-code text-mono-code text-on-surface-variant">{alumno.ultimaActividad}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
