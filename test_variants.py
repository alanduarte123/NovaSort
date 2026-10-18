import numpy as np

from nova_sort.nova_variants import VARIANT_ALGOS


def test_variants():
    rng = np.random.default_rng(123)
    fails = []
    sizes = [0,1,2,3,10,100,500,1000,5000,10000]
    for algo in VARIANT_ALGOS:
        for sz in sizes:
            base = rng.integers(-10**7,10**7,size=sz).astype(np.int64)
            a = base.copy()
            try:
                algo.func(a)
            except Exception:
                fails.append((algo.name, sz, 'exc'))
                break
            if not np.array_equal(a, np.sort(base)):
                fails.append((algo.name, sz, 'wrong'))
                break
        else:
            continue
        break
    if fails:
        print('FAILS', fails)
        raise SystemExit(1)
    print('variantes OK: ok, count=', len(VARIANT_ALGOS))


if __name__ == '__main__':
    test_variants()
