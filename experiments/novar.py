"""NovaR: Radix LSD directo optimizado."""
from __future__ import annotations

import numpy as np

from . import recorder


def _insertion_small(a: np.ndarray) -> None:
    n = a.shape[0]
    if n < 2:
        return
    for i in range(1, n):
        x = a[i]
        j = int(np.searchsorted(a[:i], x, side="right"))
        if j != i:
            a[j + 1 : i + 1] = a[j:i]
            a[j] = x


def _lsd_direct_fast(v_in: np.ndarray) -> np.ndarray:
    n = v_in.shape[0]
    if n == 0:
        return v_in.copy()
    a = v_in.astype(np.int64, copy=True)
    flip = np.int64(1) << 63
    buf = [np.empty_like(a), np.empty_like(a)]
    buf[0][:] = a ^ flip
    cur = 0
    for shift in (0, 8, 16, 24, 32, 40, 48, 56):
        src = buf[cur]
        dst = buf[1 - cur]
        d = (src >> shift) & 0xFF
        c = np.bincount(d, minlength=256)
        if c.max() == n:
            cur = 1 - cur
            continue
        start = np.cumsum(c)
        pos = np.empty(256, dtype=np.int64)
        pos[0] = 0
        pos[1:] = start[:-1]
        # bucket-wise scatter
        for i in range(256):
            k = c[i]
            if k:
                m = (d == i)
                p = pos[i]
                dst[p:p + k] = src[m]
        cur = 1 - cur
        recorder.tick()
    return buf[cur] ^ flip


def novar_v1(a: np.ndarray) -> None:
    if a.shape[0] < 48:
        _insertion_small(a)
        return
    n = a.shape[0]
    if n > 1:
        if bool(np.all(a[1:] >= a[:-1])):
            return
        if bool(np.all(a[1:] <= a[:-1])):
            a[:] = a[::-1]
            return
    mn = int(a.min())
    mx = int(a.max())
    r = mx - mn + 1
    if r == 1:
        return
    if r <= max(65536, n):
        cnts = np.bincount(a - mn, minlength=r)
        a[:] = np.repeat(np.arange(mn, mx + 1, dtype=a.dtype), cnts)
        recorder.tick()
        return
    res = _lsd_direct_fast(a)
    a[:] = res


NOVAR_V1 = novar_v1
