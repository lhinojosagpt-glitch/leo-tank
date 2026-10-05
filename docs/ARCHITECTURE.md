# Architecture

```text
JSON / SQLite revision snapshot
            │
            ▼
Python calculation engine ──► formula traces + checks + geometry snapshot
            │
            ▼
SQLAlchemy / SQLite immutable run
            │
            ▼
FastAPI REST
    ├── React + TypeScript UI
    ├── Three.js viewer
    ├── n8n clients
    ├── HTML/PDF/JSON reports
    └── OpenSCAD generator
```

El frontend nunca contiene fórmulas API 650. Three.js y OpenSCAD consumen `TankGeometrySpec`; no recalculan espesores ni cargas.

## Límites de capas

- `engine`: funciones puras, deterministas y ejecutables sin servidor.
- `domain`: DTOs inmutables para trazas, verificaciones y módulos.
- `db`: persistencia; una revisión ejecutada se bloquea y no se muta.
- `api`: orquestación HTTP, autenticación opcional y errores estructurados.
- `geometry`: snapshot suficiente para reconstruir el modelo de un run histórico.
- `reports`: siempre consume el `result_json` del run, nunca inputs actuales.
- `frontend`: formularios, navegación, gráficos y auditoría.

## Evolución

Los módulos fuera del perfil T-78 deben incorporarse como nuevos perfiles y fórmulas registradas. No se debe ampliar el perfil congelado de forma silenciosa.

