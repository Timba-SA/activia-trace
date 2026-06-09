# Design System — Active Trace (Institutional Navy)

> Design system oficial del frontend de **activia-trace**. Generado desde Stitch (Google Design AI) como parte de la fundación del proyecto.
> Versión canónica en el proyecto Stitch: `projects/16132595247646015374`

---

## 1. Filosofía de Diseño

El sistema está diseñado para auditoría académica de alto riesgo y analytics predictivos. Adopta una estética **Corporate / Modern** con inclinación **Minimalista**, priorizando la claridad de datos sobre elementos decorativos. La personalidad de marca es **autoritaria, precisa y transparente**, orientada a administradores institucionales y analistas de datos.

La jerarquía visual se establece mediante tipografía meticulosa y una paleta de colores contenida, asegurando que conjuntos de datos multi-tenant complejos sigan siendo legibles. La respuesta emocional debe ser de "inteligencia controlada" — un entorno silencioso y robusto donde la UI se repliega para que los insights ocupen el centro.

---

## 2. Colores

Paleta de alto contraste institucional. Modo **claro** solamente (por ahora).

### 2.1 Paleta Completa

| Token                         | Hex       | Uso                                |
| ----------------------------- | --------- | ---------------------------------- |
| **primary**                   | `#002855` | Navigation, primary actions, brand |
| **on-primary**                | `#ffffff` | Texto sobre primary                |
| **primary-container**         | `#002855` | Fondo de contenedores primarios    |
| **on-primary-container**      | `#7490c3` | Texto sobre primary-container      |
| **primary-fixed**             | `#d6e3ff` | Variante clara de primary          |
| **primary-fixed-dim**         | `#aac7fd` | Versión tenue                      |
| **secondary**                 | `#334155` | Body text, borders (Slate)         |
| **on-secondary**              | `#ffffff` | Texto sobre secondary              |
| **secondary-container**       | `#d5e3fd` | Fondo secundario                   |
| **tertiary**                  | `#64748b` | Acentos terciarios                 |
| **surface**                   | `#f7f9fb` | Canvas principal                   |
| **surface-dim**               | `#d8dadc` | Superficie atenuada                |
| **surface-bright**            | `#f7f9fb` | Superficie brillante               |
| **surface-container**         | `#eceef0` | Contenedores                       |
| **surface-container-low**     | `#f2f4f6` | Contenedores bajos                 |
| **surface-container-high**    | `#e6e8ea` | Contenedores altos                 |
| **surface-container-highest** | `#e0e3e5` | Contenedores muy altos             |
| **surface-container-lowest**  | `#ffffff` | Cards, data containers             |
| **on-surface**                | `#191c1e` | Texto principal                    |
| **on-surface-variant**        | `#43474f` | Texto secundario                   |
| **inverse-surface**           | `#2d3133` | Superficie invertida (dark)        |
| **inverse-on-surface**        | `#eff1f3` | Texto sobre inverse                |
| **inverse-primary**           | `#aac7fd` | Primary en modo invertido          |
| **outline**                   | `#747780` | Bordes                             |
| **outline-variant**           | `#c4c6d0` | Bordes tenues                      |
| **error**                     | `#ba1a1a` | Errores                            |
| **on-error**                  | `#ffffff` | Texto sobre error                  |
| **error-container**           | `#ffdad6` | Fondo de error                     |
| **on-error-container**        | `#93000a` | Texto sobre error-container        |
| **background**                | `#f7f9fb` | Fondo general                      |

### 2.2 Reglas de Color

- **Semántica**: Los colores Emerald, Amber y Rose se usan **exclusivamente** para indicadores de estado y outliers. Aplicar con fondo de baja saturación + ícono/texto de alta saturación.
- **Fondo**: Gris claro frío (`#f7f9fb`) para reducir fatiga visual en sesiones analíticas prolongadas.
- **Cards**: Blanco puro (`#ffffff`) con borde de 1px (`#e2e8f0`).

---

## 3. Tipografía

### 3.1 Stack

- **UI General**: **Inter** — legibilidad excepcional en tamaños pequeños y altas resoluciones.
- **Console / Código**: **JetBrains Mono** — para logs de API, auditorías técnicas y metadata.

### 3.2 Escala Tipográfica

