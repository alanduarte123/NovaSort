"""Verificacion de correccion de todos los algoritmos (20 + Nova) en multiples perfiles."""

import sys

import numpy as np

from nova_sort.algorithms import ALGORITHMS
from nova_sort import recorder

try:
    from nova_sort.nova import NOVA_V3 as nova
    NOVAS = [("NovaSort v3", nova)]
except Exception:
    NOVAS = []

try:
    from nova_sort.nova import NOVA_V1, NOVA_V2, NOVA_V3
    NOVAS = [("NovaSort v1", NOVA_V1), ("NovaSort v2", NOVA_V2), ("NovaSort v3", NOVA_V3)]
except Exception:
    pass


def profiles(rng, n):
    yield "random", rng.integers(0, 10_000_000, size=n).astype(np.int64)
    yield "sorted", np.sort(rng.integers(0, 10_000_000, size=n).astype(np.int64))
    yield "reversed", np.sort(rng.integers(0, 10_000_000, size=n).astype(np.int64))[::-1].copy()
    yield "duplicates", rng.integers(0, 50, size=n).astype(np.int64)
    yield "all_equal", np.full(n, 7, dtype=np.int64)
    yield "negatives", rng.integers(-10_000_000, 10_000_000, size=n).astype(np.int64)
    a = rng.integers(0, 10_000_000, size=n).astype(np.int64)
    if n > 10:
        idx = rng.choice(n, size=max(1, n // 50), replace=False)
        a[idx] = rng.integers(0, 10_000_000, size=idx.size).astype(np.int64)
    yield "nearly_sorted", a


def main():
    rng = np.random.default_rng(42)
    sizes = [0, 1, 2, 3, 5, 17, 32, 33, 64, 100, 1000, 10_000]
    fails = 0
    checked = 0
    all_algos = [(alg.name, alg.func) for alg in ALGORITHMS] + NOVAS
    for name, func in all_algos:
        for n in sizes:
            for pname, base in profiles(rng, n):
                arr = base.copy()
                expected = np.sort(base)
                recorder.bind_array(arr)
                try:
                    func(arr)
                except Exception as e:
                    print(f"FAIL {name} n={n} profile={pname}: EXC {e!r}")
                    fails += 1
                    continue
                finally:
                    recorder.set_state(None)
                checked += 1
                if not np.array_equal(arr, expected):
                    print(f"FAIL {name} n={n} profile={pname}")
                    fails += 1
    print(f"\nchecked={checked} fails={fails}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
