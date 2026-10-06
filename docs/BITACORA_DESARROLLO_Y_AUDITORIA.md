# Bitácora de desarrollo y guía de auditoría

**Proyecto:** TANK650 ENGINE — caso T-78  
**Versión documentada:** 0.2.0
**Fecha de corte:** 2026-10-05
**Estado:** aplicación técnica v0.2 funcional, limitada al perfil congelado `API650_12E_T78`
**Propósito de este archivo:** entregar a un revisor humano o a otra IA un punto de entrada único para reconstruir qué se desarrolló, con qué fuentes, qué se verificó y qué no debe darse por concluido.

## 1. Alcance solicitado y resultado entregado

Se construyó una aplicación local para reproducir y auditar el cálculo del tanque T-78 a partir de los documentos suministrados. El resultado separa:

- motor de cálculo en Python;
- persistencia de proyectos, escenarios, revisiones y ejecuciones en SQLite;
- API REST en FastAPI;
- interfaz web clara en React/TypeScript;
- visor geométrico en Three.js;
- exportación paramétrica OpenSCAD;
- reportes HTML, PDF y JSON;
- pruebas doradas contra resultados del caso T-78.

La aplicación se ejecuta localmente en `http://127.0.0.1:8000/`. El botón **Cargar ejemplo T-78** carga el fixture de prueba. El cálculo se ejecuta solamente al pulsar **Calcular**, permitiendo al usuario modificar antes los valores expuestos en la interfaz.

## 2. Fuentes de entrada y control de integridad

Los siguientes hashes SHA-256 identifican exactamente las fuentes usadas en este corte:

| Fuente | SHA-256 |
|---|---|
| `datos/5. DISEÑO MECÁNICO TANQUE T-78.pdf` | `E625E2CDA652A68A15A12F4465AE8D9390C2ADD2E5B3F809AFEFC17A724BF3BD` |
| `datos/6.  Reporte software Tank 2016 Tanque T-78_REV0.pdf` | `E00CD5826D270A0BEA6D19ECB0DAB1FD6CC9B64C3984D021CEEEC72A276299F9` |
| `planos referenciales/7. DISTRIBUCIÓN DE PLANCHAS EN EL FONDO TANQUE T-78.pdf` | `04C5DF5B3FF5799CA170F9CC87A9AD1DB537DC8BB3C1DA5640E09B13D10C8691` |
| `planos referenciales/8. DISTRIBUCIÓN DE PLANCHAS EN CILINDRO TANQUE T-78.pdf` | `65AF24FBAFE874A54C4F991E16C5B180691E5B2009E7C25255D70B3F15848133` |
| Prompt maestro adjunto `Texto pegado.txt` | `59BA03812A8CBDF8B746ECEC51AFF6D255B68781D60D9F40DE95DE836D5B8388` |
| Fixture derivado `data/fixtures/T78_2019.json` | `4247A90BB2A2665DF65F95C8DA796ED53310053D888467391A387C148D54049B` |
| Prompt UX/UI v0.2 de 120 puntos `Texto pegado.txt` | `242C09D060FDD2E30860622168E1365478840E958375F78E0C38E06FE29D1BBC` |

El prompt maestro original está almacenado por Codex fuera del repositorio en:

`C:\Users\Leoncio\.codex\attachments\46bffa4f-7704-4311-91b6-62fdfc851210\Texto pegado.txt`

Para una auditoría portable, el usuario debe entregar también ese archivo a la IA revisora. Esta bitácora no sustituye el texto contractual del prompt ni los documentos fuente.

## 3. Cronología verificable del desarrollo

### 2026-10-04 — descubrimiento documental

- Se inventariaron los cuatro PDF y el prompt maestro.
- Se extrajeron parámetros y resultados del tanque T-78.
- Se registraron contradicciones sin ocultarlas ni resolverlas de forma silenciosa.
- Se creó `docs/DISCOVERY_REPORT.md`.
- Se creó `docs/SOURCE_CONFLICTS.md` con ocho conflictos identificados y su tratamiento explícito.

### 2026-10-04 — dataset y motor

- Se creó el fixture dorado `data/fixtures/T78_2019.json`.
- Se implementó el cálculo del casco por método One-Foot para ocho cursos.
- Se implementó la cadena sísmica del perfil T-78 y las verificaciones circunferenciales.
- Se incorporaron verificaciones de fondo, anular, anclajes, silla, viento y pesos.
- Se etiquetaron como `REFERENCE_RECONSTRUCTION`, `REVIEW` o `NOT_IMPLEMENTED` las ramas cuya ecuación normativa completa no estaba demostrada por la fuente disponible.

### 2026-10-04 — persistencia, API y salidas

