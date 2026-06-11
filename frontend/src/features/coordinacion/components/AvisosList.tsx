import type { AvisoResponse } from '../types'

interface Props {
  items: AvisoResponse[]
  onEdit?: (aviso: AvisoResponse) => void
  onDelete?: (id: string) => void
  onStats?: (id: string) => void
}

const severityColors: Record<string, string> = {
  INFO: 'bg-primary/10 text-primary',
  WARNING: 'bg-warning/10 text-warning',
  CRITICAL: 'bg-danger/10 text-danger',
}

const scopeLabels: Record<string, string> = {
  GENERAL: 'General',
  MATERIA: 'Por materia',
  COHORTE: 'Por cohorte',
  ROL: 'Por rol',
}

export function AvisosList({ items, onEdit, onDelete, onStats }: Props) {
  return (
    <div className="overflow-x-auto rounded-lg border border-border">
      <table className="w-full text-left text-sm">
        <thead>
          <tr className="border-b border-border bg-surface text-xs uppercase text-on-surface-muted">
            <th className="px-4 py-3">Título</th>
            <th className="px-4 py-3">Severidad</th>
            <th className="px-4 py-3">Alcance</th>
            <th className="px-4 py-3">Vigencia</th>
            <th className="px-4 py-3">Estado</th>
            <th className="px-4 py-3">Acciones</th>
          </tr>
        </thead>
        <tbody>
          {items.map((a) => (
            <tr key={a.id} className="border-b border-border last:border-b-0 hover:bg-surface-hover">
              <td className="px-4 py-3 font-medium text-on-surface">
                <div>{a.titulo}</div>
                <div className="mt-0.5 text-xs text-on-surface-muted line-clamp-1">{a.cuerpo}</div>
              </td>
              <td className="px-4 py-3">
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${severityColors[a.severidad]}`}>
                  {a.severidad}
                </span>
              </td>
              <td className="px-4 py-3 text-on-surface-muted">{scopeLabels[a.alcance] || a.alcance}</td>
              <td className="px-4 py-3 text-xs text-on-surface-muted">
                <div>{new Date(a.inicio_en).toLocaleDateString()}</div>
                <div>{new Date(a.fin_en).toLocaleDateString()}</div>
              </td>
              <td className="px-4 py-3">
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${a.activo ? 'bg-success/10 text-success' : 'bg-on-surface-muted/10 text-on-surface-muted'}`}>
                  {a.activo ? 'Activo' : 'Inactivo'}
                </span>
              </td>
              <td className="px-4 py-3">
                <div className="flex gap-2">
                  {onEdit && (
                    <button onClick={() => onEdit(a)} className="text-xs text-primary hover:underline">Editar</button>
                  )}
                  {onStats && (
                    <button onClick={() => onStats(a.id)} className="text-xs text-primary hover:underline">Stats</button>
                  )}
                  {onDelete && (
                    <button onClick={() => onDelete(a.id)} className="text-xs text-danger hover:underline">Eliminar</button>
                  )}
                </div>
              </td>
            </tr>
          ))}
          {items.length === 0 && (
            <tr>
              <td colSpan={6} className="px-4 py-8 text-center text-sm text-on-surface-muted">
                Sin avisos
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  )
}
