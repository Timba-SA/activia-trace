## Context

C-21 entregó el shell completo: Layout, Auth, Router, Axios client. El backend académico (C-10 calificaciones, C-11 atrasados, C-12 comunicaciones) expone APIs REST para consumir. Este change construye las features de frontend del flujo PROFESOR: importar datos del LMS, analizar atrasados y comunicarse con alumnos.

El frontend sigue la estructura feature-based del proyecto: `features/{name}/{components,hooks,services,types,pages}`. Cada feature define sus propias rutas lazy-loadeadas. Los componentes compartidos (tablas, modales, side-sheets, botones, KPIs) se documentan en el Design System.

## Goals / Non-Goals

**Goals:**
- Cubrir el flujo completo FL-02 (importar → analizar → comunicar) para PROFESOR y TUTOR
- Reutilizar Layout, ProtectedRoute, Router y Axios de C-21 sin modificaciones
- TanStack Query para server state con stale-time agresivo (30s en datos importados, 5min en catálogos)
- Componentes modulares y testeables: tabla de atrasados, preview de importación, tracking de comunicaciones
- Side-sheet para preview de comunicación (reutilizando patrón de C-21)
- Exportación CSV de entregas sin corregir vía Blob download

**Non-Goals:**
- No incluye gestión de equipos docentes (C-23)
- No incluye avisos ni tareas internas (C-23)
- No incluye liquidaciones ni facturas (C-24)
- No incluye panel de auditoría (C-19, C-24)
- No incluye la vista COORDINADOR de monitores transversales (F2.7, F2.9) — esas van en C-23

## Decisions

| Decisión | Opción elegida | Alternativa | Razón |
|----------|---------------|-------------|-------|
| Feature splitting | 1 feature `academico` con sub-módulos internos | Feature separada por capacidad | Las pantallas comparten estado (materia/comisión seleccionada). Un solo contexto QueryClient permite invalidar queries relacionadas. |
| File upload | Axios multipart con preview local | Upload directo sin preview | La preview es requisito funcional (F1.1 paso 3). El backend ya devuelve actividades detectadas. El frontend renderiza la tabla y permite selección. |
| Tracking en tiempo real | Polling cada 5s con TanStack Query `refetchInterval` | WebSocket | La cola de comunicaciones tiene latencia de segundos, no milisegundos. Polling es más simple, no requiere conexión persistente, y TanStack Query cachea mientras el usuario navega. |
| Estado de comisión | Context de React (AcademicoProvider) | Redux/Zustand/URL params | Scope acotado a `features/academico/`. Context evita prop drilling materia/cohorte/periodo entre páginas. El estado se resetea al salir de la feature. |
| CSV export | Blob + `<a download>` client-side | Backend genera CSV | La data ya está en el frontend (desde TanStack Query cache). Evita un viaje al backend. |

## Component Architecture

```
features/academico/
├── components/
│   ├── ComisionSelector.tsx        # Selector materia × cohorte
│   ├── DashboardMetrics.tsx        # KPIs: total alumnos, atrasados, actividades
│   ├── ImportPreview.tsx           # Preview de actividades detectadas + checkboxes
│   ├── UmbralConfig.tsx            # Slider/input de porcentaje
│   ├── AtrasadosTable.tsx          # Tabla de alumnos atrasados filtrable
│   ├── RankingTable.tsx            # Ranking de actividades aprobadas
│   ├── NotasFinalesTable.tsx       # Nota final agrupada por alumno
│   ├── EntregasSinCorregir.tsx     # Tabla + botón export CSV
│   ├── ComunicacionPreview.tsx     # Side-sheet con preview de mensaje
│   ├── ComunicacionTracking.tsx    # Timeline de estados de envío
│   └── MonitoreoAlumnos.tsx        # Vista filtrable TUTOR/PROFESOR
├── hooks/
│   ├── useComision.ts             # Estado de comisión seleccionada (context consumer)
│   ├── useCalificaciones.ts       # GET /calificaciones, POST /calificaciones/importar
│   ├── useUmbral.ts              # GET/PUT /umbral
│   ├── useAtrasados.ts           # GET /atrasados
│   ├── useRanking.ts             # GET /ranking
│   ├── useNotasFinales.ts        # GET /notas-finales
│   ├── useEntregasSinCorregir.ts # GET /entregas-sin-corregir
│   ├── useComunicaciones.ts      # POST comunicacion/preview, POST comunicacion/enviar, GET tracking
│   └── useMonitoreo.ts           # GET /monitoreo
├── services/
│   └── api.ts                     # Endpoints específicos del feature
├── types/
│   └── index.ts                   # Interfaces de dominio
├── pages/
│   ├── ComisionPage.tsx           # Dashboard de comisión seleccionada
│   ├── CalificacionesPage.tsx     # Upload + preview + selección
│   ├── AtrasadosPage.tsx          # Atrasados + umbral + ranking
│   ├── NotasFinalesPage.tsx       # Notas finales
│   ├── EntregasPage.tsx           # Entregas sin corregir + export
│   ├── ComunicacionPage.tsx       # Preview + envío + tracking
│   └── MonitoreoPage.tsx          # Seguimiento de alumnos
└── context/
    └── AcademicoContext.tsx        # Estado compartido (comisión seleccionada)
```

