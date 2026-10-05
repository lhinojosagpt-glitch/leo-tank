# TANK650 ENGINE v0.2 — arquitectura UX/UI

## Objetivo

La versión 0.2 reorganiza el MVP como una aplicación técnica de escritorio. La página deja de ser un documento vertical único: cabecera, navegación, área de trabajo, inspector y barra de estado permanecen dentro de la altura disponible y cada panel administra su propio desplazamiento.

## Estructura de información

- **Cabecera:** proyecto, escenario, revisión, perfil, guardado y cálculo.
- **Navegación izquierda:** workspaces reales para proyecto, código, geometría, producto, materiales, casco, fondo, viento, sismo, techo/cargas, anclaje, revisión, resultados, historial y variantes.
- **Área central:** editor específico del módulo; el casco integra tabla, árbol de modelo y visor 3D.
- **Inspector derecho:** resumen, propiedades de la selección, verificaciones y accesos a cálculos.
- **Calculation Inspector:** drawer fijo y redimensionable conceptualmente, con ecuación, referencia, variables, resultado crudo, resultado mostrado y aceptación. Puede fijarse o maximizarse y no obliga a desplazarse al pie.
- **Barra de estado:** versión del motor, mensaje operativo y run activo.

## Estados y flujo de trabajo

Los datos editables viven en un borrador. Una edición muestra `CAMBIOS SIN GUARDAR`; **Guardar revisión** crea una revisión inmutable y entrega confirmación visible. **Calcular** valida y ejecuta el motor. Si el borrador coincide con la revisión guardada, el run queda persistido; si contiene cambios, se identifica como cálculo de borrador.

El historial del navegador refleja el workspace activo mediante rutas `/project/local/design/<módulo>`. Los botones de la navegación no son marcadores: cambian el editor central y preservan el estado de trabajo.

## Modelo 3D y selección cruzada

El casco se representa mediante 8 cursos y 24 planchas individuales por curso (`C01-P01` … `C08-P24`), con costuras verticales alternadas medio paño entre cursos. La selección en el árbol o en el visor actualiza el inspector de propiedades; el aislamiento y la visibilidad operan sobre entidades identificables.

El fondo distingue zona central, anular y sumidero. El techo físico es un domo geodésico de aluminio representativo, conectado a la coronación, con paneles, retícula y nodos visibles. La cubierta equivalente empleada por el cálculo se expone como un modo analítico distinto para evitar confundir geometría física con idealización de cálculo.

La distribución de planchas es **informada por los planos AFC pero representativa**; no es un plano de fabricación ni sustituye un modelo del proveedor. El diseño estructural del domo de aluminio pertenece al alcance del proveedor y permanece `NOT_IMPLEMENTED`.

## Modos de visualización

- sólido, transparente, aristas y sección;
- vistas frente, lateral, superior, isométrica y ortográfica;
- ajuste al modelo o a la selección;
- color por espesor, utilización o material;
- aislamiento, mostrar/ocultar y menú contextual del Model Browser.

## Contratos API incorporados

- lectura de inputs de una revisión;
- creación de revisión derivada;
- snapshot geométrico de una revisión;
- resumen, resultados por módulo y traza por fórmula de un run;
- historial completo de escenario con revisiones y runs.

El frontend continúa sin implementar fórmulas API 650: consume resultados, trazas y `TankGeometrySpec` emitidos por el backend.

## Verificación

La aceptación automatizada incluye un flujo de interfaz que navega entre módulos, modifica un valor, detecta estado sucio, guarda dos revisiones, ejecuta un run, abre una traza y comprueba la selección de una plancha. La verificación visual se efectuó a 1600×900 y 1920×1080, comprobando que no exista desplazamiento global necesario para operar.

