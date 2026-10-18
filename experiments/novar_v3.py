"""NovaR3: radix LSD 4-bits + menos recorder ticks."""
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


def novar_v3(a: np.ndarray) -> None:
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
    v = a.astype(np.int64, copy=True)
    flip = np.int64(1) << 63
    buf = [np.empty_like(v), np.empty_like(v)]
    buf[0][:] = v ^ flip
    cur = 0
    shifts = (0,4,8,12,16,20,24,28,32,36,40,44,48,52,56,60)
    for i, shift in enumerate(shifts):
        src = buf[cur]
        dst = buf[1-cur]
        d = (src >> shift) & 0xF
        c = np.bincount(d, minlength=16)
        if c.max() == n:
            cur = 1-cur
            if i % 2 == 0:
                recorder.tick()
            continue
        start = np.cumsum(c)
        pos = np.zeros(16, dtype=np.int64)
        pos[1:] = start[:-1]
        for j in range(16):
            k = c[j]
            if k:
                m = (d == j)
                p = pos[j]
                dst[p:p+k] = src[m]
        cur = 1-cur
        if i % 2 == 0:
            recorder.tick()
    res = buf[cur] ^ flip
    a[:] = res


NOVAR_V3 = novar_v3
