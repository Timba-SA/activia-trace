import { useState } from 'react'
import { useSession } from '@/features/auth/hooks/useAuth'
import { SideSheet } from '@/shared/components/ui/SideSheet'
import AlertasTable, { type StudentAlert } from '../components/AlertasTable'
import StudentDetail from '../components/StudentDetail'

function Icon({ name, className = '' }: { name: string; className?: string }) {
  return <span className={`material-symbols-outlined ${className}`}>{name}</span>
}

const alertas: StudentAlert[] = [
  { initials: 'MR', name: 'Martina Rossi', carrera: 'Ingeniería en Sistemas', cohorte: '2023-1', status: 'CRITICO', ultimaActividad: 'Hace 14 días', legajo: 'SYS-23-0045' },
  { initials: 'JG', name: 'Juan Gomez', carrera: 'Licenciatura en Adm.', cohorte: '2022-2', status: 'ATRASADO', ultimaActividad: 'Hace 5 días', legajo: 'ADM-22-0092' },
  { initials: 'AL', name: 'Ana Lopez', carrera: 'Ingeniería Industrial', cohorte: '2023-2', status: 'REGULAR', ultimaActividad: 'Hace 2 horas', legajo: 'IND-23-0118' },
  { initials: 'CP', name: 'Carlos Perez', carrera: 'Analista de Sistemas', cohorte: '2021-1', status: 'CRITICO', ultimaActividad: 'Hace 21 días', legajo: 'AS-21-0033' },
]

export default function HomePage() {
  const { data: session } = useSession()
  const [selectedStudent, setSelectedStudent] = useState<StudentAlert | null>(null)
  const userName = session?.nombre ?? session?.email ?? 'Usuario'

  return (
    <>
      <div className="space-y-lg">
        <div>
          <h2 className="text-display-lg text-on-background">Dashboard Analítico</h2>
          <p className="mt-1 text-body-md text-on-surface-variant">
            Bienvenido, {userName}. Visión general del rendimiento y alertas tempranas del período lectivo actual.
          </p>
        </div>

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
            <div className="absolute inset-0 opacity-30" style={{ backgroundImage: 'linear-gradient(to right, #e0e3e5 1px, transparent 1px), linear-gradient(to bottom, #e0e3e5 1px, transparent 1px)', backgroundSize: '2rem 2rem' }} />
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

        <AlertasTable alertas={alertas} onSelect={setSelectedStudent} />
      </div>

      <SideSheet
        open={!!selectedStudent}
        onClose={() => setSelectedStudent(null)}
        title={selectedStudent?.name ?? ''}
        breadcrumbs={[{ label: 'Mapeo de Alertas' }, { label: 'Detalle de Alumno' }]}
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
        {selectedStudent && <StudentDetail student={selectedStudent} />}
      </SideSheet>
    </>
  )
}
