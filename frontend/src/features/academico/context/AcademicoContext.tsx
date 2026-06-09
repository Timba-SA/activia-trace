import { createContext, useContext, useState, useCallback, type ReactNode } from 'react'

interface AcademicoState {
  materiaId: string | null
  cohorteId: string | null
  setComision: (materiaId: string, cohorteId: string) => void
  clear: () => void
}

const AcademicoContext = createContext<AcademicoState | null>(null)

const STORAGE_KEY = 'academico_comision'

function loadFromStorage(): { materiaId: string | null; cohorteId: string | null } {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    if (raw) return JSON.parse(raw)
  } catch { /* ignore */ }
  return { materiaId: null, cohorteId: null }
}

function saveToStorage(materiaId: string, cohorteId: string) {
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify({ materiaId, cohorteId }))
}

export function AcademicoProvider({ children }: { children: ReactNode }) {
  const stored = loadFromStorage()
  const [materiaId, setMateriaId] = useState<string | null>(stored.materiaId)
  const [cohorteId, setCohorteId] = useState<string | null>(stored.cohorteId)

  const setComision = useCallback((mid: string, cid: string) => {
    setMateriaId(mid)
    setCohorteId(cid)
    saveToStorage(mid, cid)
  }, [])

  const clear = useCallback(() => {
    setMateriaId(null)
    setCohorteId(null)
    sessionStorage.removeItem(STORAGE_KEY)
  }, [])

  return (
    <AcademicoContext.Provider value={{ materiaId, cohorteId, setComision, clear }}>
      {children}
    </AcademicoContext.Provider>
  )
}

export function useComision(): AcademicoState {
  const ctx = useContext(AcademicoContext)
  if (!ctx) throw new Error('useComision must be used within AcademicoProvider')
  return ctx
}
