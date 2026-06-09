import type { ComunicacionTracking as TrackingType } from '../types'

export function ComunicacionTracking({ data }: { data: TrackingType }) {
  const counts = {
    ok: data.items.filter((i) => i.estado === 'ok').length,
    fallido: data.items.filter((i) => i.estado === 'fallido').length,
    cancelado: data.items.filter((i) => i.estado === 'cancelado').length,
    pendiente: data.items.filter((i) => i.estado === 'pendiente' || i.estado === 'enviando').length,
  }
  const terminado = counts.pendiente === 0

  return (
    <div className="space-y-3">
      {terminado && (
        <div className="rounded bg-success/10 p-3 text-sm text-success">
          Comunicación finalizada: {counts.ok} enviados, {counts.fallido} fallidos, {counts.cancelado} cancelados
        </div>
      )}
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border text-left text-xs uppercase text-on-surface-muted">
            <th className="px-2 py-2">Alumno</th>
            <th className="px-2 py-2">Estado</th>
          </tr>
        </thead>
        <tbody>
          {data.items.map((item) => (
            <tr key={item.alumno_id} className="border-b border-border">
              <td className="px-2 py-2">{item.alumno_nombre}</td>
              <td className="px-2 py-2">
                <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${
                  item.estado === 'ok' ? 'bg-success/10 text-success' :
                  item.estado === 'fallido' ? 'bg-danger/10 text-danger' :
                  item.estado === 'cancelado' ? 'bg-on-surface-muted/10 text-on-surface-muted' :
                  item.estado === 'enviando' ? 'bg-warning/10 text-warning' :
                  'bg-on-surface-muted/10 text-on-surface-muted'
                }`}>
                  {item.estado === 'ok' ? 'Enviado' :
                   item.estado === 'fallido' ? 'Fallido' :
                   item.estado === 'cancelado' ? 'Cancelado' :
                   item.estado === 'enviando' ? 'Enviando' : 'Pendiente'}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