- Se definieron modelos SQLAlchemy y una migración inicial Alembic.
- Se implementaron revisiones inmutables y snapshots de cada ejecución.
- Se añadieron endpoints de cálculo directo, proyectos, escenarios, revisiones, runs, variantes, trazas, checks, reportes, OpenSCAD y backup.
- Se añadieron exportaciones JSON, SCAD y reportes HTML/PDF.

### 2026-10-04 — interfaz y validación

- Se creó una interfaz de escritorio técnico con paleta clara.
- Se añadió un visor Three.js que consume el snapshot geométrico del backend.
- Se añadieron pruebas doradas y de integración.
- Se construyó el frontend de producción y se sirvió desde FastAPI.
- Se verificó manualmente en navegador la carga del ejemplo, el cálculo, el modelo 3D y el panel de resultados.

### 2026-10-05 — refactorización UX/UI y modelo 3D v0.2

- Se confirmó la recepción íntegra del prompt UX/UI de 120 puntos y se registró su hash.
- Se creó el commit base local `dda226a` (`chore: snapshot initial MVP v0.1`) antes de modificar el proyecto.
- Se reemplazó la página vertical por un shell de escritorio con workspaces y desplazamiento interno.
- Se habilitaron editores por disciplina, navegación con URL, dirty state, guardado con confirmación e historial.
- La traza inferior se reemplazó por un inspector fijo invocable desde resultados y tablas.
- Se modelaron 24 planchas por curso, 192 en total, con costuras alternadas y selección cruzada.
- Se añadió fondo zonificado y domo geodésico físico representativo, separado del modelo analítico.
- Se ampliaron contratos REST para revisión, geometría, resultados, trazas e historial.
- Se ejecutaron 10 pruebas backend, 1 prueba integrada frontend y el build de producción con resultado satisfactorio.
- Se realizó control visual de la aplicación a 1600×900 y 1920×1080.

## 4. Arquitectura implementada

```text
PDF / prompt maestro
        │
        ▼
fixture T78_2019.json
        │
        ▼
motor Python determinista ──► trazas + checks + geometría
        │
        ▼
SQLite / SQLAlchemy ──► revisiones y runs inmutables
        │
        ▼
FastAPI REST
   ├── interfaz React/TypeScript
   ├── visor Three.js
   ├── batch de variantes
   ├── reportes HTML/PDF/JSON
   └── exportación OpenSCAD
```

Regla arquitectónica central: el frontend y el visor no contienen fórmulas de ingeniería. Consumen los resultados y el `TankGeometrySpec` producidos por el backend.

## 5. Inventario de componentes relevantes

| Área | Archivos principales | Responsabilidad |
|---|---|---|
| Arranque | `backend/app/main.py` | FastAPI, API y archivos estáticos del frontend |
| API | `backend/app/api/router.py`, `schemas.py` | Contratos HTTP y orquestación |
| Dominio | `backend/app/domain/models.py` | DTO de resultados, trazas y checks |
| Motor | `backend/app/engine/runner.py` | Ejecución integral del perfil |
| Casco | `backend/app/engine/shell/calculator.py` | Método One-Foot |
| Sismo | `backend/app/engine/seismic/calculator.py` | Cadena sísmica y hoop stress |
| Otros checks | `backend/app/engine/other.py` | Fondo, viento, anclajes, silla y pesos |
| Registro | `backend/app/engine/registry.py` | Fórmulas y metadatos auditables |
| Base de datos | `backend/app/db/` | Proyectos, escenarios, revisiones y runs |
| Migración | `backend/alembic/versions/0001_initial.py` | Esquema inicial |
| Geometría | `backend/app/geometry/spec.py` | Snapshot paramétrico |
| Reportes | `backend/app/reports/generator.py` | HTML, PDF y JSON |
| OpenSCAD | `backend/app/openscad/generator.py` | Fuente `.scad` paramétrica |
| Interfaz | `frontend/src/App.tsx` | Flujo principal, inputs y resultados |
| Visor | `frontend/src/viewer/TankViewer.tsx` | Modelo tridimensional |
| Estilos | `frontend/src/styles.css` | Interfaz en colores claros |
| Dataset | `data/fixtures/T78_2019.json` | Caso base y procedencia |

## 6. Superficie de API implementada

Prefijo: `/api/v1`

- `GET /health`
- `GET /fixtures/T78_2019`
- `POST /calculate`
- `GET|POST /projects`
- `GET|POST /projects/{project_id}/scenarios`
- `GET|POST /scenarios/{scenario_id}/revisions`
- `POST /revisions/{revision_id}/runs`
- `GET /runs/{run_id}`
- `GET /runs/{run_id}/trace`
- `GET /runs/{run_id}/checks`
- `POST /variant-batches`
- `POST /runs/{run_id}/export/scad`
- `GET /runs/{run_id}/export/json`
- `POST /runs/{run_id}/reports`
- `GET /reports/{run_id}/{format_name}`
- `POST /system/backup`

