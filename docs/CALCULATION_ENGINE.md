# Calculation engine

## Principios

1. Funciones puras con inputs serializables.
2. Unidades explícitas; conversiones registradas.
3. Fórmulas con ID estable y referencia.
4. Sin “factores de coincidencia”.
5. Diferencia entre resultado bruto y mostrado.
6. Estados `PASS`, `WARNING`, `FAIL`, `REVIEW`, `NOT_APPLICABLE` y `NOT_IMPLEMENTED`.

## One-Foot

Para reproducir TANK se conserva la ecuación imperial que muestra el software:

```text
td_in = 2.6 D_ft (H_ft - 1) G / (Sd_psi E) + CA_in
tt_in = 2.6 D_ft (H_ft - 1) / (St_psi E)
```

El valor se convierte a milímetros y se aplica el mínimo nominal de 8 mm. Esto evita la diferencia producida por constantes SI redondeadas.

## Sismo

La cadena se ejecuta por nodos individuales. Los resultados intermedios están en `modules.seismic.values` y cada fórmula evaluada en `modules.seismic.traces`. Las tensiones de aro usan la ecuación E.6.1.4-6 con los espesores seleccionados.

## Madurez

- `CALCULATED`: ecuación explícita reconstruida.
- `REVIEW`: valor de referencia validado cuyo desarrollo completo no aparece en los documentos disponibles (por ejemplo parte de la cadena de viento).

