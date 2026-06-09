import { useNavigate } from 'react-router-dom'
import { useMaterias, useCohortes, useComision } from '../hooks/useAcademico'

export function ComisionSelector() {
  const navigate = useNavigate()
  const { data: materias } = useMaterias()
  const { data: cohortes } = useCohortes()
  const { setComision } = useComision()

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const fd = new FormData(e.currentTarget)
    const m = fd.get('materia_id') as string
    const c = fd.get('cohorte_id') as string
    if (m && c) {
      setComision(m, c)
      navigate(`/academico/${m}/${c}`)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="mx-auto max-w-md space-y-4 rounded-lg bg-surface p-6 shadow-kpi">
      <h2 className="text-lg font-semibold text-primary">Seleccionar comisión</h2>
      <div>
        <label className="mb-1 block text-sm text-on-surface">Materia</label>
        <select name="materia_id" required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm">
          <option value="">Seleccionar materia</option>
          {materias?.filter((m) => m.activa).map((m) => (
            <option key={m.id} value={m.id}>{m.nombre}</option>
          ))}
        </select>
      </div>
      <div>
        <label className="mb-1 block text-sm text-on-surface">Cohorte</label>
        <select name="cohorte_id" required className="w-full rounded border border-border bg-surface px-3 py-2 text-sm">
          <option value="">Seleccionar cohorte</option>
          {cohortes?.filter((c) => c.activa).map((c) => (
            <option key={c.id} value={c.id}>{c.nombre}</option>
          ))}
        </select>
      </div>
      <button type="submit" className="w-full rounded bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:bg-primary-hover">
        Ingresar
      </button>
    </form>
  )
}
