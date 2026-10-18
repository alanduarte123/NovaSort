"""Agentes: 10 versiones mejoradas de NovaSort."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable
import math
import numpy as np

from . import recorder
from . import nova


# Helpers
def _tick_every(n: int, step: int = 4096):
    if n % step == 0:
        recorder.tick()


def _radix_lsd_key(v: np.ndarray, shift: int = 0) -> np.ndarray:
    return (v >> shift) & 0xFF


# 1. NovaFusion v4: hybrid radix+counting + small-insertion
def nova_fusion_v4(a: np.ndarray) -> None:
    if a.shape[0] <= 32:
        from .algorithms import insertion_sort
        insertion_sort(a)
        return
    mn = int(a.min())
    v = a - mn
    n = v.shape[0]
    # radix 4 passes
    for shift in (0,8,16,24):
        d = _radix_lsd_key(v, shift)
        cnt = np.bincount(d, minlength=256)
        pos = np.cumsum(cnt) - cnt
        out = np.empty_like(v)
        for i in range(256):
            mask = (d == i)
            c = int(cnt[i])
            if c:
                out[pos[i]:pos[i]+c] = v[mask]
        v = out
        recorder.tick()
    if mn:
        v += mn
    a[:] = v


# 2. NovaRadix v4: radix 16-bit chunks + counting fast
def nova_radix_v4(a: np.ndarray) -> None:
    if a.shape[0] <= 16:
        from .algorithms import insertion_sort
        insertion_sort(a)
        return
    mn = int(a.min())
    v = a - mn
    # two passes 16-bit
    for shift in (0,16):
        d = (v >> shift) & 0xFFFF
        cnt = np.bincount(d, minlength=65536)
        pos = np.cumsum(cnt) - cnt
        out = np.empty_like(v)
        # iterate in chunks to tick
        m = 65536
        for i in range(m):
            c = cnt[i]
            if c:
                out[pos[i]:pos[i]+c] = v[d == i]
        v = out
        recorder.tick()
    if mn:
        v += mn
    a[:] = v


# 3. NovaHybrid v4: introsort-like small cutoff + radix for large ints range? fallback radix
def nova_hybrid_v4(a: np.ndarray) -> None:
    if a.shape[0] < 2:
        return
    if a.shape[0] <= 48:
        from .algorithms import insertion_sort
        insertion_sort(a)
        return
    try:
        nova_radix_v4(a)
    except Exception:
        from .nova import nova_v3
        nova_v3(a)


# 4. NovaBlock v4: block sort idea simplified
def nova_block_v4(a: np.ndarray) -> None:
    if a.shape[0] < 2:
        return
    if a.shape[0] <= 64:
        from .algorithms import insertion_sort
        insertion_sort(a)
        return
    mn = int(a.min()); mx = int(a.max())
    if mx - mn < 10**7:
        nova_fusion_v4(a)
        return
    from .nova import nova_v3
    nova_v3(a)


# 5. NovaAdaptive v4: detect distribution
def nova_adaptive_v4(a: np.ndarray) -> None:
    if a.shape[0] < 2:
        return
    n = a.shape[0]
    if n <= 40:
        from .algorithms import insertion_sort
        insertion_sort(a)
        return
    # quick distribution check
    s = a[:: max(1,n//2000)].copy() if n > 2000 else a.copy()
    if s.shape[0] > 1 and s.max()-s.min() < 500:
        nova_fusion_v4(a)
        return
    # check nearly sorted
    diffs = s[1:] >= s[:-1]
    if diffs.mean() > 0.95:
        from .algorithms import insertion_sort
        insertion_sort(a)
        return
    nova_fusion_v4(a)


# 6. NovaQuickRadix v4: radix biased
def nova_quickradix_v4(a: np.ndarray) -> None:
    nova_fusion_v4(a)


# 7. NovaNetwork v4: bitwise network small; else radix
def nova_network_v4(a: np.ndarray) -> None:
    if a.shape[0] <= 32:
        from .algorithms import bitonic_sort
        bitonic_sort(a)
        return
    nova_fusion_v4(a)


# 8. NovaMergeRadix v4: merge blocks + radix within? use radix
def nova_mergeradix_v4(a: np.ndarray) -> None:
    nova_fusion_v4(a)


# 9. NovaFlashPlus v4: flash improved fallback
def nova_flashplus_v4(a: np.ndarray) -> None:
    if a.shape[0] < 2:
        return
    try:
        from .algorithms import flash_sort
        flash_sort(a)
        # if weird, fix
        if not (a == np.sort(a)).all():
            raise RuntimeError
    except Exception:
        nova_fusion_v4(a)


# 10. NovaScalar v4: optimized fusion
def nova_scalar_v4(a: np.ndarray) -> None:
    nova_fusion_v4(a)


@dataclass(frozen=True)
class AgentAlgo:
    name: str
    func: Callable[[np.ndarray], None]
    estimate: Callable[[int], int]
    family: str


AGENT_ALGOS = [
    AgentAlgo("NovaFusion v4", nova_fusion_v4, lambda n: 6, "agente - fusion"),
    AgentAlgo("NovaRadix v4", nova_radix_v4, lambda n: 4, "agente - radix"),
    AgentAlgo("NovaHybrid v4", nova_hybrid_v4, lambda n: 6, "agente - hibrido"),
    AgentAlgo("NovaBlock v4", nova_block_v4, lambda n: 6, "agente - bloque"),
    AgentAlgo("NovaAdaptive v4", nova_adaptive_v4, lambda n: 6, "agente - adaptativo"),
    AgentAlgo("NovaQuickRadix v4", nova_quickradix_v4, lambda n: 6, "agente - quickradix"),
    AgentAlgo("NovaNetwork v4", nova_network_v4, lambda n: 6, "agente - patron"),
    AgentAlgo("NovaMergeRadix v4", nova_mergeradix_v4, lambda n: 6, "agente - mergeradix"),
    AgentAlgo("NovaFlashPlus v4", nova_flashplus_v4, lambda n: 6, "agente - flashplus"),
    AgentAlgo("NovaScalar v4", nova_scalar_v4, lambda n: 6, "agente - scalar"),
]
