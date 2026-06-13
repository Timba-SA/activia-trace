import type { StudentAlert } from './AlertasTable'

export default function StudentDetail({ student }: { student: StudentAlert }) {
  return (
    <div className="space-y-lg">
      <div className="grid grid-cols-2 gap-md">
        <div>
          <div className="text-label-sm text-on-surface-variant">Legajo</div>
          <div className="font-mono-code text-mono-code text-on-background">{student.legajo}</div>
        </div>
        <div>
          <div className="text-label-sm text-on-surface-variant">Cohorte</div>
          <div className="font-mono-code text-mono-code text-on-background">{student.cohorte}</div>
        </div>
        <div className="col-span-2">
          <div className="text-label-sm text-on-surface-variant">Carrera</div>
          <div className="text-body-md text-on-background">{student.carrera}</div>
        </div>
      </div>

      {student.status === 'CRITICO' && (
        <div className="flex items-start gap-md rounded-lg border border-error/30 bg-error-container/20 p-md">
          <span className="material-symbols-outlined mt-0.5 text-error">warning</span>
          <div>
            <h4 className="text-label-sm text-on-error-container">RIESGO DE DESERCIÓN CRÍTICO</h4>
            <p className="mt-1 text-body-md text-on-surface-variant">
              Ausencia prolongada en el campus virtual (Moodle) y falta de entregas en 3 materias troncales durante las últimas 2 semanas.
            </p>
          </div>
        </div>
      )}

      {student.status === 'ATRASADO' && (
        <div className="flex items-start gap-md rounded-lg border border-[#fef3c7]/30 bg-[#fff8e1]/50 p-md">
          <span className="material-symbols-outlined mt-0.5 text-[#b45309]">schedule</span>
          <div>
            <h4 className="text-label-sm text-[#b45309]">RIESGO DE ATRASO MODERADO</h4>
            <p className="mt-1 text-body-md text-on-surface-variant">
              Entregas pendientes en 1 materia. Se recomienda contacto con el alumno para regularizar su situación.
            </p>
          </div>
        </div>
      )}

      <div>
        <h3 className="mb-md border-b border-outline-variant pb-1 text-label-sm text-on-surface-variant">MÉTRICAS DE COMPROMISO</h3>
        <div className="space-y-4">
          <div>
            <div className="mb-1 flex justify-between text-label-sm">
              <span className="text-on-background">Asistencia Promedio</span>
              <span className={student.status === 'CRITICO' ? 'text-error' : 'text-[#b45309]'}>
                {student.status === 'CRITICO' ? '42%' : '71%'}
              </span>
            </div>
            <div className="h-1.5 w-full rounded-full bg-surface-container-high">
              <div
                className={`h-1.5 rounded-full ${student.status === 'CRITICO' ? 'bg-error' : 'bg-[#b45309]'}`}
                style={{ width: student.status === 'CRITICO' ? '42%' : '71%' }}
              />
            </div>
          </div>
          <div>
            <div className="mb-1 flex justify-between text-label-sm">
              <span className="text-on-background">Entregas a Tiempo (TPs)</span>
              <span className={student.status === 'CRITICO' ? 'text-error' : 'text-[#15803d]'}>
                {student.status === 'CRITICO' ? '60%' : '94%'}
              </span>
            </div>
            <div className="h-1.5 w-full rounded-full bg-surface-container-high">
              <div
                className={`h-1.5 rounded-full ${student.status === 'CRITICO' ? 'bg-error' : 'bg-[#15803d]'}`}
                style={{ width: student.status === 'CRITICO' ? '60%' : '94%' }}
              />
            </div>
          </div>
        </div>
      </div>

      <div>
        <h3 className="mb-md border-b border-outline-variant pb-1 text-label-sm text-on-surface-variant">ÚLTIMOS EVENTOS (LOGS)</h3>
        <div className="h-48 overflow-y-auto rounded-lg bg-[#0F172A] p-md font-mono-code text-mono-code text-on-surface-variant">
          <div className="mb-2 flex gap-4">
            <span className="text-[#475569]">10:45:02</span>
            <span className="text-[#38bdf8]">[LOGIN_FAILED]</span>
            <span className="text-[#94a3b8]">Invalid credentials</span>
          </div>
          <div className="mb-2 flex gap-4">
            <span className="text-[#475569]">14-days-ago</span>
            <span className="text-[#f472b6]">[SYSTEM_ALERT]</span>
            <span className="text-[#94a3b8]">Inactivity threshold reached (336h)</span>
          </div>
          <div className="mb-2 flex gap-4">
            <span className="text-[#475569]">14-days-ago</span>
            <span className="text-[#a7f3d0]">[SESSION_END]</span>
            <span className="text-[#94a3b8]">User logged out normally</span>
          </div>
          <div className="mb-2 flex gap-4">
            <span className="text-[#475569]">14-days-ago</span>
            <span className="text-[#fbbf24]">[RESOURCE_VIEW]</span>
            <span className="text-[#94a3b8]">/mod/assign/view.php?id=8492</span>
          </div>
        </div>
      </div>
    </div>
  )
}
