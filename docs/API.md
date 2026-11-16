# REST API

Base: `/api/v1`.

## Cálculo directo

- `GET /fixtures/T78_2019`
- `POST /calculate` con `{ "inputs": { ... } }`

## Persistencia

- `GET|POST /projects`
- `GET|POST /projects/{project_id}/scenarios`
- `GET|POST /scenarios/{scenario_id}/revisions`
- `POST /revisions/{revision_id}/runs`
- `GET /runs/{run_id}`
- `GET /runs/{run_id}/trace`
- `GET /runs/{run_id}/checks`

## Variantes y exportación

- `POST /variant-batches`
- `GET /runs/{run_id}/export/json`
- `POST /runs/{run_id}/export/scad`
- `POST /runs/{run_id}/reports`
- `GET /reports/{run_id}/{json|html|pdf}`
- `POST /calculation-memory`: recibe `{ "inputs": ... }`, recalcula con el motor Python y descarga una memoria Word determinista con entradas, resultados, verificaciones y trazas de fórmulas.

## Sistema

- `GET /health`
- `POST /system/backup`

Si `TANK650_API_KEY` tiene valor, los endpoints de escritura requieren `X-API-Key`.

# Design Assistant V2

- `GET /api/v1/capabilities/modules` returns meaningful workspace capabilities.
- `POST /api/v1/runs/{run_id}/design-assistant/analyze` explains failed checks and classifies editable/fixed variables.
- `POST /api/v1/runs/{run_id}/design-assistant/studies` runs up to 500 deterministic candidate simulations for up to three registered design variables.
- `GET /api/v1/design-studies/{study_id}` returns status, provenance, search space and compact summary.
- `GET /api/v1/design-studies/{study_id}/variants` returns every candidate and calculation run.
- `GET /api/v1/design-studies/{study_id}/recommendations` returns only truly passing candidates.
- `POST /api/v1/design-studies/{study_id}/recommendations/{recommendation_id}/apply` returns full or partial draft changes. It never mutates a revision and always requires recalculation.

