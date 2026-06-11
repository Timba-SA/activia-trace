import { useEffect, type ReactNode } from 'react'

function Icon({ name, className = '' }: { name: string; className?: string }) {
  return <span className={`material-symbols-outlined ${className}`}>{name}</span>
}

interface Breadcrumb {
  label: string
  href?: string
}

interface SideSheetProps {
  open: boolean
  onClose: () => void
  title: string
  breadcrumbs?: Breadcrumb[]
  children: ReactNode
  footer?: ReactNode
}

export function SideSheet({ open, onClose, title, breadcrumbs, children, footer }: SideSheetProps) {
  // Close on Escape key
  useEffect(() => {
    function handleKey(e: KeyboardEvent) {
      if (e.key === 'Escape') onClose()
    }
    if (open) document.addEventListener('keydown', handleKey)
    return () => document.removeEventListener('keydown', handleKey)
  }, [open, onClose])

  return (
    <>
      {/* Backdrop */}
      <div
        className={`fixed inset-0 z-50 bg-primary/20 backdrop-blur-sm transition-opacity duration-300 ${
          open ? 'opacity-100' : 'pointer-events-none opacity-0'
        }`}
        onClick={onClose}
      />

      {/* Sheet */}
      <aside
        className={`fixed right-0 top-0 z-50 flex h-full w-full flex-col border-l border-outline-variant bg-surface-container-lowest shadow-2xl transition-transform duration-300 ease-in-out sm:w-[40%] sm:min-w-[320px] sm:max-w-[600px] ${
          open ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-outline-variant bg-surface p-md">
          <div>
            {breadcrumbs && breadcrumbs.length > 0 && (
              <div className="mb-1 flex items-center gap-1 text-label-sm text-on-surface-variant">
                {breadcrumbs.map((crumb, i) => (
                  <span key={i} className="flex items-center gap-1">
                    {i > 0 && <Icon name="chevron_right" className="text-[14px]" />}
                    <span className={i === breadcrumbs.length - 1 ? 'text-primary' : ''}>
                      {crumb.label}
                    </span>
                  </span>
                ))}
              </div>
            )}
            <h2 className="text-headline-sm text-on-background">{title}</h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-full p-2 text-on-surface-variant transition-colors hover:bg-surface-container-high"
          >
            <Icon name="close" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-md">
          {children}
        </div>

        {/* Footer */}
        {footer && (
          <div className="flex justify-end gap-sm border-t border-outline-variant bg-surface p-md">
            {footer}
          </div>
        )}
      </aside>
    </>
  )
}
