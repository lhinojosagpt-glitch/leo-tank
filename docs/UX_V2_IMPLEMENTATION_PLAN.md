# TANK650 ENGINE v0.2 - UX implementation plan

**Date:** 2026-10-04  
**Baseline commit:** `dda226a`  
**Scope:** UX/UI, geometry information model and 3D representation. The calculation formulas and golden values are frozen unless a separately demonstrated defect is found.

## 1. Baseline evidence

Before changing code:

```text
pytest: 9 passed
warning: Starlette TestClient/httpx deprecation only
```

The current implementation was inspected in:

- `frontend/src/App.tsx`
- `frontend/src/viewer/TankViewer.tsx`
- `frontend/src/styles.css`
- `backend/app/api/router.py`
- `backend/app/geometry/spec.py`
- `data/fixtures/T78_2019.json`
- both AFC plate-layout drawings

## 2. Confirmed UX causes

1. The left navigation has no event handler; the Shell row is hard-coded as active.
2. `App.tsx` owns loading, editing, persistence, calculation, navigation, results and trace display in one component.
3. Only four inputs are exposed (`D`, `H`, `G`, `Sp`).
4. The trace panel is outside the main workspace grid, which creates global vertical scrolling.
5. Saving does call the API, but response status is not checked and feedback is only placed in the bottom status bar.
6. Edits made before a result exists do not set `dirty`, because the current code uses `setDirty(Boolean(result))`.
7. Saving with no changes is allowed and silently creates another revision.
8. Direct calculation does not create a persisted immutable run; persisted runs require a saved revision.
9. The 3D shell is eight continuous cylinders, not plate entities.
10. The roof is a compressed spherical fragment placed as a floating shell and has no geodesic frame.
11. Selection changes only course opacity and does not expose a synchronized engineering entity.

## 3. Drawing findings

### Shell drawing

The AFC cylinder-development drawing confirms:

- 8 courses;
- course height 2400 mm;
- 24 plates per course;
- procurement plates described as 6000 x 2400 mm;
- 192 shell plates total;
- vertical seams staggered between adjacent courses;
- thicknesses 25, 22, 19, 16, 12.7, 9.5, 8 and 8 mm.

For the visual model, every course will therefore contain 24 selectable plate sectors. Adjacent courses will use a half-plate angular offset. Because the drawing contains closure/cut dimensions that are not identical to 6000 mm, the model will retain both the 6000 mm nominal procurement width and the developed equal-sector width, and will label the visualization `AFC-informed representative` rather than pretending to be a fabrication cutting model.

### Bottom drawing

The bottom drawing confirms:

- a visually distinct annular ring and central bottom;
- central rows with staggered transverse joints;
- a central sump;
- 1% slope toward the center;
- a schedule containing 115 central 6000 x 2400 plates, 12 annular 6000 x 2400 plates and 5 smaller closure plates.

V0.2 will show annular/central zones, sump, slope indication and representative primary seams. It will not claim to be a complete fabrication nesting model.

## 4. Target information architecture

The SPA remains a single React application but adopts route-like workspaces:

```text
/project/local/overview
/project/local/design/geometry
/project/local/design/product
/project/local/design/materials
/project/local/design/shell
/project/local/design/bottom
/project/local/design/wind
/project/local/design/seismic
/project/local/design/roof
/project/local/design/anchorage
/project/local/review
/project/local/results
/project/local/variants
/project/local/history
```

The application shell will use a fixed viewport with internal panel scrolling:

```text
top bar
module navigation | main workspace | contextual inspector
status bar
```

## 5. Frontend decomposition

Planned source structure:

```text
src/app/AppShell.tsx
src/app/config.ts
src/app/state/useTankWorkspace.ts
src/modules/ModuleWorkspace.tsx
src/modules/fieldDefinitions.ts
src/modules/ShellWorkspace.tsx
src/modules/SeismicWorkspace.tsx
src/modules/ReviewWorkspace.tsx
src/modules/HistoryWorkspace.tsx
src/viewer/TankViewer.tsx
src/viewer/ModelBrowser.tsx
src/inspector/ResultInspector.tsx
src/inspector/CalculationInspector.tsx
src/shared/Status.tsx
src/shared/Toast.tsx
```

`App.tsx` will become a thin application entry point.

## 6. State model

The UI will keep these concepts separate:

- `persistedRevision`
- `persistedInputs`
- `draftInputs`
- `activeRun`
- `activeModule`
- `activeMode` (`inputs`, `results`, `checks`)
- `selectedEntity`
- `selectedTrace`
- `calculationInspector`
- `busyAction`
- `toast`

Dirty state will be computed against the persisted snapshot, not inferred from whether a result exists.

## 7. Save and calculate workflow

### Save revision

- Initial fixture -> Save creates `R1`.
- Edited saved revision -> Save creates an immutable successor.
- No changes -> visible toast; no API write.
- HTTP failures -> visible error toast.
- Success -> revision badge and history update without full refresh.

### Calculate

- Immediate `Validating...` then `Calculating...` feedback.
- A clean saved revision creates a persisted immutable run through the existing run endpoint.
- An unsaved draft may be calculated directly, but is clearly labeled as a draft result and does not masquerade as a persisted run.
- Results, model and inspector update without navigation or global scroll.

## 8. Geometry specification v2

The backend geometry service will add, without changing engineering formulas:

- shell course engineering results;
- 24 plate entities per course;
- staggered seam angles;
- bottom central/annular zones and representative seam layout;
- representative aluminum geodesic dome parameters;
- roof scope/status metadata;
- anchor and chair properties;
- entity IDs required for cross-selection.

The schema will remain consumable by older clients through preservation of existing top-level fields.

## 9. Three.js implementation

- Individual shell plate meshes with `userData` entity metadata.
- Visible vertical and horizontal seam edges.
- Strong selection outline/contrast and dimming of non-selected entities.
- Raycasting for plates, courses, roof, bottom and anchors.
- Synchronized Model Browser, 3D selection and Property Inspector.
- Geodesic dome touching the top shell edge, with triangular panels, frame and hubs.
- Roof modes: panels + frame, frame only, transparent panels.
- Display modes: solid, transparent, edges and section clipping.
- Color modes: thickness and utilization, with numeric legend.
- Fit model and fit selection controls.

The geodesic dome is explicitly `REPRESENTATIVE`; detailed structural design remains supplier scope.

## 10. API changes

Existing endpoints will be reused. Only missing read models will be added:

- revision input snapshot;
- derived geometry/result preview;
- run summary;
- module result;
- individual formula trace;
- scenario history including runs.

No calculation endpoint or formula will be duplicated.

## 11. Verification plan

1. Preserve all current golden tests.
2. Add API tests for the new read endpoints and history payload.
3. Add frontend interaction tests for navigation, dirty state, save feedback, calculation, trace opening and selection linkage where practical.
4. Run `pytest -q` after backend changes.
5. Run frontend tests and `pnpm run build`.
6. Validate manually at approximately 1920 x 1080 and 1600 x 900.
7. Capture the required screenshots in `docs/screenshots/v0.2/`.
8. Update version, changelog, architecture, implementation status and UX documentation.

## 12. Non-goals for v0.2

No nozzle design, stairs, platforms, full BOM, full weld map, API 653, Annex G structural calculation, FEA or foundation design will be added. Visual geometry will not be presented as AFC fabrication detail when the supplied evidence is insufficient.
