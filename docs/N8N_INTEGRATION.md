# n8n integration

## Flujo demostrativo validado

El flujo exportable se encuentra en `automation/n8n/tank650-prueba-local-compatible.json`. Fue validado el 2026-10-05 contra n8n local 1.122.4 y TANK650 ENGINE 0.2.0. Usa las versiones disponibles en esa instalación: Manual Trigger 1, Set 3.4, Code 2 y HTTP Request 4.3.

La secuencia comprueba la API, carga el fixture T-78, aplica variantes de diámetro, altura de líquido, gravedad específica y aceleración pico, ejecuta `POST /api/v1/calculate` y presenta un resumen junto con la respuesta completa. Al final, una cadena LLM conectada al modelo `deepseek-flash` genera una lectura técnica restringida a los resultados recibidos. Requiere una credencial n8n de tipo `DeepSeek API`. La prueba integral del cálculo alcanzó el estado `PASS_WITH_MECHANICAL_ANCHORAGE`.

El flujo ofrece dos entradas: `Inicio manual` genera un resumen automático y `Conversar sobre resultados` habilita la interfaz de chat de n8n. Cada pregunta del chat ejecuta nuevamente el cálculo, convierte el resumen a texto plano y lo adjunta a la pregunta antes de llamar a DeepSeek. La llamada usa Chat Completions con `thinking.type=disabled`, ya que el nodo DeepSeek incluido en n8n 1.122.4 no expone ese control para V4.1 Flash y puede devolver el contenido visible vacío. `Respuesta del asistente` publica la respuesta en el campo `text`, que consume la interfaz de chat. Esta versión no conserva memoria semántica entre preguntas; cada respuesta se basa en la pregunta actual y en la simulación recién ejecutada.

Para importarlo, use la opción **Import from File** de n8n y seleccione el JSON versionado. La URL predeterminada es `http://127.0.0.1:8000`; debe cambiarse en `Configurar prueba T-78` cuando la API se ejecute en otra máquina.

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
