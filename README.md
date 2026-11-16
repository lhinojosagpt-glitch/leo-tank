# TANK650 ENGINE v2.0

Aplicación de ingeniería para el cálculo auditable y el diseño paramétrico de tanques API 650. La identidad visible del proyecto es **T-160MB**; el identificador interno `T78` y el perfil congelado `API650_12E_T78` se conservan por compatibilidad con el fixture dorado, la base de datos, la API y las pruebas históricas.

La bitácora integral para revisión independiente está en [`docs/BITACORA_DESARROLLO_Y_AUDITORIA.md`](docs/BITACORA_DESARROLLO_Y_AUDITORIA.md).

El repositorio implementa el caso verificado T-160MB con separación estricta entre cálculo Python, persistencia SQLite, API REST, interfaz React/TypeScript/Three.js, automatización n8n y exportación OpenSCAD. La interfaz utiliza una paleta clara azul, blanca y neutra de escritorio técnico.

## Capacidades principales

- Entradas editables por disciplina desde la interfaz web o mediante la API.
- Motor determinista Python con resultados, verificaciones, referencias y trazas de fórmulas.
- Modelo Three.js con cursos, planchas, fondo, anclajes y domo geodésico representativo.
- Proyectos, escenarios, revisiones inmutables, runs y variantes almacenados en SQLite.
- Design Assistant v2 para explicar incumplimientos y simular alternativas sin modificar automáticamente el diseño.
- Memoria de cálculo Word regenerable desde el estado actual del modelo.
- Reportes técnicos y gerenciales en Word y PDF.
- Workflow n8n para ejecutar cálculos, aplicar variantes y conversar con los datos mediante DeepSeek.

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
- Design Assistant determinista con estudios persistidos, candidatos calculados, clasificación de fallos y adopción total o parcial de cambios.
- Identidad visual T-160MB desacoplada de los identificadores internos T78 para mantener compatibilidad.
- Sistema visual v2 azul/blanco con estados semánticos PASS, FAIL, WARNING y REVIEW.

La arquitectura de interacción y sus límites se describen en [`docs/UX_V2.md`](docs/UX_V2.md).

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

El script de inicio escucha en `0.0.0.0:8000` y limita los clientes de red mediante `TANK650_ALLOWED_CLIENTS`. Revise esa lista antes de exponer la aplicación en una LAN diferente.

## Flujo de trabajo

1. Cargue el ejemplo T-160MB o ingrese los parámetros desde la interfaz.
2. Revise las entradas por módulo y ejecute **Calcular**.
3. Consulte resultados, verificaciones y trazas desde el inspector.
4. Cuando corresponda, abra Design Assistant para estudiar alternativas de un check fallido.
5. Guarde una revisión para conservar inputs y runs de forma inmutable.
6. Genere nuevamente la memoria Word después de cualquier variación de parámetros.

Los cálculos de borrador permiten explorar valores sin crear una revisión. Los estudios trazables del Design Assistant requieren una revisión y un run persistidos.

## API

La API se publica bajo `/api/v1`. Operaciones habituales:

- `GET /api/v1/fixtures/T78_2019`: obtiene el fixture compatible del caso T-160MB.
- `POST /api/v1/calculate`: calcula directamente un objeto `inputs` sin crear una revisión.
- Endpoints de proyectos, escenarios, revisiones y runs para persistencia auditable.
- Endpoints de Design Assistant para analizar checks, crear estudios, comparar candidatos y aplicar un changeset al borrador.
- Generación de geometría, reportes y memoria de cálculo a partir de datos controlados.

Consulte [`docs/API.md`](docs/API.md) para el detalle de contratos y [`docs/V2_DESIGN_ASSISTANT.md`](docs/V2_DESIGN_ASSISTANT.md) para el asistente de diseño.

## Integración con n8n y DeepSeek

El workflow importable se encuentra en [`automation/n8n/tank650-prueba-local-compatible.json`](automation/n8n/tank650-prueba-local-compatible.json).

El flujo:

1. Comprueba la API local de TANK650.
2. Obtiene el fixture compatible y aplica variantes de entrada.
3. Ejecuta `POST /api/v1/calculate`.
4. Construye un contexto conversacional con los **inputs completos**, metadatos, resumen, valores calculados y verificaciones por módulo.
5. Envía la pregunta y ese contexto a `deepseek-flash`.
6. Devuelve la respuesta técnica al chat de n8n.

El modelo conversacional debe distinguir entre dato de entrada, valor derivado, resultado y verificación. No reemplaza al motor Python, no modifica resultados y no certifica el diseño.

Para usar el workflow en otra instalación de n8n:

- Importe el archivo JSON.
- Configure una credencial n8n de tipo **DeepSeek API**.
- Ajuste `apiBaseUrl` si TANK650 no se ejecuta en `http://127.0.0.1:8000`.
- No suba credenciales, claves API ni la base de datos interna de n8n al repositorio.

La guía completa se encuentra en [`docs/N8N_INTEGRATION.md`](docs/N8N_INTEGRATION.md).

## Reportes y evidencias

La carpeta [`output`](output) contiene entregables generados, entre ellos:

- Informe gerencial de TANK650 ENGINE v2.
- Reporte de funcionalidad T-160MB en Word y PDF.
- Evidencia visual de la interfaz.

La memoria de cálculo operativa se genera dinámicamente desde la aplicación y puede regenerarse después de modificar cualquier input.

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
- `backend/app/assistant`: Design Assistant, variables candidatas y recomendaciones deterministas.
- `frontend`: React, TypeScript, Vite, Three.js y CSS puro.
- `data/fixtures/T78_2019.json`: dataset dorado con procedencia.
- `docs`: descubrimiento, conflictos, arquitectura y validación.
- `automation/n8n`: workflows exportables para integración y conversación con resultados.
- `models/generated`: exportaciones SCAD generadas.
- `reports/generated`: reportes por run (ignorados por Git).
- `output`: informes y evidencias entregables.

## Seguridad local

Si `TANK650_API_KEY` está vacío, se asume desarrollo local. Si contiene un valor, los endpoints de escritura exigen el encabezado `X-API-Key`.

## Límites del perfil

No es una implementación general de API 650. El perfil permanece limitado al caso verificado T-160MB/T78 y documenta como `REVIEW` o `NOT_IMPLEMENTED` cualquier rama no reconstruida con certeza. El domo geodésico es representativo y su diseño estructural de proveedor no forma parte del alcance del motor.

Los resultados de viento y pesos identificados como `REFERENCE_RECONSTRUCTION` conservan su procedencia documental y no deben interpretarse como una fórmula normativa reconstruida cuando la fuente no expone la cadena completa.

## Auditoría y documentación

- [`docs/BITACORA_DESARROLLO_Y_AUDITORIA.md`](docs/BITACORA_DESARROLLO_Y_AUDITORIA.md): bitácora integral y guía de auditoría.
- [`docs/V2_ACCEPTANCE_REPORT.md`](docs/V2_ACCEPTANCE_REPORT.md): aceptación funcional de la versión 2.
- [`docs/UI_MODULE_AUDIT_V2.md`](docs/UI_MODULE_AUDIT_V2.md): auditoría de módulos de interfaz.
- [`docs/V2_COLOR_SYSTEM.md`](docs/V2_COLOR_SYSTEM.md): sistema visual y estados semánticos.
- [`docs/DATABASE.md`](docs/DATABASE.md): persistencia, revisiones, runs y estudios.
