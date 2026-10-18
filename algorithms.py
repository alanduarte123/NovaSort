"""20 algoritmos de ordenamiento, optimizados para Python/numpy.

Todos mutan in-place un np.ndarray int64 y llaman a recorder.tick() en
puntos de control para la captura de frames de la visualizacion.
"""

from __future__ import annotations

import bisect
import heapq
import math
from dataclasses import dataclass
from typing import Callable

import numpy as np

from . import recorder


def _list_view(a: np.ndarray) -> list:
    lst = a.tolist()
    recorder.set_state(lst)
    return lst


def _commit(a: np.ndarray, lst: list) -> None:
    a[:] = lst
    recorder.set_state(None)


def _insertion_range(lst: list, lo: int, hi: int) -> None:
    for i in range(lo + 1, hi):
        key = lst[i]
        j = bisect.bisect_left(lst, key, lo, i)
        if j != i:
            lst[j + 1 : i + 1] = lst[j:i]
            lst[j] = key


def _median3(lst: list, lo: int, hi: int) -> int:
    mid = (lo + hi) // 2
    if lst[mid] < lst[lo]:
        lst[mid], lst[lo] = lst[lo], lst[mid]
    if lst[hi - 1] < lst[mid]:
        lst[hi - 1], lst[mid] = lst[mid], lst[hi - 1]
    if lst[mid] < lst[lo]:
        lst[mid], lst[lo] = lst[lo], lst[mid]
    return lst[mid]


def _hoare_partition(lst: list, lo: int, hi: int) -> int:
    p = _median3(lst, lo, hi)
    i, j = lo - 1, hi
    while True:
        i += 1
        while lst[i] < p:
            i += 1
        j -= 1
        while lst[j] > p:
            j -= 1
        if i >= j:
            return j + 1
        lst[i], lst[j] = lst[j], lst[i]


def _sift_down(lst: list, root: int, size: int) -> None:
    x = lst[root]
    child = 2 * root + 1
    while child < size:
        if child + 1 < size and lst[child + 1] > lst[child]:
            child += 1
        if x >= lst[child]:
            break
        lst[root] = lst[child]
        root = child
        child = 2 * root + 1
    lst[root] = x