La definición viva puede inspeccionarse en `http://127.0.0.1:8000/docs` mientras el servidor está activo.

## 7. Decisiones de ingeniería que el auditor debe cuestionar

1. **Ocho cursos:** se escogieron ocho cursos de 2,40 m porque coinciden el reporte TANK y los planos; una frase de la memoria menciona siete.
2. **Estado de anclaje:** el tanque puede pasar como autoanclado frente a viento y requerir anclaje mecánico frente a sismo. No se fusionaron ambos resultados.
3. **Rangos de `J`:** se implementaron los rangos `≤0,785`, `0,785–1,54` y `>1,54`; la narrativa contradictoria quedó registrada.
4. **Anular:** se mantienen por separado espesor requerido de 7,6 mm, seleccionado de 9 mm y alternativa de 12 mm.
5. **Ancho anular:** se mantienen por separado 685,40 mm calculados y 800 mm seleccionados.
6. **Techo:** el techo físico de aluminio y la plancha ficticia A36 usada para carga son entidades distintas.
7. **Pesos:** peso estructural neto y peso bruto de compra no se consideran equivalentes.
8. **Viento:** parte del resultado es reconstrucción del reporte de referencia; no debe presentarse como derivación normativa general completa.

La justificación y procedencia detalladas están en `docs/SOURCE_CONFLICTS.md` y dentro del fixture.

## 8. Evidencia de validación al corte

Comando ejecutado:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Resultado del 2026-10-04:

```text
9 passed
```

Advertencia observada: `StarletteDeprecationWarning` en la integración de `httpx` con `starlette.testclient`. No produjo fallos, pero debe resolverse al actualizar dependencias.

Pruebas cubiertas:

- salud de la API;
- cálculo directo desde el fixture;
- revisiones inmutables, runs y batch de variantes;
- espesores de diseño e hidroprueba del casco;
- espesor mínimo;
- cadena sísmica;
- esfuerzos circunferenciales sísmicos;
- caso integral T-78.

Los valores numéricos comparados y sus tolerancias están en `docs/VALIDATION_T78.md`. Entre otros, el motor coincide con el reporte de referencia en espesores del casco, `Tc`, `J`, hoop stress, tensión combinada de pernos y placa superior de silla dentro de las tolerancias declaradas.

Comando de compilación del frontend:

```powershell
cd frontend
pnpm run build
```

Resultado del 2026-10-04: compilación TypeScript y Vite exitosa. Vite emitió una advertencia de tamaño porque el bundle JavaScript minificado es aproximadamente 795 kB; se recomienda división de código antes de un despliegue público.

## 9. Estado funcional por módulo

| Módulo | Estado | Observación de auditoría |
|---|---|---|
| Descubrimiento documental | Terminado | Revisar extracción y referencias de página |
| Fixture T-78 | Terminado | Verificar cada valor contra su fuente |
| Casco One-Foot | Terminado para T-78 | No asumir generalidad fuera del perfil |
| Sismo Annex E | Terminado para T-78 | Revisar unidades, redondeo y ramas no ejercitadas |
| Fondo/anular | Terminado para T-78 | Confirmar criterio normativo y corrosión |
| Anclajes y silla | Terminado para T-78 | Confirmar propiedades de material y geometría |
| Viento | Revisión requerida | Contiene reconstrucción de resultados de referencia |
| Pesos | Revisión requerida | Algunos valores conservan procedencia de referencia |
| Base de datos | Terminado para MVP | Auditar concurrencia, migraciones futuras y backup |
| API | Terminado para MVP local | Auditar autenticación antes de exponer a red |
| Interfaz y 3D | Terminado v0.2 | Workspaces editables, árbol, 192 planchas e inspectores fijos |
| Batch de variantes | Parcial | Cálculo y deltas listos; falta promoción persistida de variante |
| OpenSCAD | Parcial | Genera fuente; ejecución automática de CLI queda pendiente |
| Reportes | Terminado para MVP | Ampliar tablas/anexos para entrega formal |
| n8n | Validado localmente | Flujo demostrativo ejecutado en n8n 1.122.4 contra TANK650 0.2.0; export versionado en `automation/n8n/` |

## 10. Limitaciones y deuda técnica conocida

