# Evidencia visual v0.2

Control visual ejecutado el 2026-10-05 con el servidor local de producción.

| Vista | Resolución | Evidencia verificada |
|---|---:|---|
| Casco / selección `C01-P05` | 1600×900 | árbol expandido, plancha seleccionada, inspector en pestaña Properties |
| Casco / modelo completo | 1920×1080 | 192 planchas, costuras, fondo, anclajes y domo representativo |
| Sismo / resumen | 1920×1080 | `J = 2.4059`, máximo hoop 95.9%, estados por módulo |
| Calculation Inspector | 1920×1080 | ecuación, referencia, raw, display, variables y estado visibles sin scroll global |

Comprobaciones DOM:

- `document.documentElement.scrollHeight === window.innerHeight` en ambas resoluciones;
- `document.body.scrollHeight === window.innerHeight` en ambas resoluciones;
- `body` con `overflow: hidden`;
- consola del navegador sin errores ni advertencias durante el recorrido;
- navegación mediante rutas `/project/local/design/<módulo>`;
- selección cruzada `C01-P05` muestra `required design = 24.2226 mm` y `selected = 25 mm`.

Las capturas se realizaron con el navegador controlado de Codex y se revisaron visualmente durante el desarrollo. Este registro textual conserva los criterios verificables sin confundir las imágenes del MVP v0.1 proporcionadas por el usuario con evidencia de la versión v0.2.
