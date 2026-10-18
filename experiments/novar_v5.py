"""NovaR v5: usa argsort estable por byte (delegado a C) + skips."""
from __future__ import annotations

import numpy as np

from . import recorder
from .algorithms import insertion_sort


def novar_v5(a: np.ndarray) -> None:
    if a.shape[0] < 48:
        insertion_sort(a)
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
    v_f = v ^ flip
    buf1 = np.empty_like(v_f)
    buf2 = np.empty_like(v_f)
    cur = v_f
    for shift in (0, 8, 16, 24, 32, 40, 48, 56):
        d = (cur >> shift) & 0xFF
        if d.max() == d.min():
            continue
        idx = np.argsort(d, kind='stable')
        buf1[:] = cur[idx]
        cur, buf1, buf2 = buf1, buf2, cur
        recorder.tick()
    res = cur ^ flip
    a[:] = res


NOVAR_V5 = novar_v5
