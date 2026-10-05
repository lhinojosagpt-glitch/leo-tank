# Discovery report - T-78

Fecha de análisis: 2026-10-04. Perfil objetivo: `API650_12E_T78`.

## Documentos encontrados

| ID | Documento | Páginas | Rol y contenido relevante |
|---|---|---:|---|
| MEMORY | `datos/5. DISEÑO MECÁNICO TANQUE T-78.pdf` | 23 | Memoria narrativa, entradas, selección de espesores, conclusiones, pesos y geometría de sillas. |
| TANK2016 | `datos/6.  Reporte software Tank 2016 Tanque T-78_REV0.pdf` | 29 | Fuente numérica primaria: inputs, ecuaciones, resultados de casco, viento, sismo, anclajes y sillas. |
| BOTTOM_DRAWING | `planos referenciales/7. DISTRIBUCIÓN DE PLANCHAS EN EL FONDO TANQUE T-78.pdf` | 1 (A1) | Distribución de 115 planchas centrales 6000x2400x8, 12 sectores anulares, pendiente 1%, sumidero NPS 6 y 60 anclajes. |
| SHELL_DRAWING | `planos referenciales/8. DISTRIBUCIÓN DE PLANCHAS EN CILINDRO TANQUE T-78.pdf` | 1 (A1) | Desarrollo de 8 cursos, 24 planchas por curso, costuras alternadas, espesores y elevación. |

La extracción nativa fue suficiente para memoria y reporte TANK. Los dos planos se verificaron visualmente a resolución completa porque su mapa de fuentes no produce texto fiable. No se usó OCR para fijar valores críticos.

## Jerarquía aplicada

1. Reporte numérico TANK 2016.
2. Planos AFC/de fabricación.
3. Memoria narrativa.
4. OCR (no necesario para valores finales).

## Entradas verificadas

| Grupo | Campo | Valor | Fuente principal |
|---|---|---:|---|
| Identificación | Tag | T-78 | MEMORY p. 1; planos |
| Geometría | Diámetro nominal | 45,725 m | TANK2016 p. 3 |
| Geometría | Diámetro interior | 45,700 m | planos de fondo/cilindro |
| Geometría | Altura del casco | 19,200 m | TANK2016 p. 3; SHELL_DRAWING |
| Geometría | Altura de líquido | 18,700 m | TANK2016 p. 3 |
| Producto | Gravedad específica | 0,8778 | TANK2016 p. 3 |
| Diseño | Temperatura | 43 °C | TANK2016 p. 3 |
| Diseño | Presión superior | 0,75 kPa | TANK2016 p. 3 |
| Casco | Material | ASTM A36, grupos I/II | TANK2016 p. 4 |
| Casco | Eficiencia de junta | 1,0 | TANK2016 p. 3 |
| Casco | Corrosión | 1,6 mm | TANK2016 pp. 3-4 |
| Viento | Velocidad | 25 m/s | TANK2016 pp. 3 y 7 |
| Sismo | Sp | 0,45 | TANK2016 pp. 6 y 11 |
| Sismo | Fa / Fv | 1,05 / 1,50 | TANK2016 p. 11 |
| Anclajes | Cantidad / diámetro | 60 / 63,5 mm | TANK2016 pp. 4 y 25 |
| Fondo | Central seleccionado | 8 mm | MEMORY pp. 8 y 22; BOTTOM_DRAWING |
| Fondo | Anular seleccionado | 9 mm | MEMORY p. 22; BOTTOM_DRAWING |
| Fondo | Ancho anular seleccionado | 800 mm | MEMORY p. 22 |
| Techo físico | Domo geodésico de aluminio | diseño del proveedor | MEMORY p. 5 y descripción del proyecto |

### Cursos del casco

| Curso | Altura m | Espesor mm | Material |
|---:|---:|---:|---|
| 1 | 2,40 | 25,0 | A36 Grupo II |
| 2 | 2,40 | 22,0 | A36 Grupo II |
| 3 | 2,40 | 19,0 | A36 Grupo I |
| 4 | 2,40 | 16,0 | A36 Grupo I |
| 5 | 2,40 | 12,7 | A36 Grupo I |
| 6 | 2,40 | 9,5 | A36 Grupo I |
| 7 | 2,40 | 8,0 | A36 Grupo I |
| 8 | 2,40 | 8,0 | A36 Grupo I |

## Salidas verificadas

### Casco - One Foot Method (TANK2016 p. 8)

