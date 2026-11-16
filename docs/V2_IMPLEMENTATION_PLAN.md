# TANK650 ENGINE 2.0 — Implementation Plan

## Baseline evidence

- Backend baseline: existing suite started with engine `0.2.0`; golden values are treated as immutable.
- Frontend baseline: Vitest `1/1` passed; production build passed (bundle-size warning only).
- Repository: existing FastAPI/SQLAlchemy calculation service, React/TypeScript client, Three.js viewer and SQLite audit model are retained.

## Root causes found

1. `ModuleWorkspace` renders the same `inputs/results/checks` tabs for every discipline. Configuration-only modules therefore expose meaningless empty states.
2. Result lookup uses `result.modules[module]`; geometry, project, code, product, materials and roof have no calculation module with the same key. The “no run selected” text is therefore false when a run exists.
3. Check JSON uses the dataclass fields `title`, `standard_reference` and `message`, while both workspace and inspector render legacy keys `name`, `reference` and `note`. This produces orphan percentages and blank labels.
4. `activeRun` and results live only in React memory. Route changes do not intentionally clear them, but a reload loses context; draft changes also are not visibly marked stale against the previous result.
5. There is no persistent design-study model, variable registry, dependency graph or recommendation provenance. The existing variant endpoint calculates matrices but does not create a real `CalculationRun` per candidate.
6. The teal visual tokens and hard-coded colors predate the supplied V2 palette.

## Module/tab audit decision

| Module | Entradas | Resultados | Verificaciones | Decision |
|---|---:|---:|---:|---|
| Project | yes | no | no | single configuration view |
| Code | yes | no | no | profile + capabilities view |
| Geometry | yes | no | no | parameters + model; remove false result state |
| Product | yes | no | no | input configuration only |
| Materials | yes | no | no | input configuration only |
| Shell | yes | yes | yes | keep all |
| Bottom | yes | yes | yes | keep all |
| Wind | yes | yes | yes | keep all |
| Seismic | yes | yes | yes | keep all |
| Roof | yes | no | no | representative geometry/input scope only |
| Anchorage | yes | yes | yes | keep all |
| Review/results/variants/history | specialized | specialized | specialized | no universal tabs |

## Check → formula → variable map

| Check family | Formula/source | Adjustable design variables | Fixed/project conditions |
|---|---|---|---|
| Shell course | API 650 5.6.3.2 | selected course thickness | diameter, liquid height, SG, code stresses |
| Bottom | API 650 5.4/Table 5-1 | central/annular selected thickness | required minimum |
| Wind | API 650 5.11 reconstruction | none in V2 study | wind velocity/coefficient chain |
| Auto-anchor | API 650 Annex E.6.2.1.1 / J | annular effective/selected thickness | J limit 1.54, Sp, liquid height, diameter |
| Seismic hoop | API 650 Annex E | affected course thickness | seismic spectrum and material properties |
| Anchor bolt stress | API 650 Table 5.21b | bolt count, diameter/effective area | load cases/allowable stress |
| Anchor chair | AISI/TANK chair equation | top plate thickness | load and material allowable |

## Implementation

### Data quality

- Extend acceptance checks with stable title/description, short title, module, formula, related entity and fail classification.
- Preserve all numeric formulas and golden outputs.

### Backend/design assistant

- Add `backend/app/assistant/` containing registry, dependency analysis, candidate generation, deterministic simulation and ranking.
- Persist `DesignStudy` and `DesignStudyVariant`; every evaluated candidate also persists a real `CalculationRun` linked to the immutable base revision.
- Add analyze/create/status/recommendations/variants/apply endpoints. Apply returns a draft changeset and never mutates a revision.
- Limit studies to three variables and 500 runs; never alter standard-defined, derived or project-condition values automatically.

### Frontend

- Drive tabs from a module-capability registry and use Spanish labels.
- Keep active result/run across workspace navigation and persist the last run id for reload recovery.
- Mark results stale when draft inputs differ from the calculated input fingerprint.
- Render check titles, demand/capacity/unit, full utilization and calculation link.
- Add a Design Resolution drawer for failed checks: explanation, affecting variables, study configuration, simulated alternatives, draft/partial adoption and ignore.
- Add project/scenario/revision/run/profile header context.

### Visual system

- Centralize `#014BA0`, `#0A5CB8`, `#1466C3`, `#C0C0C0`, `#D9D5D5`, white and accessible derivatives.
- Preserve green/red/amber semantic status colors; change Three.js selection to `#1466C3`.

## Database migration

- Add design studies and study variants with base run, base revision, intent, target check, search space, candidate run, ranking and recommendation metadata.
- Migration is additive; existing projects, revisions and runs remain untouched.

## API changes

- `POST /runs/{run_id}/design-assistant/analyze`
- `POST /runs/{run_id}/design-assistant/studies`
- `GET /design-studies/{study_id}`
- `GET /design-studies/{study_id}/recommendations`
- `GET /design-studies/{study_id}/variants`
- `POST /design-studies/{study_id}/recommendations/{id}/apply`
- `GET /capabilities/modules`

## Test strategy

- Re-run every existing golden and integration test.
- Add deterministic assistant tests for immutable revisions, candidate run provenance, true FAIL→PASS transitions, fixed-variable exclusion, boundary/no-solution behavior and partial draft application.
- Add UI tests for capability-driven tabs, visible check identity, stale-run notice and design-resolution workflow.
- Finish with frontend tests and production build.

## Migration/release strategy

1. Add data-quality fields without changing formula results.
2. Add tables/endpoints and test via isolated SQLite databases.
3. Replace universal tabs and legacy check keys.
4. Add assistant UI and design tokens.
5. Update documentation and acceptance evidence.
6. Change engine/app version to `2.0.0` only after the full acceptance suite passes.
