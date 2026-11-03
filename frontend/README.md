# Frontend

```text
app/                       Next.js routes, metadata, global CSS entrypoint
features/editor/
  editor.tsx               assembling the editor screen
  components/              header, library, canvas, inspector, loading overlay
  hooks/use-editor.ts      scene state and user actions
  lib/api.ts               HTTP transport and response validation
  lib/export-svg.ts        standalone vector export
  lib/scene.ts             pure group geometry operations
  lib/library.ts           catalog and UI names
  lib/types.ts             scene object type
styles/editor.css          component and workspace styles
styles/responsive.css      viewport adaptation and reduced-motion rules
shared/palettes.json       original palettes shared with the backend
public/assets/             prepared SVG variants
tests/                     geometry invariants without browser or AI calls
```

```powershell
npm ci
npm run dev
npm run check
npm run build
```

`check` runs Prettier, strict TypeScript and Node tests. Next.js/React/tool versions are pinned in package.json and package-lock.json. The screen is an SVG editor; generated raster images and canvas screenshots are never used in SVG export.
