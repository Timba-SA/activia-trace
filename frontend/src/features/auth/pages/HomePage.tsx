import { useState } from 'react'
import { useSession } from '@/features/auth/hooks/useAuth'
import { SideSheet } from '@/shared/components/ui/SideSheet'

function Icon({ name, className = '' }: { name: string; className?: string }) {
  return <span className={`material-symbols-outlined ${className}`}>{name}</span>
}

interface StudentAlert {
  initials: string
  name: string
  carrera: string
  cohorte: string
  status: 'CRITICO' | 'ATRASADO' | 'REGULAR'
  ultimaActividad: string
  legajo: string
}

const alertas: StudentAlert[] = [
  { initials: 'MR', name: 'Martina Rossi', carrera: 'Ingeniería en Sistemas', cohorte: '2023-1', status: 'CRITICO', ultimaActividad: 'Hace 14 días', legajo: 'SYS-23-0045' },
  { initials: 'JG', name: 'Juan Gomez', carrera: 'Licenciatura en Adm.', cohorte: '2022-2', status: 'ATRASADO', ultimaActividad: 'Hace 5 días', legajo: 'ADM-22-0092' },
  { initials: 'AL', name: 'Ana Lopez', carrera: 'Ingeniería Industrial', cohorte: '2023-2', status: 'REGULAR', ultimaActividad: 'Hace 2 horas', legajo: 'IND-23-0118' },
  { initials: 'CP', name: 'Carlos Perez', carrera: 'Analista de Sistemas', cohorte: '2021-1', status: 'CRITICO', ultimaActividad: 'Hace 21 días', legajo: 'AS-21-0033' },
]

const statusConfig = {
  CRITICO: {
    className: 'border border-error/20 bg-error-container text-on-error-container',
    label: 'CRÍTICO',
  },
  ATRASADO: {
    className: 'border border-[#fef3c7] bg-[#fff8e1] text-[#b45309]',
    label: 'ATRASADO',
  },
  REGULAR: {
    className: 'border border-[#dcfce7] bg-[#f0fdf4] text-[#15803d]',
    label: 'REGULAR',
  },
}

