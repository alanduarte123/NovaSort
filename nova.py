"""NovaSort: algoritmo hibrido nuevo, disenado para superar a los 20 anteriores.

Trayectoria de mejora iterativa (cada version benchmarkeada en benchmark_nova.py):

  v1  Insercion binaria (n<48) + chequeo de orden + LSD radix base 256 (4 pases).
  v2  + radix base 65536 (2 pases) + offset a rango no negativo
      + camino rapido de conteo cuando el rango es pequeno
      + deteccion de arreglo invertido (flip O(n)).
  v3  + salida O(n) si todos iguales + digito alto recortado (bincount pequeno)
      + modelo de costo conteo-vs-radix afin + digitos fused con out=
      + salto de pases de digito constantes.

Todos los caminos mutan in-place un np.ndarray int64.
"""

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


def _radix_lsd_base256(v: np.ndarray) -> np.ndarray:
    n = v.shape[0]
    chunk = 16384
    for shift in (0, 8, 16, 24):
        digit = (v >> shift) & 0xFF
        order = np.argsort(digit, kind="stable")
        out = np.empty_like(v)
        for s in range(0, n, chunk):
            e = min(s + chunk, n)
            out[s:e] = v[order[s:e]]
        v = out
        recorder.tick()
    return v


def nova_v1(a: np.ndarray) -> None:
    n = a.shape[0]
    if n < 48:
        _small_insertion(a)
        return
    if bool(np.all(a[1:] >= a[:-1])):
        return
    mn = int(a.min())
    v = a - mn if mn else a.copy()
    v = _radix_lsd_base256(v)
    if mn:
        v += mn
    a[:] = v


def _counting_fast(a: np.ndarray, mn: int, mx: int) -> None:
    r = mx - mn + 1
    counts = np.bincount(a - mn, minlength=r)
    a[:] = np.repeat(np.arange(mn, mx + 1, dtype=a.dtype), counts)
    recorder.tick()


def nova_v2(a: np.ndarray) -> None:
    n = a.shape[0]
    if n < 48:
        _small_insertion(a)
        return
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
        _counting_fast(a, mn, mx)
        return
    v = a - mn if mn else a.copy()
    d0 = v & 0xFFFF
    order = np.argsort(d0, kind="stable")
    v = v[order]
    recorder.tick()
    d1 = v >> 16
    order = np.argsort(d1, kind="stable")
    v = v[order]
    recorder.tick()
    if mn:
        v += mn
    a[:] = v


def _fallback(a: np.ndarray) -> None:
    lst = a.tolist()
    n = len(lst)

    def rec(lo: int, hi: int, depth: int) -> None:
        while hi - lo > 16:
            if depth == 0:
                for start in range(lo, hi):
                    x = lst[start]
                    j = start - 1
                    while j >= lo and lst[j] > x:
                        lst[j + 1] = lst[j]
                        j -= 1
                    lst[j + 1] = x
                return
            depth -= 1
            mid = _hoare_partition(lst, lo, hi)
            if mid - lo < hi - mid:
                rec(lo, mid, depth)
                lo = mid
            else:
                rec(mid, hi, depth)
                hi = mid
        _insertion_range(lst, lo, hi)

    if n > 1:
        rec(0, n, 2 * n.bit_length())
    a[:] = lst


def nova_v3(a: np.ndarray) -> None:
    if a.dtype.kind not in "iu":
        _fallback(a)
        return
    n = a.shape[0]
    if n < 48:
        _small_insertion(a)
        return
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
        _counting_fast(a, mn, mx)
        return
    v = a - mn if mn else a.copy()
    d0 = v & 0xFFFF
    if int(d0.min()) != int(d0.max()):
        order = np.argsort(d0, kind="stable")
        out = np.empty_like(v)
        n_v = v.shape[0]
        for s in range(0, n_v, 16384):
            e = min(s + 16384, n_v)
            out[s:e] = v[order[s:e]]
        v = out
        recorder.tick()
    top = int(v.max() >> 16)
    if top == 0:
        if mn:
            v += mn
        a[:] = v
        return
    d1 = np.right_shift(v, 16)
    order = np.argsort(d1, kind="stable")
    out = np.empty_like(v)
    n_v = v.shape[0]
    for s in range(0, n_v, 16384):
        e = min(s + 16384, n_v)
        out[s:e] = v[order[s:e]]
    v = out
    recorder.tick()
    if mn:
        v += mn
    a[:] = v


NOVA_V1 = nova_v1
NOVA_V2 = nova_v2
NOVA_V3 = nova_v3
