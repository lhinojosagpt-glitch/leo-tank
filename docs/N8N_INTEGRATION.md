# n8n integration

## Workflow A - cálculo individual

1. `GET /api/v1/fixtures/T78_2019`
2. Modificar el JSON en un nodo Code/Set.
3. `POST /api/v1/calculate`
4. Filtrar `overall_status` y `summary`.
5. Para persistencia, crear Project → Scenario → Revision → Run.
6. `POST /api/v1/runs/{run_id}/reports` y descargar PDF/JSON.

## Workflow B - variantes

`POST /api/v1/variant-batches`:

```json
{
  "name": "Barrido SG",
  "baseline_inputs": {},
  "variants": [
    {"name": "SG 0.90", "changes": {"product.specific_gravity": 0.90}},
    {"name": "Sp 0.50", "changes": {"seismic.Sp": 0.50}}
  ]
}
```

La matriz compacta retorna peso, utilizaciones, J, necesidad de anclaje y estado global, sin obligar a descargar todas las trazas.

