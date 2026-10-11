# TANK650 ENGINE v0.2

Motor auditable de cálculo y diseño paramétrico de tanques API 650, perfil inicial congelado `API650_12E_T78`.

La bitácora integral para revisión independiente está en [`docs/BITACORA_DESARROLLO_Y_AUDITORIA.md`](docs/BITACORA_DESARROLLO_Y_AUDITORIA.md).

El repositorio implementa el caso T-78 con separación estricta entre cálculo Python, persistencia SQLite, API REST, interfaz React/TypeScript/Three.js y exportación OpenSCAD. La interfaz usa una paleta clara de escritorio técnico.

## Estado de la aplicación

- Método 1-Foot reproducido para los 8 cursos con tolerancia absoluta de 0,01 mm.
- Cadena sísmica Annex E: `Ss`, `S1`, `Ts`, `Ks`, `Tc`, `SDS`, `Ai`, `Ac`, `Wc`, `Wi`, cortantes, brazos, momentos, `Av`, `Ge`, `wa`, `wt` y `J`.
- Ocho verificaciones de tensión circunferencial.
- Clasificación explícita de auto-anclaje y verificación de 60 pernos Ø63,5 mm.
- Verificación de placa superior de silla de anclaje.
- Fondo central/anular, viento, viga de rigidez y pesos documentados.
- Proyectos, escenarios, revisiones inmutables, runs y batch de variantes en SQLite.
- API directa para n8n, exportación JSON y SCAD, reportes HTML/PDF/JSON y memoria de cálculo Word regenerable desde los parámetros actuales.
- Workspaces editables por disciplina, navegación funcional y estado de borrador/revisión/run.
- Inspector fijo de resultados y drawer de trazas sin desplazamiento global.
- Visor Three.js con 192 planchas seleccionables, fondo zonificado, 60 anclajes y domo geodésico representativo.

La arquitectura de interacción y sus límites se describen en [`docs/UX_V2.md`](docs/UX_V2.md).

Los resultados de viento y pesos marcados como `REFERENCE_RECONSTRUCTION` conservan la procedencia de TANK 2016; no se ha inventado una ecuación normativa cuando el documento no expone toda la cadena.

## Inicio rápido en Windows

```bat
scripts\setup.bat
scripts\dev.bat
```

Abra `http://127.0.0.1:5173` durante desarrollo. Para el entorno web único:

```bat
scripts\start.bat
```

Abra `http://127.0.0.1:8000`. La documentación OpenAPI queda en `/docs`.

## Pruebas

```bat
scripts\test.bat
```

Hitos individuales:

```powershell
python -m pytest backend/tests/golden/test_t78_shell.py
python -m pytest backend/tests/golden/test_t78_seismic.py
python -m pytest backend/tests/golden/test_t78_full.py
cd frontend
pnpm test
pnpm run build
```

## Estructura

- `backend/app/engine`: cálculo y trazas de fórmulas.
- `backend/app/db`: modelo SQLAlchemy 2.
- `backend/app/api`: API REST FastAPI.
- `frontend`: React, TypeScript, Vite, Three.js y CSS puro.
- `data/fixtures/T78_2019.json`: dataset dorado con procedencia.
- `docs`: descubrimiento, conflictos, arquitectura y validación.
- `models/generated`: exportaciones SCAD generadas.
- `reports/generated`: reportes por run (ignorados por Git).

## Seguridad local

Si `TANK650_API_KEY` está vacío, se asume desarrollo local. Si contiene un valor, los endpoints de escritura exigen el encabezado `X-API-Key`.

## Límites del perfil

No es una implementación general de API 650. El perfil está limitado al caso T-78 y documenta como `REVIEW` o `NOT_IMPLEMENTED` cualquier rama no reconstruida con certeza.
