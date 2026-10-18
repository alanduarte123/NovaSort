"""NovaR4 fixed."""
from __future__ import annotations

import numpy as np

from . import recorder


def novar_v4(a: np.ndarray) -> None:
    if a.shape[0] < 48:
        from .algorithms import insertion_sort
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
    buf0 = v_f
    buf1 = np.empty_like(v_f)
    buf2 = np.empty_like(v_f)
    cur = buf0
    for shift in (0,8,16,24,32,40,48,56):
        d = (cur >> shift) & 0xFF
        c = np.bincount(d, minlength=256)
        if c.max() == n:
            continue
        s = np.cumsum(c)
        pos = np.zeros(256, dtype=np.int64)
        pos[1:] = s[:-1]
        for i in range(256):
            k = c[i]
            if k:
                m = d == i
                p = pos[i]
                buf1[p:p+k] = cur[m]
        cur, buf1, buf2 = buf1, buf2, cur
        recorder.tick()
    res = cur ^ flip
    a[:] = res


NOVAR_V4 = novar_v4
