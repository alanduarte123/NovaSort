# Sorting Showdown

Comparación y desarrollo iterativo de algoritmos de ordenamiento en Python/numpy:

- **20 algoritmos clásicos** optimizados (bubble, quick, merge, heap, radix, timsort...)
- **NovaSort v1 → v3**: algoritmo híbrido nuevo creado por iteración (benchmark-guided)
- **NovaSuper v1**: versión final especializada en batir a *Radix LSD*
- **10 variantes "agente"** (NovaFusion v4, NovaRadix v4, ...) generadas y evaluadas
- Benchmark secuencial (un algoritmo a la vez, subprocesos con timeout — anti-lag/memoria)
- Suite de corrección cruzada: **1932/1932 verificacones OK**
- Visualización: benchmark con gráficas + clasificador visual de imágenes (GUI/CLI)

## Resultados clave (50,000 elementos int64)

| # | Algoritmo | Tiempo (s) |
|---|-----------|-----------|
| 1 | **NovaSuper v1** (creado) | 0.0153 |
| 2 | NovaSort v3 (creado) | 0.0155 |
| 3 | Radix LSD | 0.0218 |
| 4 | Bucket Sort | 0.0555 |
| ... | ... | ... |
| 20 | Bubble Sort | ~21.7 |
| 21 | Cocktail Shaker | ~23.3 |

**NovaSuper v1 vs Radix LSD: speedup 1.47–1.62×** (ver `FINAL_VS_RADIX.md`)

## Estructura

```
sorting_showdown/
├── algorithms.py        # 20 algoritmos clásicos optimizados
├── nova.py              # NovaSort v1, v2, v3 (trayectoria de mejora)
├── nova_vs_radix.py     # NovaSuper v1 (mejor algoritmo, vs Radix LSD)
├── nova_agents.py       # 10 variantes v4 generadas por agentes
├── recorder.py          # captura de frames downsampled (visualización)
├── benchmark.py         # runner en serie con subprocesos + timeout
├── visualize.py         # animación/gráficas comparativas
├── test_correctness.py  # suite: 1932 verificaciones
├── test_agents.py       # verificación de variantes de agentes
├── experiments/         # variantes de investigación (novar*, ultra, tuned...)
├── examples/            # clasificador visual de imágenes (CLI + GUI)
├── results/             # benchmarks JSON, gráficas PNG
└── AGENTS_REPORT.md / FINAL_VS_RADIX.md / RESULTS_NOVA_RADIX.md
```

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

### Verificación

```bash
python3 -m sorting_showdown.test_correctness   # 1932/1932
python3 -m sorting_showdown.test_agents        # variantes agentes
```

### Benchmark (50k, en serie, un algoritmo a la vez)

```python
from sorting_showdown.benchmark import run_all
results = run_all(n=50_000, timeout=120.0)
```

### Comparar solo NovaSuper vs Radix LSD

```python
from sorting_showdown import nova_vs_radix, algorithms
```

### Clasificador visual de imágenes (CLI)

```bash
python3 sorting_showdown/examples/img_sort_cli.py imagen.png novasuper
# opciones: novasuper | novasort | radix | quick
```

### Clasificador visual de imágenes (GUI, requiere display)

```bash
python3 sorting_showdown/examples/img_sort_gui.py
```

## Notas de diseño

- Todos los algoritmos mutan in-place `np.ndarray` int64; si trabajan sobre listas usan `_list_view`/`_commit` para que la captura de frames vea su estado.
- El tiempo reportado descuenta el costo de captura (`wall - capture_seconds`).
- El runner lanza cada algoritmo en un subproceso con timeout → ningún O(n²) bloquea el proyecto.
- NovaSuper v1: early-exits (ya ordenado/invertido), camino rápido de counting para rangos pequeños, radix de 2 pases de 16 bits con `argsort` estable + chunking, fallback introsort-lista para floats.

## Licencia

MIT (ver LICENSE).
