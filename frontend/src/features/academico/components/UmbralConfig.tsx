import { useSetUmbral, useUmbral } from '../hooks/useAcademico'

export function UmbralConfig() {
  const { data: umbral, isLoading } = useUmbral()
  const setUmbral = useSetUmbral()

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const v = Number(e.target.value)
    if (v >= 0 && v <= 100) {
      setUmbral.mutate(v)
    }
  }

  if (isLoading) return <div className="h-8 w-32 animate-pulse rounded bg-border" />

  return (
    <div className="flex items-center gap-3">
      <label className="text-sm text-on-surface">Umbral de aprobación:</label>
      <div className="flex items-center gap-2">
        <input
          type="range"
          min="0"
          max="100"
          value={umbral?.porcentaje ?? 60}
          onChange={handleChange}
          className="w-32"
        />
        <span className="min-w-[3ch] text-sm font-semibold text-primary">{umbral?.porcentaje ?? 60}%</span>
      </div>
    </div>
  )
}
