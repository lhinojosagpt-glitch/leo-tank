# Source conflicts - T-78

| ID | Asunto | Evidencia | Resolución del modelo |
|---|---|---|---|
| SC-001 | Número de anillos | Un párrafo de MEMORY indica siete; MEMORY p. 10, TANK2016 pp. 3-4 y SHELL_DRAWING muestran ocho cursos de 2,40 m = 19,20 m. | Ocho cursos. La frase de siete queda registrada como contradicción narrativa. |
| SC-002 | Auto-anclado vs anclado | Viento: “anchors not needed” (TANK2016 p. 9). Sismo: J=2,4059 y “anchors needed” (pp. 12 y 17). | El estado global es `PASS_WITH_MECHANICAL_ANCHORAGE`. Viento y sismo se clasifican por separado. |
| SC-003 | Lógica narrativa de J | MEMORY p. 19 contiene una frase que asocia “menor que 1,54” con inestabilidad, mientras el resultado J=2,4059 y el reporte TANK exigen anclajes por superar el límite. | Se implementan tres rangos: ≤0,785 auto-anclado; 0,785–1,54 uplift/check; >1,54 anclaje mecánico. |
| SC-004 | Espesor anular | TANK2016 p. 9 calcula 7,6 mm; MEMORY p. 22 y plano seleccionan 9 mm. El prompt menciona una alternativa posterior de 12 mm. | `required=7,6`, `selected=9,0`; 12 mm queda como variante, no baseline. |
| SC-005 | Ancho anular | TANK2016 p. 9 calcula 685,40 mm; MEMORY p. 22 selecciona 800 mm. | Ambos campos se guardan por separado. |
| SC-006 | Techo | El tanque físico tiene domo geodésico de aluminio, pero TANK usa plancha ficticia A36 de 9 mm para carga. | `physical_roof` y `analysis_roof` separados. El visor muestra el físico; el motor de pesos conserva el sustituto. |
| SC-007 | Peso neto vs compra | TANK reporta pesos netos; los planos cuantifican planchas rectangulares antes del corte. | Se separan `net_structural_weight` y `gross_procurement_weight`; el segundo queda marcado para futura BOM/nesting. |
| SC-008 | Anular efectivo sísmico | Seleccionado 9 mm, pero la ecuación sísmica usa aproximadamente 6 mm efectivos después de corrosión. | Se guardan nominal, corrosión y efectivo como campos independientes. |

Ningún conflicto se elimina del fixture. La tabla `source_provenance` permite vincular cada decisión a su documento y página.