def _heapsort_range(lst: list, lo: int, hi: int) -> None:
    size = hi - lo
    for i in range(size // 2 - 1, -1, -1):
        _sift_down(lst, lo + i, size)
    for end in range(size - 1, 0, -1):
        lst[lo], lst[lo + end] = lst[lo + end], lst[lo]
        _sift_down(lst, lo, end)


def bubble_sort(a: np.ndarray) -> None:
    n = a.shape[0]
    while True:
        any_swap = False
        for p in (0, 1):
            l = a[p : n - 1 : 2]
            r = a[p + 1 : n : 2]
            m = l > r
            if m.any():
                lc = l.copy()
                a[p : n - 1 : 2] = np.where(m, r, lc)
                a[p + 1 : n : 2] = np.where(m, lc, r)
                any_swap = True
            recorder.tick()
        if not any_swap:
            return


def cocktail_sort(a: np.ndarray) -> None:
    n = a.shape[0]
    lo, hi = 0, n - 1
    while lo < hi:
        any_swap = False
        for p in (0, 1):
            s = lo if (lo % 2 == p) else lo + 1
            if s >= hi:
                break
            l = a[s:hi:2]
            r = a[s + 1 : hi + 1 : 2]
            m = l > r
            if m.any():
                lc = l.copy()
                a[s:hi:2] = np.where(m, r, lc)
                a[s + 1 : hi + 1 : 2] = np.where(m, lc, r)
                any_swap = True
            recorder.tick()
        if not any_swap:
            return
        win = a[lo : hi + 1]
        if a[hi] == win.max():
            hi -= 1
        if lo < hi and a[lo] == a[lo : hi + 1].min():
            lo += 1


def selection_sort(a: np.ndarray) -> None:
    n = a.shape[0]
    for i in range(n - 1):
        j = i + int(np.argmin(a[i:]))
        if j != i:
            a[i], a[j] = a[j], a[i]
        recorder.tick()


def exchange_sort(a: np.ndarray) -> None:
    n = a.shape[0]
    for i in range(n - 1):
        rest = a[i + 1 :]
        m = np.argmin(rest)
        j = i + 1 + m
        if a[j] < a[i]:
            a[i], a[j] = a[j], a[i]
        recorder.tick()


def insertion_sort(a: np.ndarray) -> None:
    n = a.shape[0]
    for i in range(1, n):
        x = a[i]
        gt = a[:i] > x
        if gt.any():
            j = int(np.argmax(gt))
            a[j + 1 : i + 1] = a[j:i]
            a[j] = x
        recorder.tick()


def binary_insertion_sort(a: np.ndarray) -> None:
    n = a.shape[0]
    for i in range(1, n):
        x = a[i]
        j = int(np.searchsorted(a[:i], x, side="right"))
        if j != i:
            a[j + 1 : i + 1] = a[j:i]
            a[j] = x
        recorder.tick()


def shell_sort(a: np.ndarray) -> None:
    lst = _list_view(a)
    n = len(lst)
    if n < 2:
        _commit(a, lst)
        return
    gaps = []
    h = 1
    while h < n:
        gaps.append(h)
        h = 3 * h + 1
    gaps.reverse()
    if not gaps:
        gaps = [1]
    for g in gaps:
        for i in range(g, n):
            key = lst[i]
            j = i
            while j >= g and lst[j - g] > key:
                lst[j] = lst[j - g]
                j -= g
            lst[j] = key
        recorder.tick()
    _commit(a, lst)


def comb_sort(a: np.ndarray) -> None:
    lst = _list_view(a)
    n = len(lst)
    gap = n
    while True:
        gap = int(gap / 1.3) if gap > 1 else 1
        swapped = False
        end = n - gap
        for i in range(end):
            if lst[i] > lst[i + gap]:
                lst[i], lst[i + gap] = lst[i + gap], lst[i]
                swapped = True
            if (i & 0x1FFF) == 0:
                recorder.tick()
        if gap == 1 and not swapped:
            break
    _commit(a, lst)


def merge_sort(a: np.ndarray) -> None:
    lst = _list_view(a)
    n = len(lst)
    src, dst = lst, [0] * n
    width = 1
    while width < n:
        for i in range(0, n, 2 * width):
            mid = i + width
            if mid >= n:
                dst[i:n] = src[i:n]
                break
            end = min(i + 2 * width, n)
            l, r, w = i, mid, i
            while l < mid and r < end:
                if src[l] <= src[r]:
                    dst[w] = src[l]
                    l += 1
                else:
                    dst[w] = src[r]
                    r += 1
                w += 1
            if l < mid:
                dst[w:end] = src[l:mid]
            elif r < end:
                dst[w:end] = src[r:end]
        src, dst = dst, src
        recorder.tick()
        width <<= 1
    _commit(a, src)


def quick_sort(a: np.ndarray) -> None:
    lst = _list_view(a)

    def rec(lo: int, hi: int) -> None:
        while hi - lo > 32:
            recorder.tick()
            mid = _hoare_partition(lst, lo, hi)
            if mid - lo < hi - mid:
                rec(lo, mid)
                lo = mid
            else:
                rec(mid, hi)
                hi = mid
        _insertion_range(lst, lo, hi)

    if len(lst) > 1:
        rec(0, len(lst))
    _commit(a, lst)


def heap_sort(a: np.ndarray) -> None:
    lst = _list_view(a)
    n = len(lst)
    for i in range(n // 2 - 1, -1, -1):
        _sift_down(lst, i, n)
    for end in range(n - 1, 0, -1):
        lst[0], lst[end] = lst[end], lst[0]
        _sift_down(lst, 0, end)
        recorder.tick()
    _commit(a, lst)


def intro_sort(a: np.ndarray) -> None:
    lst = _list_view(a)
    n = len(lst)

    def rec(lo: int, hi: int, depth: int) -> None:
        while hi - lo > 16:
            recorder.tick()
            if depth == 0:
                _heapsort_range(lst, lo, hi)
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
    _commit(a, lst)


def _minrun(n: int) -> int:
    r = 0
    while n >= 64:
        r |= n & 1
        n >>= 1
    return n + r


def tim_sort(a: np.ndarray) -> None:
    lst = _list_view(a)
    n = len(lst)
    if n < 2:
        _commit(a, lst)
        return
    minrun = _minrun(n)
    runs: list[tuple[int, int]] = []
    i = 0
    while i < n:
        j = i + 1
        if j < n and lst[j] < lst[i]:
            while j < n and lst[j] < lst[j - 1]:
                j += 1
            lst[i:j] = lst[i:j][::-1]
        else:
            while j < n and lst[j] >= lst[j - 1]:
                j += 1
        stop = min(i + minrun, n)
        if j < stop:
            for k in range(j, stop):
                key = lst[k]
                pos = bisect.bisect_left(lst, key, i, k)
                if pos != k:
                    lst[pos + 1 : k + 1] = lst[pos:k]
                    lst[pos] = key
            j = stop
        runs.append((i, j))
        recorder.tick()
        i = j

    def merge(a0: int, a1: int, b0: int, b1: int) -> None:
        left = lst[a0:a1]
        li, ri, w = 0, b0 - a0, a0
        right_end = b1 - a0
        full = lst[a0:b1]
        while li < len(left) and ri < right_end:
            if left[li] <= full[ri]:
                lst[w] = left[li]
                li += 1
            else:
                lst[w] = full[ri]
                ri += 1
            w += 1
        if li < len(left):
            lst[w:b1] = left[li:]
        elif ri < right_end:
            lst[w:b1] = full[ri:]

    stack: list[tuple[int, int]] = []
    for r in runs:
        stack.append(r)
        while len(stack) > 1:
            yl = stack[-2][1] - stack[-2][0]
            zl = stack[-1][1] - stack[-1][0]
            if len(stack) >= 3:
                xl = stack[-3][1] - stack[-3][0]
                if xl <= yl + zl:
                    if xl < zl:
                        s0, s1 = stack.pop(-3), stack.pop(-2)
                        merge(s0[0], s0[1], s1[0], s1[1])
                        stack.insert(-1, (s0[0], s1[1]))
                    else:
                        s0, s1 = stack.pop(-2), stack.pop(-1)
                        merge(s0[0], s0[1], s1[0], s1[1])
                        stack.append((s0[0], s1[1]))
                    recorder.tick()
                    continue
            if yl <= zl:
                s0, s1 = stack.pop(-2), stack.pop(-1)
                merge(s0[0], s0[1], s1[0], s1[1])
                stack.append((s0[0], s1[1]))
                recorder.tick()
            else:
                break
    while len(stack) > 1:
        s0 = stack.pop(-2)
        s1 = stack.pop(-1)
        merge(s0[0], s0[1], s1[0], s1[1])
        stack.append((s0[0], s1[1]))
        recorder.tick()
    _commit(a, lst)


def patience_sort(a: np.ndarray) -> None:
    lst = _list_view(a)
    n = len(lst)
    piles: list[list] = []
    tops: list[int] = []
    for k in range(n):
        x = lst[k]
        pos = bisect.bisect_left(tops, x)
        if pos == len(piles):
            piles.append([x])
            tops.append(x)
        else:
            piles[pos].append(x)
            tops[pos] = x
        if (k & 0x3FF) == 0:
            recorder.tick()
    heap = [(p[-1], i, len(p) - 1) for i, p in enumerate(piles)]
    heapq.heapify(heap)
    w = 0
    while heap:
        v, pi, idx = heapq.heappop(heap)
        lst[w] = v
        w += 1
        if idx > 0:
            heapq.heappush(heap, (piles[pi][idx - 1], pi, idx - 1))
        if (w & 0x3FF) == 0:
            recorder.tick()
    _commit(a, lst)


def counting_sort(a: np.ndarray) -> None:
    if a.shape[0] < 2:
        return
    mn = int(a.min())
    mx = int(a.max())
    r = mx - mn + 1
    counts = np.bincount(a - mn, minlength=r)
    recorder.tick()
    values = np.arange(mn, mx + 1, dtype=a.dtype)
    a[:] = np.repeat(values, counts)
    recorder.tick()


def radix_lsd_sort(a: np.ndarray) -> None:
    if a.shape[0] < 2:
        return
    mn = int(a.min())
    v = a - mn
    n = v.shape[0]
    chunk = 8192
    for shift in (0, 8, 16, 24):
        digit = (v >> shift) & 0xFF
        order = np.argsort(digit, kind="stable")
        out = np.empty_like(v)
        for s in range(0, n, chunk):
            e = min(s + chunk, n)
            out[s:e] = v[order[s:e]]
            recorder.tick()
        v = out
    if mn:
        v += mn
    a[:] = v


def radix_msd_sort(a: np.ndarray) -> None:
    if a.shape[0] < 2:
        return
    mn = int(a.min())
    v = (a - mn).astype(np.int64, copy=True)
    n = v.shape[0]

    def rec(lo: int, hi: int, shift: int) -> None:
        size = hi - lo
        if size < 2:
            return
        if size <= 64 or shift < 0:
            seg = np.sort(v[lo:hi])
            v[lo:hi] = seg
            recorder.tick()
            return
        digit = (v[lo:hi] >> shift) & 0xFF
        counts = np.bincount(digit, minlength=256)
        order = np.argsort(digit, kind="stable")
        v[lo:hi] = v[lo:hi][order]
        recorder.tick()
        start = lo
        for d in range(256):
            c = int(counts[d])
            if c > 1:
                rec(start, start + c, shift - 8)
            start += c

    rec(0, n, 24)
    if mn:
        v += mn
    a[:] = v


def bucket_sort(a: np.ndarray) -> None:
    n = a.shape[0]
    if n < 2:
        return
    mn = int(a.min())
    mx = int(a.max())
    if mx == mn:
        return
    nb = min(n, max(8, int(math.sqrt(n))))
    r = mx - mn + 1
    idx = np.minimum(((a - mn) * (nb / r)).astype(np.int64), nb - 1)
    buckets: list[list] = [[] for _ in range(nb)]
    for i in range(n):
        buckets[int(idx[i])].append(int(a[i]))
        if (i & 0x1FFF) == 0:
            recorder.tick()
    pos = 0
    for b in buckets:
        lb = len(b)
        if lb > 1:
            b.sort()
        if lb:
            a[pos : pos + lb] = b
            pos += lb
        recorder.tick()


def bitonic_sort(a: np.ndarray) -> None:
    n = a.shape[0]
    if n < 2:
        return
    size = 1 << (n - 1).bit_length()
    fill = np.iinfo(a.dtype).max
    work = np.empty(size, dtype=a.dtype)
    work[:n] = a
    work[n:] = fill
    all_i = np.arange(size)
    logn = size.bit_length() - 1
    for k in range(1, logn + 1):
        K = 1 << k
        for j in range(k, 0, -1):
            J = 1 << (j - 1)
            left = all_i[(all_i & J) == 0]
            right = left ^ J
            up = (left & K) == 0
            x = work[left]
            y = work[right]
            work[left] = np.where(up, np.minimum(x, y), np.maximum(x, y))
            work[right] = np.where(up, np.maximum(x, y), np.minimum(x, y))
            recorder.tick()
    a[:] = work[:n]


def flash_sort(a: np.ndarray) -> None:
    n = a.shape[0]
    if n < 2:
        return
    mn = int(a.min())
    mx = int(a.max())
    if mx == mn:
        return
    m = min(n, max(16, int(4 * math.sqrt(n))))
    idx = np.minimum(((a - mn) * (m / (mx - mn + 1))).astype(np.int64), m - 1)
    counts = np.bincount(idx, minlength=m)
    starts = np.zeros(m + 1, dtype=np.int64)
    np.cumsum(counts, out=starts[1:])
    out = np.empty(n, dtype=a.dtype)
    cursor = starts[:m].copy()
    for i in range(n):
        k = int(idx[i])
        out[cursor[k]] = a[i]
        cursor[k] += 1
        if (i & 0x1FFF) == 0:
            recorder.tick()
    for b in range(m):
        lo = int(starts[b])
        hi = int(starts[b + 1])
        for i in range(lo + 1, hi):
            key = out[i]
            j = i - 1
            while j >= lo and out[j] > key:
                out[j + 1] = out[j]
                j -= 1
            out[j + 1] = key
        recorder.tick()
    a[:] = out


@dataclass(frozen=True)
class Algorithm:
    name: str
    func: Callable[[np.ndarray], None]
    estimate: Callable[[int], int]
    family: str


def _est_constant(k: int):
    return lambda n: k


def _est_n(div: int = 1):
    return lambda n: max(1, n // div)


ALGORITHMS: list[Algorithm] = [
    Algorithm("Bubble Sort", bubble_sort, _est_n(), "O(n^2) - familia bubble"),
    Algorithm("Cocktail Shaker", cocktail_sort, _est_n(2), "O(n^2) - familia bubble"),
    Algorithm("Selection Sort", selection_sort, _est_n(), "O(n^2) - seleccion"),
    Algorithm("Exchange Sort", exchange_sort, _est_n(), "O(n^2) - intercambio"),
    Algorithm("Insertion Sort", insertion_sort, _est_n(), "O(n^2) - insercion"),
    Algorithm("Binary Insertion", binary_insertion_sort, _est_n(), "O(n^2) - insercion"),
    Algorithm("Shell Sort", shell_sort, lambda n: max(1, n * 13 // 4096), "O(n^1.3) - incrementos"),
    Algorithm("Comb Sort", comb_sort, lambda n: max(1, n * n // 2 // 8192), "O(n^2) - gap"),
    Algorithm("Merge Sort", merge_sort, _est_n(), "O(n log n) - fusion"),
    Algorithm("Quick Sort", quick_sort, lambda n: max(1, 2 * n), "O(n log n) - particion"),
    Algorithm("Heap Sort", heap_sort, lambda n: max(1, 3 * n // 2), "O(n log n) - monticulo"),
    Algorithm("Introsort", intro_sort, lambda n: max(1, 2 * n), "O(n log n) - hibrido"),
    Algorithm("Timsort", tim_sort, lambda n: max(1, n // 8), "O(n log n) - adaptativo"),
    Algorithm("Patience Sort", patience_sort, lambda n: max(1, n // 512), "O(n log n) - pilas"),
    Algorithm("Counting Sort", counting_sort, _est_constant(2), "O(n+r) - histograma"),
    Algorithm("Radix LSD", radix_lsd_sort, lambda n: max(1, 5 * n // 8192), "O(nk) - digitos"),
    Algorithm("Radix MSD", radix_msd_sort, lambda n: max(1, 4 * n // 8192), "O(nk) - digitos"),
    Algorithm("Bucket Sort", bucket_sort, lambda n: max(1, n // 8192 + 256), "O(n) - cubetas"),
    Algorithm("Bitonic Sort", bitonic_sort, _est_constant(136), "O(n log^2 n) - red"),
    Algorithm("Flash Sort", flash_sort, lambda n: max(1, n // 8192 + 300), "O(n) - clasificacion"),
]
