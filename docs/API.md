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

## Sistema

- `GET /health`
- `POST /system/backup`

Si `TANK650_API_KEY` tiene valor, los endpoints de escritura requieren `X-API-Key`.