| Nivel           | Font Size | Weight          | Line Height | Letter Spacing | Font Family    |
| --------------- | --------- | --------------- | ----------- | -------------- | -------------- |
| **display-lg**  | 32px      | 600 (Semi Bold) | 40px        | -0.02em        | Inter          |
| **headline-md** | 24px      | 600 (Semi Bold) | 32px        | -0.01em        | Inter          |
| **headline-sm** | 20px      | 500 (Medium)    | 28px        | normal         | Inter          |
| **body-lg**     | 16px      | 400 (Regular)   | 24px        | normal         | Inter          |
| **body-md**     | 14px      | 400 (Regular)   | 20px        | normal         | Inter          |
| **label-sm**    | 12px      | 600 (Semi Bold) | 16px        | 0.05em         | Inter          |
| **mono-code**   | 13px      | 400 (Regular)   | 20px        | normal         | JetBrains Mono |

### 3.3 Reglas Tipográficas

- **Cuerpo base**: `body-md` (14px) para máxima densidad de información sin perder legibilidad.
- **Headlines**: Semi-bold con tracking negativo leve para mantener aspecto compacto y profesional.
- **Console**: Fondo oscuro (`#0F172A` - Slate-900) para diferenciar metadata técnica de datos institucionales.

---

## 4. Layout & Spacing

### 4.1 Grid System

Sistema de **Fluid Grid** con restricciones de ancho fijo para navegación.

```
┌─────────────┬────────────────────────────────────────┐
│  Sidebar    │          Content Area                  │
│  280px fijo │      12-column fluid grid              │
│             │                                        │
│  (#002855)  │  ┌──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┐ │
│             │  │  │  │  │  │  │  │  │  │  │  │  │  │ │
│             │  └──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┘ │
└─────────────┴────────────────────────────────────────┘
```

### 4.2 Spacing Scale

Base unit: **4px**

| Token           | Value | Uso                              |
| --------------- | ----- | -------------------------------- |
| `xs`            | 4px   | Espaciado mínimo                 |
| `sm`            | 8px   | Padding interno compacto         |
| `md`            | 16px  | Padding estándar dentro de cards |
| `lg`            | 24px  | Margen entre bloques principales |
| `xl`            | 32px  | Espaciado de secciones           |
| `sidebar-width` | 280px | Ancho del panel de navegación    |
| `gutter`        | 20px  | Separación entre columnas        |

### 4.3 Responsive Breakpoints

| Dispositivo       | Sidebar           | Content        |
| ----------------- | ----------------- | -------------- |
| Desktop ≥1024px   | 280px (expandido) | 12-column grid |
| Tablet 768-1023px | 72px (icon rail)  | 8-column grid  |
| Mobile <768px     | Hidden (drawer)   | 4-column stack |

---

## 5. Elevation & Profundidad

La profundidad se comunica mediante **capas tonales** y **bordes de bajo contraste**, no sombras pesadas.

