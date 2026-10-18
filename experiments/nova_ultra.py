"""NovaUltra: combina bucket-wise + early skip + counting."""
from __future__ import annotations

import numpy as np

from . import recorder


def nova_ultra(a: np.ndarray) -> None:
    if a.shape[0] < 32:
        from .algorithms import insertion_sort
        insertion_sort(a)
        return
    n = a.shape[0]
    if n > 1:
        # quick check sorted/rev
        limit = min(4096, n-1)
        is_s = True
        for i in range(limit):
            if a[i+1] < a[i]:
                is_s=False; break
        if is_s and np.all(a[1:]>=a[:-1]): return
        is_r = True
        for i in range(limit):
            if a[i+1] > a[i]:
                is_r=False; break
        if is_r and np.all(a[1:]<=a[:-1]):
            a[:] = a[::-1]; return
    mn = int(a.min()); mx = int(a.max())
    r = mx-mn+1
    if r==1: return
    if r <= max(65536,n):
        cnts = np.bincount(a-mn, minlength=r)
        a[:] = np.repeat(np.arange(mn,mx+1,dtype=a.dtype), cnts)
        recorder.tick()
        return
    v = a.astype(np.int64, copy=True)
    flip = np.int64(1)<<63
    v_f = v ^ flip
    buf = [np.empty_like(v_f), np.empty_like(v_f)]
    buf[0][:] = v_f
    cur = 0
    for shift in (0,8,16,24,32,40,48,56):
        src = buf[cur]; dst = buf[1-cur]
        d = (src >> shift) & 0xFF
        c = np.bincount(d, minlength=256)
        if c.max() == n: cur=1-cur; continue
        pos = np.zeros(256, dtype=np.int64)
        pos[1:] = np.cumsum(c)[:-1]
        for i in range(256):
            k=c[i]
            if k:
                m = d==i
                p = pos[i]
                dst[p:p+k] = src[m]
        cur = 1-cur
        recorder.tick()
    res = buf[cur] ^ flip
    a[:] = res


NOVA_ULTRA = nova_ultra
