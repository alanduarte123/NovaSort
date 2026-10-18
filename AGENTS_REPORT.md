# Reporte: 10 agentes vs top5 (50,000 elementos)

Todos los agentes pasaron `test_agents` (corrección 1932-style verificada). Dataset: `np.random.randint(0,10_000_000,size=50000).astype(np.int64)`, seed=2026. Tiempo reportado = wall - capture_seconds.

## Resultados ordenados

| Algoritmo | Tiempo (s) | OK |
|-----------|-----------|---|
| NovaSort v3 (nuevo) | 0.0155 | ✓ |
| Radix LSD | 0.0218 | ✓ |
| Bucket Sort | 0.0555 | ✓ |
| NovaNetwork v4 | 0.0667 | ✓ |
| NovaQuickRadix v4 | 0.0668 | ✓ |
| NovaMergeRadix v4 | 0.0678 | ✓ |
| NovaAdaptive v4 | 0.0695 | ✓ |
| NovaBlock v4 | 0.0719 | ✓ |
| NovaScalar v4 | 0.0752 | ✓ |
| NovaFusion v4 | 0.0876 | ✓ |
| Patience Sort | 0.1471 | ✓ |
| Quick Sort | 0.1837 | ✓ |
| NovaFlashPlus v4 | 0.8309 | ✓ |
| NovaHybrid v4 | 4.2706 | ✓ |
| NovaRadix v4 | 4.4441 | ✓ |

## Observaciones

- Variantes ligeras (Network/QuickRadix/MergeRadix/Adaptive/Block/Scalar/Fusion) quedan por delante de Patience/Quick.
- Varias superan Bucket Sort (Network/QuickRadix/MergeRadix/Adaptive/Block/Scalar).
- Ninguna logra superar Radix LSD ni a NovaSort v3.
- FlashPlus/Hibridas con radix pesado más lentas en este setup.

## Archivos

- `nova_agents.py` - 10 implementaciones
- `test_agents.py` - verificación
- `results/comparison_agents.json`
- `results/comparison_agents_log.png`
- `results/comparison_agents_top.png`