- Este repositorio implementa el perfil T-78; no es todavía un calculador general certificado de API 650.
- No se debe usar el resultado como sustituto de la revisión y firma de un ingeniero responsable.
- Las fórmulas normativas deben comprobarse contra una copia autorizada de la edición aplicable de API 650.
- Los campos del perfil T-78 están organizados por disciplina; al ampliar el perfil deben añadirse definiciones de formulario explícitas.
- La promoción de una variante a escenario/revisión no tiene endpoint dedicado.
- No se ejecuta OpenSCAD automáticamente para producir STL/3MF/PNG.
- Los reportes aún no contienen todas las tablas y anexos gráficos posibles.
- La seguridad por API key es adecuada para desarrollo local, no constituye por sí sola un diseño de seguridad de producción.
- Las dependencias frontend usan la etiqueta `latest`; para reproducibilidad formal deben fijarse versiones y conservarse el lockfile.
- Existe una advertencia de bundle frontend superior a 500 kB.
- Existe una advertencia de deprecación en la pareja Starlette/TestClient-httpx.
- El commit local `dda226a` congela el MVP v0.1 previo a la refactorización y permite auditar el cambio v0.2 contra una base identificable.

## 11. Documentos complementarios

- `README.md`: puesta en marcha, estructura y límites generales.
- `docs/DISCOVERY_REPORT.md`: inventario y hallazgos de las fuentes.
- `docs/SOURCE_CONFLICTS.md`: contradicciones y resolución adoptada.
- `docs/CALCULATION_ENGINE.md`: organización del motor y trazabilidad.
- `docs/VALIDATION_T78.md`: valores, tolerancias y comparación con TANK.
- `docs/ARCHITECTURE.md`: separación de capas.
- `docs/DATABASE.md`: persistencia y revisiones inmutables.
- `docs/API.md`: contratos HTTP.
- `docs/N8N_INTEGRATION.md`: uso desde automatizaciones.
- `docs/OPENSCAD.md`: generación paramétrica.
- `docs/IMPLEMENTATION_STATUS.md`: matriz de estado resumida.
- `CHANGELOG.md`: cambios por versión.

## 12. Protocolo recomendado para otra IA auditora

La auditoría debe ejecutarse sin modificar primero el código. Se recomienda pedir a la IA revisora:

1. Leer el prompt maestro, esta bitácora, `DISCOVERY_REPORT.md`, `SOURCE_CONFLICTS.md` y `VALIDATION_T78.md`.
2. Recalcular de forma independiente los valores del fixture usando las páginas citadas, sin tomar el código como verdad.
3. Trazar cada campo de entrada hasta documento y página.
4. Revisar dimensiones, unidades y conversiones de cada fórmula registrada.
5. Comparar el motor con el reporte TANK usando valores sin redondear y las tolerancias declaradas.
6. Buscar constantes calibradas, correcciones artificiales o resultados copiados que se presenten incorrectamente como cálculo.
7. Probar valores frontera, entradas inválidas y variantes alejadas del T-78.
8. Auditar inmutabilidad, serialización de snapshots y recuperación de runs históricos.
9. Revisar autenticación, validación de payloads, rutas de archivos, backups y exposición de errores.
10. Revisar que el frontend no duplique ni altere fórmulas del backend.
11. Ejecutar las pruebas y el build en un entorno limpio.
12. Clasificar cada hallazgo por severidad y citar archivo y línea.

Prompt sugerido para el auditor:

> Audita este repositorio como un revisor independiente de software de ingeniería. No aceptes la documentación ni las pruebas existentes como evidencia suficiente por sí solas. Contrasta el prompt maestro y los PDF con el fixture y las fórmulas. Busca errores numéricos, unidades inconsistentes, supuestos no declarados, constantes calibradas, ramas no cubiertas, problemas de seguridad y afirmaciones de cumplimiento excesivas. Ejecuta las pruebas, añade casos adversos sin modificar primero la implementación y entrega hallazgos priorizados con archivo, línea, evidencia, impacto y corrección recomendada. Distingue claramente entre coincidencia con el caso T-78 y validez general bajo API 650.

## 13. Criterio de aceptación para cerrar la auditoría

La auditoría no debería considerarse cerrada hasta que:

- cada valor de entrada crítico tenga fuente y página comprobadas;
- cada salida crítica pueda reproducirse independientemente;
- no existan hallazgos abiertos de severidad alta;
- las limitaciones `REVIEW` y `NOT_IMPLEMENTED` estén visibles para el usuario final;
- las pruebas pasen en un entorno limpio con versiones fijadas;
- exista al menos un commit firmado o identificable que congele el corte auditado;
- el responsable de ingeniería apruebe los supuestos normativos.

---

Esta bitácora describe el estado observado del repositorio en la fecha de corte. No afirma certificación normativa ni sustituye el juicio profesional requerido para diseño, fabricación o puesta en servicio del tanque.
