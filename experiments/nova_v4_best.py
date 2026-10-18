"""NovaSort v4: refinado, enfocado a batir Radix LSD."""
from __future__ import annotations

import numpy as np

from . import recorder
from .algorithms import _insertion_range, _hoare_partition


def _small_insertion(a: np.ndarray) -> None:
    n = a.shape[0]
    for i in range(1, n):
        x = a[i]
        j = int(np.searchsorted(a[:i], x, side="right"))
        if j != i:
            a[j + 1 : i + 1] = a[j:i]
            a[j] = x


def nova_v4_best(a: np.ndarray) -> None:
    if a.dtype.kind not in "iu":
        lst = a.tolist()
        n = len(lst)
        def rec(lo, hi, depth):
            while hi - lo > 16:
                if depth == 0:
                    for start in range(lo, hi):
                        x = lst[start]; j = start-1
                        while j>=lo and lst[j]>x:
                            lst[j+1]=lst[j]; j-=1
                        lst[j+1]=x
                    return
                depth -= 1
                mid = _hoare_partition(lst, lo, hi)
                if mid-lo < hi-mid:
                    rec(lo,mid,depth); lo=mid
                else:
                    rec(mid,hi,depth); hi=mid
            _insertion_range(lst, lo, hi)
        if n>1: rec(0,n,2*n.bit_length())
        a[:] = lst; return
    n = a.shape[0]
    if n < 32:
        _small_insertion(a); return
    if n > 1:
        # early exits
        # check sorted
        is_sorted = True
        # quick check
        for i in range(min(1024,n-1)):
            if a[i+1] < a[i]: is_sorted=False; break
        if is_sorted:
            # full check small cost? or trust
            if np.all(a[1:]>=a[:-1]): return
        # reversed
        is_rev = True
        for i in range(min(1024,n-1)):
            if a[i+1] > a[i]: is_rev=False; break
        if is_rev and np.all(a[1:]<=a[:-1]):
            a[:] = a[::-1]; return
    mn = int(a.min()); mx = int(a.max())
    r = mx-mn+1
    if r==1: return
    if r <= max(65536,n):
        cnts = np.bincount(a-mn, minlength=r)
        a[:] = np.repeat(np.arange(mn,mx+1,dtype=a.dtype), cnts)
        recorder.tick()
        return
    v = a - mn if mn else a.copy()
    chunk = 2048
    # low
    d0 = v & 0xFFFF
    if int(d0.min()) != int(d0.max()):
        order = np.argsort(d0, kind='stable')
        out = np.empty_like(v)
        for s in range(0,n,chunk):
            e = min(s+chunk,n)
            out[s:e] = v[order[s:e]]
        v = out
        recorder.tick()
    d1 = v >> 16
    if int(d1.min()) != int(d1.max()):
        order = np.argsort(d1, kind='stable')
        out = np.empty_like(v)
        for s in range(0,n,chunk):
            e = min(s+chunk,n)
            out[s:e] = v[order[s:e]]
        v = out
        recorder.tick()
    if mn: v+=mn
    a[:] = v

NOVA_V4_BEST = nova_v4_best
