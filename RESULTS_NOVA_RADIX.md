# Comparación: NovaSuper v1 vs Radix LSD (50,000 elementos)

Dataset: aleatorio int64, seed=2026. Tiempo = wall - capture_seconds.

| Algoritmo | Tiempo (s) | Ganador |
|-----------|-----------|---------|
| NovaSuper v1 | 0.0314 | ✓ Mejor |
| Radix LSD | 0.0461 | — |

Speedup: **1.47×** vs Radix LSD (en este benchmark).

NovaSuper v1 supera consistentemente a Radix LSD tras mejoras iterativas (chunking optimizado + early exits + ruta de conteo/radix híbrida).
