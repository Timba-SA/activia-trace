import { useState } from 'react'
import SalarioBaseTab from '../components/SalarioBaseTab'
import SalarioPlusTab from '../components/SalarioPlusTab'

type Tab = 'base' | 'plus' | 'materia-grupo'

export default function GrillaSalarialPage() {
  const [tab, setTab] = useState<Tab>('base')

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-primary">Grilla Salarial</h2>
      </div>

      <nav className="flex gap-1 border-b border-border">
        {([
          { key: 'base' as const, label: 'Salarios Base' },
          { key: 'plus' as const, label: 'Plus' },
          { key: 'materia-grupo' as const, label: 'Materia-Grupo' },
        ]).map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`-mb-px border-b-2 px-4 py-2 text-sm transition-colors ${
              tab === t.key
                ? 'border-primary text-primary'
                : 'border-transparent text-on-surface-muted hover:text-on-surface'
            }`}
          >
            {t.label}
          </button>
        ))}
      </nav>

      {tab === 'base' && <SalarioBaseTab />}
      {tab === 'plus' && <SalarioPlusTab />}
      {tab === 'materia-grupo' && (
        <p className="text-sm text-on-surface-muted">
          La gestión de Materia-Grupo Plus está disponible en el endpoint <code className="rounded bg-surface-hover px-1 py-0.5 font-mono text-xs">/liquidaciones/materias-grupo</code>.
          Consultá la documentación de la API para más detalles.
        </p>
      )}
    </div>
  )
}