| Elemento               | Técnica                                                            |
| ---------------------- | ------------------------------------------------------------------ |
| Canvas                 | `surface` (#f7f9fb)                                                |
| Cards, grids           | `surface-container-lowest` (#ffffff) + borde 1px `outline-variant` |
| KPI Cards interactivos | Sombra difusa: `0px 4px 12px rgba(0, 40, 85, 0.05)`                |
| Side-sheets            | Fondo semitransparente (#002855 al 20%)                            |

---

## 6. Shapes (Border Radius)

| Elemento            | Radius        | Clase Tailwind |
| ------------------- | ------------- | -------------- |
| Botones, inputs     | 4px (0.25rem) | `rounded`      |
| Cards, contenedores | 8px (0.5rem)  | `rounded-lg`   |
| Chips, badges       | Pill (full)   | `rounded-full` |

---

## 7. Componentes

### 7.1 Data Grids

- Row height: **40px** (standard) / **48px** (comfortable)
- Hover: `Slate-100` (#f1f5f9)
- Column headers: `label-sm` + borde inferior sutil
- Sin rayas alternadas (mejor legibilidad con hover)

### 7.2 Sidebar Navigation

- Background: **Institutional Navy** (`#002855`)
- Active state: barra izquierda de 4px en `info blue` + overlay blanco 10%
- Texto: `on-primary` (#ffffff)
- Collapsible a icon rail (72px) en tablet

### 7.3 KPI Cards

- Background: white (`surface-container-lowest`)
- Border radius: 8px (`rounded-lg`)
- Border: 1px `outline-variant`
- Headline: `label-sm` en `on-surface-variant`
- Metric: `headline-md`
- Sparkline: 24px de alto para tendencias predictivas

### 7.4 Side-sheets (Modals)

- Ancho: **40%** del viewport
- Entrada: desde la derecha
- Header: breadcrumb + botón cerrar
- Backdrop: #002855 al 20%

### 7.5 Botones

| Variante      | Background          | Border                                | Texto                |
| ------------- | ------------------- | ------------------------------------- | -------------------- |
| **Primary**   | `primary` (#002855) | None                                  | `on-primary` (#fff)  |
| **Secondary** | White               | 1px `outline`, btn-hover bg `#f8fafc` | `on-surface`         |
| **Ghost**     | Transparent         | None, hover bg `#f1f5f9`              | `on-surface-variant` |

### 7.6 Console (Logs / Auditoría)

- Background: `#0F172A` (Slate-900)
- Font: `mono-code` (JetBrains Mono, 13px)
- Syntax highlighting: "Midnight" theme (colores desaturados de la paleta semántica)

---

## 8. Implementación en Tailwind CSS

Al configurar Tailwind, mapear estos tokens en `tailwind.config.ts`:

```typescript
// tailwind.config.ts — Design System Active Trace
export default {
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#002855",
          container: "#002855",
          fixed: "#d6e3ff",
          "fixed-dim": "#aac7fd",
          "on-container": "#7490c3",
          inverse: "#aac7fd",
        },
        secondary: {
          DEFAULT: "#334155",
          container: "#d5e3fd",
          "on-container": "#57657b",
        },
        tertiary: {
          DEFAULT: "#64748b",
          container: "#1a2a3e",
          "on-container": "#8191a9",
        },
        surface: {
          DEFAULT: "#f7f9fb",
          dim: "#d8dadc",
          bright: "#f7f9fb",
          container: "#eceef0",
          "container-low": "#f2f4f6",
          "container-high": "#e6e8ea",
          "container-highest": "#e0e3e5",
          "container-lowest": "#ffffff",
        },
        "on-surface": {
          DEFAULT: "#191c1e",
          variant: "#43474f",
        },
        inverse: {
          surface: "#2d3133",
          "on-surface": "#eff1f3",
        },
        outline: {
          DEFAULT: "#747780",
          variant: "#c4c6d0",
        },
        error: {
          DEFAULT: "#ba1a1a",
          container: "#ffdad6",
          "on-container": "#93000a",
        },
        background: "#f7f9fb",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      fontSize: {
        "display-lg": [
          "32px",
          { lineHeight: "40px", fontWeight: "600", letterSpacing: "-0.02em" },
        ],
        "headline-md": [
          "24px",
          { lineHeight: "32px", fontWeight: "600", letterSpacing: "-0.01em" },
        ],
        "headline-sm": ["20px", { lineHeight: "28px", fontWeight: "500" }],
        "body-lg": ["16px", { lineHeight: "24px", fontWeight: "400" }],
        "body-md": ["14px", { lineHeight: "20px", fontWeight: "400" }],
        "label-sm": [
          "12px",
          { lineHeight: "16px", fontWeight: "600", letterSpacing: "0.05em" },
        ],
        "mono-code": ["13px", { lineHeight: "20px", fontWeight: "400" }],
      },
      spacing: {
        xs: "4px",
        sm: "8px",
        md: "16px",
        lg: "24px",
        xl: "32px",
        sidebar: "280px",
        gutter: "20px",
      },
      borderRadius: {
        DEFAULT: "0.25rem", // 4px — botones, inputs
        lg: "0.5rem", // 8px — cards
      },
      boxShadow: {
        kpi: "0px 4px 12px rgba(0, 40, 85, 0.05)",
      },
    },
  },
};
```

---

## 9. Design Tokens (JSON)

Para consumo programático desde diseño o herramientas:

```json
{
  "primary": "#002855",
  "secondary": "#334155",
  "tertiary": "#64748b",
  "neutral": "#f8fafc",
  "surface": "#f7f9fb",
  "surface-container-lowest": "#ffffff",
  "on-surface": "#191c1e",
  "on-surface-variant": "#43474f",
  "outline": "#747780",
  "outline-variant": "#c4c6d0",
  "error": "#ba1a1a",
  "font-family-base": "Inter",
  "font-family-mono": "JetBrains Mono",
  "font-size-base": "14px",
  "border-radius-sm": "0.25rem",
  "border-radius-lg": "0.5rem",
  "spacing-unit": "4px",
  "sidebar-width": "280px"
}
```

---

## 10. Recursos

- **Proyecto Stitch**: `projects/16132595247646015374` (Active Trace Auditor Dashboard)
- **Design system asset**: `assets/15996705518239280238`
- **DESIGN.md original**: incrustado en el proyecto Stitch con especificaciones completas de brand, componentes y comportamiento responsive.
