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
| 10 React/Three.js | DONE | Interfaz clara, escritorio técnico, 3D y audit panel. |
| 11 Reports | DONE | HTML, PDF y JSON desde snapshot del run. |
| 12 Variant Engine | IN PROGRESS | Batch y deltas listos; promoción de variante requiere endpoint adicional. |
| 13 n8n readiness | DONE | API key opcional, cálculo directo, batch y guía. |

## Trabajo posterior explícito

- Completar ecuaciones de viento desde fuentes normativas autorizadas en vez de depender de resultados de referencia.
- Añadir promoción de variante a escenario y comparación persistida Run A/Run B.
- Ejecutar OpenSCAD CLI opcionalmente para STL/3MF/PNG.
- Ampliar reportes con todas las tablas y anexos gráficos.
- Extender perfiles sin modificar silenciosamente `API650_12E_T78`.

