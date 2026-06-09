## ADDED Requirements

### Requirement: Scaffold Vite + React 18 + TypeScript
The project SHALL use Vite as bundler with React 18 + TypeScript template. The entry point SHALL be `frontend/`. Tailwind CSS SHALL be configured with the tokens defined in `docs/DESIGN_SYSTEM.md` §8, including colors, typography (Inter + JetBrains Mono), spacing scale (4px base), and border radius tokens.

#### Scenario: Project boots with Vite dev server
- **WHEN** running `npm run dev` in `frontend/`
- **THEN** Vite starts the dev server on port 5173 and renders the React app

#### Scenario: Tailwind design tokens are available
- **WHEN** a component uses `bg-primary`, `font-sans`, or `text-headline-md`
- **THEN** Tailwind resolves to the correct Institutional Navy values (#002855, Inter, 32px)

### Requirement: Feature-based directory structure
The frontend SHALL be organized by feature modules under `frontend/src/features/{name}/`. Each feature SHALL contain subdirectories: `components/`, `hooks/`, `services/`, `types/`, `pages/`. Shared code (cliente HTTP, UI components, hooks) SHALL live in `frontend/src/shared/`.

#### Scenario: Auth feature structure
- **WHEN** inspecting `frontend/src/features/auth/`
- **THEN** it SHALL contain `components/`, `hooks/`, `services/`, `types/`, `pages/`

### Requirement: Layout with sidebar and content area
The application SHALL render a persistent layout: sidebar (280px, Institutional Navy #002855) on the left and a fluid content area on the right. The sidebar SHALL display navigation items filtered by the user's permissions. On tablet (768-1023px), the sidebar SHALL collapse to a 72px icon rail. On mobile (<768px), the sidebar SHALL be hidden and accessible via a hamburger drawer.

#### Scenario: Sidebar shows permitted menu items
- **WHEN** a user with roles `[PROFESOR]` logs in
- **THEN** the sidebar SHALL only show menu items whose required permissions are satisfied by the user's roles

#### Scenario: Sidebar collapses on tablet
- **WHEN** the viewport is between 768px and 1023px
- **THEN** the sidebar SHALL render as a 72px icon rail

### Requirement: Pages are lazy-loaded
All page components SHALL use React.lazy + Suspense for code splitting. Each feature's pages SHALL be imported lazily in the router configuration.

#### Scenario: Page loads on demand
- **WHEN** navigating to `/login`
- **THEN** the login page chunk SHALL be loaded asynchronously
