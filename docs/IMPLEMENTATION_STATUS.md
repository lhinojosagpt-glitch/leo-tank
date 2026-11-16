# Implementation status

| Fase | Estado | Entregable |
|---|---|---|
| 0 Discovery | DONE | Inventario, extracción, revisión visual, `DISCOVERY_REPORT.md`, conflictos. |
| 1 Golden Dataset | DONE | `data/fixtures/T78_2019.json` con procedencia. |
| 2 Calculation Core | DONE | Unidades/conversiones, registry, One-Foot y pruebas. |
| 3 Seismic | DONE | Cadena Annex E T-78, J y hoop stresses. |
| 4 Wind / Bottom / Anchors / Chairs / Weights | DONE (T-78) | Viento con madurez `REVIEW`; demás verificaciones T-78 implementadas. |
| 5 Validation Suite | DONE | Golden tests y matriz de validación. |
| 6 Database | DONE | SQLAlchemy 2, SQLite, migración inicial, revisiones inmutables. |
| 7 FastAPI | DONE | Endpoints de cálculo, persistencia, batch, backup y exportación. |
| 8 Geometry | DONE | `TankGeometrySpec` con snapshot por run. |
| 9 OpenSCAD | DONE | Generador paramétrico; ejecución CLI queda como extensión. |
| 10 React/Three.js | DONE v0.2 | Workspaces, navegación, editores, árbol, 3D por plancha e inspectores fijos. |
| 11 Reports | DONE | HTML, PDF y JSON desde snapshot del run. |
| 12 Variant Engine | IN PROGRESS | Batch y deltas listos; promoción de variante requiere endpoint adicional. |
| 13 n8n readiness | DONE | API key opcional, cálculo directo, batch y guía. |

## Trabajo posterior explícito

- Completar ecuaciones de viento desde fuentes normativas autorizadas en vez de depender de resultados de referencia.
- Añadir promoción de variante a escenario y comparación persistida Run A/Run B.
- Ejecutar OpenSCAD CLI opcionalmente para STL/3MF/PNG.
- Ampliar reportes con todas las tablas y anexos gráficos.
- Extender perfiles sin modificar silenciosamente `API650_12E_T78`.

## Corte v0.2 — 2026-10-05

- Navegación y edición por módulos: **DONE**.
- Guardado con feedback y revisiones inmutables: **DONE**.
- Inspector de cálculo accesible sin scroll global: **DONE**.
- Selección cruzada árbol/3D/propiedades/trazas: **DONE**.
- Casco con 192 planchas identificables y costuras alternadas: **DONE**.
- Fondo zonificado y domo geodésico representativo: **DONE**.
- Diseño estructural de domo del proveedor: **NOT_IMPLEMENTED**, fuera del alcance demostrado.
- Validación visual 1600×900 y 1920×1080: **DONE**.
- Backend: **13 pruebas pasan**. Frontend: **2 pruebas integradas pasan**. Build: **DONE** con advertencia de tamaño de bundle.
# Version 2.0

The deterministic Design Assistant, capability-driven workspaces, complete check inspector, active-run context, stale-result warning, V2 palette, persistence/API surface and acceptance tests are implemented. See `V2_ACCEPTANCE_REPORT.md` for release evidence and `V2_DESIGN_ASSISTANT.md` for engineering safety boundaries.
