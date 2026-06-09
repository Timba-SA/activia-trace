import { Link, Outlet, useParams } from 'react-router-dom'
import { useComision } from '../hooks/useAcademico'
import { useEffect } from 'react'
import { AcademicoProvider } from '../context/AcademicoContext'
import { ComisionSelector } from '../components/ComisionSelector'

function AcademicoLayout() {
  const { materiaId, cohorteId, setComision } = useComision()
  const params = useParams()

  useEffect(() => {
    if (params.materiaId && params.cohorteId) {
      setComision(params.materiaId, params.cohorteId)
    }
  }, [params.materiaId, params.cohorteId, setComision])

  if (!materiaId || !cohorteId) {
    return <ComisionSelector />
  }

  const base = `/academico/${materiaId}/${cohorteId}`
  const links = [
    { to: base, label: 'Dashboard' },
    { to: `${base}/calificaciones`, label: 'Calificaciones' },
    { to: `${base}/atrasados`, label: 'Atrasados' },
    { to: `${base}/notas-finales`, label: 'Notas finales' },
    { to: `${base}/entregas`, label: 'Entregas' },
    { to: `${base}/comunicaciones`, label: 'Comunicaciones' },
    { to: `${base}/monitoreo`, label: 'Monitoreo' },
  ]

  return (
    <div className="space-y-6">
      <nav className="flex gap-1 overflow-x-auto border-b border-border pb-1">
        {links.map((l) => (
          <Link key={l.to} to={l.to} className="whitespace-nowrap rounded-t px-3 py-2 text-sm text-on-surface-muted hover:bg-surface-hover hover:text-on-surface aria-[current=page]:border-b-2 aria-[current=page]:border-primary aria-[current=page]:text-primary">
            {l.label}
          </Link>
        ))}
      </nav>
      <Outlet />
    </div>
  )
}

export default function AcademicoRootPage() {
  return (
    <AcademicoProvider>
      <AcademicoLayout />
    </AcademicoProvider>
  )
}