| Curso | Diseño mm | Hidrotest mm | Seleccionado mm | Estado |
|---:|---:|---:|---:|---|
| 1 | 24,223 | 24,012 | 25,0 | PASS |
| 2 | 21,271 | 20,880 | 22,0 | PASS |
| 3 | 18,320 | 17,747 | 19,0 | PASS |
| 4 | 15,368 | 14,614 | 16,0 | PASS |
| 5 | 12,416 | 11,481 | 12,7 | PASS |
| 6 | 9,4649 | 8,3481 | 9,5 | PASS |
| 7 | 8,0000 | 8,0000 | 8,0 | PASS |
| 8 | 8,0000 | 8,0000 | 8,0 | PASS |

### Viento, fondo y pesos

- Presión de viento: 0,86207 kPa; cortante: 920 080 N; momento: 10,734 MN·m (TANK2016 p. 7).
- Viento: anclajes no requeridos para 5.11 (TANK2016 p. 9; MEMORY p. 19).
- Anular calculado por TANK: 7,6 mm y ancho requerido 685,40 mm (TANK2016 p. 9).
- Anular seleccionado por proyecto: 9 mm y 800 mm (MEMORY p. 22).
- Módulo de sección de viga superior: 564 090 mm³; altura no rigidizada máxima 22,820 m; cero anillos intermedios (TANK2016 p. 9).
- Peso vacío no corroído: 5 506 376 N; operación: 269 533 536 N; prueba: 314 429 952 N (TANK2016 p. 10).

### Sismo Annex E (TANK2016 pp. 11-24)

| Resultado | Valor |
|---|---:|
| Ss / S1 | 1,1250 / 0,56250 |
| Ts / Tc | 0,71429 s / 7,4374 s |
| SDS / Ai / Ac | 1,1812 / 0,29531 / 0,045761 |
| Wc / Wi | 134,43 MN / 121,13 MN |
| Vc / Vi / V | 6,151 MN / 37,396 MN / 37,899 MN |
| Mrw / Ms | 273,84 MN·m / 667,69 MN·m |
| Av / Ge | 0,55519 / 0,68286 |
| wa / wt | 334,45 / 313,96 N/cm |
| J | 2,4059 |
| Clasificación | MECHANICAL ANCHORAGE REQUIRED |

Tensiones de aro por curso: 196172,81; 197885,80; 199099,03; 199413,88; 202795,31; 203915,31; 159702,84; 76349,72 kPa. Admisible: 212739,78 kPa. Todos PASS.

### Anclajes y sillas

- Pernos requeridos: 48; seleccionados: 60; diámetro: 63,5 mm; espaciamiento final: 2,41 m.
- Caso combinado presión + sismo: 22 401 366 N de levantamiento, 373 356 N/perno, 183 034 kPa frente a 198 564 kPa: PASS.
- Silla: placa superior requerida 47,5179 mm; seleccionada 50,8 mm: PASS.

## Fórmulas explícitas recuperadas

El registro de fórmulas implementa, entre otras:

- One-foot de diseño e hidrostática, conservando unidades imperiales naturales del reporte.
- `Ss=2,5 Sp`, `S1=1,25 Sp`, `Ts=Fv·S1/(Fa·Ss)`.
- `Ks=0,578/sqrt(tanh(3,68H/D))`, `Tc=Ks·sqrt(D)`.
- `SDS=2,5QFaSp`, `Ai=SDS(I/Rwi)`, `Ac=min(...,Ai)`.
- Pesos impulsivo y convectivo, cortantes, brazos y momentos Annex E.
- `Av=0,47SDS`, `Ge=(1-0,4Av)G`, fuerza de anillo resistente y `J`.
- Fuerzas impulsiva, convectiva e hidrostática y esfuerzo combinado de aro.
- Uplift de pernos para presión, sismo y combinación.
- Espesor de placa superior de silla según la expresión AISI reproducida por TANK.

Cada evaluación conserva inputs, expresión, resultado bruto, resultado mostrado, unidad, redondeo y referencia.

## Datos de planos

- Fondo: 115 planchas 6000x2400x8 para sector central; 12 sectores anulares; pendiente radial 1%; sumidero NPS 6; secuencia de soldadura; 60 sueltas/sillas de anclaje.
- Cilindro: ocho cursos de 2400 mm; 24 planchas por curso; costuras verticales alternadas; espesores 25, 22, 19, 16, 12,7, 9,5, 8 y 8 mm; diámetro interior 45 700 mm.

## Supuestos controlados

- El perfil se congela en API 650 12th Edition y en los parámetros del reporte TANK fechado 2019-08-02.
- Se usan unidades imperiales para ecuaciones donde TANK muestra esa forma; la conversión a SI se registra.
- El techo físico y el sustituto de análisis son objetos distintos.
- Los valores de viento cuya cadena completa no se expone se conservan como reconstrucción de referencia con estado `REVIEW`, sin factores inventados.