## Router Structure

```
/                           → Home
/academico                  → ComisionSelector (si no hay comisión seleccionada)
/academico/:materiaId/:cohorteId
  /                         → ComisionPage (dashboard)
  /calificaciones           → CalificacionesPage
  /atrasados                → AtrasadosPage + UmbralConfig
  /notas-finales            → NotasFinalesPage
  /entregas                 → EntregasPage
  /comunicaciones           → ComunicacionPage
  /monitoreo                → MonitoreoPage
```

Todas las rutas bajo `/academico` llevan `ProtectedRoute` con `calificaciones:ver` o `calificaciones:importar` según la página.

## Data Flow

1. Usuario selecciona materia + cohorte → `AcademicoContext` actualiza → todas las queries se disparan con esos params
2. TanStack Query cachea respuestas. Stale times: catálogos (materias/cohortes) = 5min, datos importados = 30s
3. Upload de calificaciones: `POST /calificaciones/importar` (multipart) → preview devuelta → usuario selecciona actividades → `POST /calificaciones/confirmar`
4. Comunicaciones: `POST /comunicacion/preview` → side-sheet → usuario confirma → `POST /comunicacion/enviar` → tracking con `refetchInterval: 5000`
5. Export CSV: datos desde cache → formateo client-side → Blob download

## API Endpoints Consumidos

| Método | Endpoint | Feature | Notas |
|--------|----------|---------|-------|
| GET | `/api/materias` | ComisionSelector | Catálogo, cache 5min |
| GET | `/api/cohortes` | ComisionSelector | Catálogo, cache 5min |
| GET | `/api/calificaciones?materia_id=&cohorte_id=` | Dashboard/Atrasados | |
| POST | `/api/calificaciones/importar` | CalificacionesPage | multipart, devuelve preview |
| POST | `/api/calificaciones/confirmar` | CalificacionesPage | Actividades seleccionadas |
| DELETE | `/api/calificaciones/vaciar` | CalificacionesPage | F1.5 |
| GET/PUT | `/api/umbral?materia_id=` | UmbralConfig | |
| GET | `/api/atrasados?materia_id=&cohorte_id=` | AtrasadosPage | |
| GET | `/api/ranking?materia_id=&cohorte_id=` | RankingTable | |
| GET | `/api/notas-finales?materia_id=&cohorte_id=` | NotasFinalesPage | |
| GET | `/api/entregas-sin-corregir?materia_id=&cohorte_id=` | EntregasPage | |
| POST | `/api/comunicacion/preview` | ComunicacionPage | Body: alumno_ids + template |
| POST | `/api/comunicacion/enviar` | ComunicacionPage | |
| GET | `/api/comunicacion/tracking?lote_id=` | ComunicacionTracking | refetchInterval: 5000 |
| GET | `/api/monitoreo?materia_id=&cohorte_id=` | MonitoreoPage | |

## Risks / Trade-offs

- [Risk] Polling cada 5s en tracking de comunicaciones → [Mitigation] `refetchInterval` con `enabled: bool`, solo activo mientras la página está visible. TanStack Query pausa al perder focus del tab.
- [Risk] Upload de archivos grandes sin barra de progreso → [Mitigation] Axios `onUploadProgress` en el interceptor si el archivo > 5MB.
- [Risk] Preview de importación con muchas actividades → [Mitigation] Virtual scrolling si > 20 filas (react-window si es necesario, inicialmente scroll nativo).
- [Trade-off] Context en vez de URL params para comisión seleccionada → más fácil de compartir entre componentes anidados, pero se pierde al refrescar. Se soluciona guardando en sessionStorage como fallback.