export default function HomePage() {
  const { data: session } = useSession()
  const [selectedStudent, setSelectedStudent] = useState<StudentAlert | null>(null)
  const userName = session?.nombre ?? session?.email ?? 'Usuario'

  return (
    <>
      <div className="space-y-lg">
        {/* Page Header */}
        <div>
          <h2 className="text-display-lg text-on-background">Dashboard Analítico</h2>
          <p className="mt-1 text-body-md text-on-surface-variant">
            Bienvenido, {userName}. Visión general del rendimiento y alertas tempranas del período lectivo actual.
          </p>
        </div>

        {/* KPI Cards Row */}
        <div className="grid grid-cols-1 gap-md sm:grid-cols-2 lg:grid-cols-4">
          <div className="flex flex-col gap-sm rounded-xl border border-outline-variant bg-surface-container-lowest p-md shadow-kpi">
            <div className="flex items-start justify-between">
              <span className="text-label-sm uppercase tracking-wider text-on-surface-variant">Total Alumnos Activos</span>
              <Icon name="school" className="text-primary" />
            </div>
            <div className="text-headline-md text-on-background">14,285</div>
            <div className="flex items-center gap-1 text-label-sm text-primary">
              <Icon name="trending_up" className="text-[16px]" />
              <span>+2.4% vs mes anterior</span>
            </div>
          </div>

          <div className="flex flex-col gap-sm rounded-xl border border-outline-variant bg-surface-container-lowest p-md shadow-kpi">
            <div className="flex items-start justify-between">
              <span className="text-label-sm uppercase tracking-wider text-on-surface-variant">Eficiencia Ingesta Moodle</span>
              <Icon name="cloud_sync" className="text-primary" />
            </div>
            <div className="text-headline-md text-on-background">98.4%</div>
            <div className="flex items-center gap-1 text-label-sm text-primary">
              <Icon name="check_circle" className="text-[16px]" />
              <span>Sincronización óptima</span>
            </div>
          </div>

          <div className="flex flex-col gap-sm rounded-xl border border-outline-variant bg-surface-container-lowest p-md shadow-kpi border-l-4 border-l-error">
            <div className="flex items-start justify-between">
              <span className="text-label-sm uppercase tracking-wider text-on-surface-variant">Alertas de Deserción Crítica</span>
              <Icon name="warning" className="text-error" />
            </div>
            <div className="text-headline-md text-error">12</div>
            <div className="flex items-center gap-1 text-label-sm text-error">
              <Icon name="priority_high" className="text-[16px]" />
              <span>Requiere acción inmediata</span>
            </div>
          </div>

          <div className="flex flex-col gap-sm rounded-xl border border-outline-variant bg-surface-container-lowest p-md shadow-kpi">
            <div className="flex items-start justify-between">
              <span className="text-label-sm uppercase tracking-wider text-on-surface-variant">Tasa de Aprobación Global</span>
              <Icon name="analytics" className="text-primary" />
            </div>
            <div className="text-headline-md text-on-background">68.2%</div>
            <div className="mt-1 h-1.5 w-full rounded-full bg-surface-container-high">
              <div className="h-1.5 rounded-full bg-primary" style={{ width: '68.2%' }} />
            </div>
          </div>
        </div>

        {/* Central Chart Section */}
        <div className="rounded-xl border border-outline-variant bg-surface-container-lowest p-md shadow-kpi">
          <div className="flex items-center justify-between border-b border-outline-variant pb-sm mb-md">
            <h3 className="text-headline-sm text-on-background">Correlación: Actividad vs Rendimiento</h3>
            <div className="flex gap-2">
              <span className="inline-flex items-center gap-1 text-label-sm text-on-surface-variant">
                <span className="size-3 rounded-full bg-primary" />
                Campus Activity (Logs)
              </span>
              <span className="ml-sm inline-flex items-center gap-1 text-label-sm text-on-surface-variant">
                <span className="size-3 rounded-full bg-secondary-container" />
                Academic Performance
              </span>
            </div>
          </div>
          <div className="relative flex h-64 w-full items-center justify-center overflow-hidden rounded-lg border border-dashed border-outline-variant bg-surface-container-low">
            <div
              className="absolute inset-0 opacity-30"
              style={{
                backgroundImage:
                  'linear-gradient(to right, #e0e3e5 1px, transparent 1px), linear-gradient(to bottom, #e0e3e5 1px, transparent 1px)',
                backgroundSize: '2rem 2rem',
              }}
            />
            <svg className="absolute inset-0 h-full w-full" preserveAspectRatio="none" viewBox="0 0 1000 200">
              <defs>
                <linearGradient id="chart-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stopColor="#001430" stopOpacity="0.1" />
                  <stop offset="100%" stopColor="transparent" />
                </linearGradient>
              </defs>
              <path d="M0,150 C100,140 200,180 300,120 C400,60 500,100 600,40 C700,-20 800,80 900,20 L1000,60" fill="none" stroke="#001430" strokeWidth="3" strokeLinecap="round" className="opacity-80" />
              <path d="M0,180 C150,170 250,190 350,140 C450,90 550,130 650,80 C750,30 850,110 950,50 L1000,90" fill="none" stroke="#b9c7e0" strokeWidth="2" strokeDasharray="6,4" strokeLinecap="round" />
              <path d="M0,150 C100,140 200,180 300,120 C400,60 500,100 600,40 C700,-20 800,80 900,20 L1000,60 L1000,200 L0,200 Z" fill="url(#chart-gradient)" className="opacity-60" />
            </svg>
            <span className="relative z-10 rounded bg-surface/80 px-2 py-1 text-label-sm text-on-surface-variant">
              Visualización D3.js / Recharts
            </span>
          </div>
        </div>

        {/* Data Grid — Mapeo de Alertas */}
        <div className="flex flex-col overflow-hidden rounded-xl border border-outline-variant bg-surface-container-lowest shadow-kpi">
          <div className="flex items-center justify-between border-b border-outline-variant bg-surface-container-lowest p-md">
            <h3 className="text-headline-sm text-on-background">Mapeo de Alertas Recientes</h3>
            <button type="button" className="flex items-center gap-1 text-label-sm text-primary transition-colors hover:text-primary-container">
              Ver reporte completo
              <Icon name="arrow_forward" className="text-[16px]" />
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
                    onClick={() => setSelectedStudent(alumno)}
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
      </div>

      {/* SideSheet — Student Detail */}
      <SideSheet
        open={!!selectedStudent}
        onClose={() => setSelectedStudent(null)}
        title={selectedStudent?.name ?? ''}
        breadcrumbs={[
          { label: 'Mapeo de Alertas' },
          { label: 'Detalle de Alumno' },
        ]}
        footer={
          <>
            <button
              type="button"
              onClick={() => setSelectedStudent(null)}
              className="rounded-lg border border-outline-variant bg-surface-container-lowest px-md py-2 text-label-sm text-on-surface-variant transition-colors hover:bg-surface-container-low"
            >
              Cerrar
            </button>
            <button
              type="button"
              className="rounded-lg bg-primary px-md py-2 text-label-sm text-on-primary shadow-sm transition-colors hover:bg-primary-container"
            >
              Generar Reporte PDF
            </button>
          </>
        }
      >
        {selectedStudent && (
          <div className="space-y-lg">
            {/* Student Meta Info */}
            <div className="grid grid-cols-2 gap-md">
              <div>
                <div className="text-label-sm text-on-surface-variant">Legajo</div>
                <div className="font-mono-code text-mono-code text-on-background">{selectedStudent.legajo}</div>
              </div>
              <div>
                <div className="text-label-sm text-on-surface-variant">Cohorte</div>
                <div className="font-mono-code text-mono-code text-on-background">{selectedStudent.cohorte}</div>
              </div>
              <div className="col-span-2">
                <div className="text-label-sm text-on-surface-variant">Carrera</div>
                <div className="text-body-md text-on-background">{selectedStudent.carrera}</div>
              </div>
            </div>

            {/* Risk Status Banner */}
            {selectedStudent.status === 'CRITICO' && (
              <div className="flex items-start gap-md rounded-lg border border-error/30 bg-error-container/20 p-md">
                <Icon name="warning" className="mt-0.5 text-error" />
                <div>
                  <h4 className="text-label-sm text-on-error-container">RIESGO DE DESERCIÓN CRÍTICO</h4>
                  <p className="mt-1 text-body-md text-on-surface-variant">
                    Ausencia prolongada en el campus virtual (Moodle) y falta de entregas en 3 materias troncales durante las últimas 2 semanas.
                  </p>
                </div>
              </div>
            )}

            {selectedStudent.status === 'ATRASADO' && (
              <div className="flex items-start gap-md rounded-lg border border-[#fef3c7]/30 bg-[#fff8e1]/50 p-md">
                <Icon name="schedule" className="mt-0.5 text-[#b45309]" />
                <div>
                  <h4 className="text-label-sm text-[#b45309]">RIESGO DE ATRASO MODERADO</h4>
                  <p className="mt-1 text-body-md text-on-surface-variant">
                    Entregas pendientes en 1 materia. Se recomienda contacto con el alumno para regularizar su situación.
                  </p>
                </div>
              </div>
            )}

            {/* Deep Dive Data */}
            <div>
              <h3 className="mb-md border-b border-outline-variant pb-1 text-label-sm text-on-surface-variant">MÉTRICAS DE COMPROMISO</h3>
              <div className="space-y-4">
                <div>
                  <div className="mb-1 flex justify-between text-label-sm">
                    <span className="text-on-background">Asistencia Promedio</span>
                    <span className={selectedStudent.status === 'CRITICO' ? 'text-error' : 'text-[#b45309]'}>
                      {selectedStudent.status === 'CRITICO' ? '42%' : '71%'}
                    </span>
                  </div>
                  <div className="h-1.5 w-full rounded-full bg-surface-container-high">
                    <div
                      className={`h-1.5 rounded-full ${selectedStudent.status === 'CRITICO' ? 'bg-error' : 'bg-[#b45309]'}`}
                      style={{ width: selectedStudent.status === 'CRITICO' ? '42%' : '71%' }}
                    />
                  </div>
                </div>
                <div>
                  <div className="mb-1 flex justify-between text-label-sm">
                    <span className="text-on-background">Entregas a Tiempo (TPs)</span>
                    <span className={selectedStudent.status === 'CRITICO' ? 'text-error' : 'text-[#15803d]'}>
                      {selectedStudent.status === 'CRITICO' ? '60%' : '94%'}
                    </span>
                  </div>
                  <div className="h-1.5 w-full rounded-full bg-surface-container-high">
                    <div
                      className={`h-1.5 rounded-full ${selectedStudent.status === 'CRITICO' ? 'bg-error' : 'bg-[#15803d]'}`}
                      style={{ width: selectedStudent.status === 'CRITICO' ? '60%' : '94%' }}
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Console / Audit Log area */}
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
        )}
      </SideSheet>
    </>
  )
}
