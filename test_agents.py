import numpy as np

from sorting_showdown.nova_agents import AGENT_ALGOS


def test_agents():
    rng = np.random.default_rng(123)
    fails = []
    sizes = [0,1,2,3,10,100,500,1000,5000,10000]
    for algo in AGENT_ALGOS:
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
    print('agents checked: ok, count=', len(AGENT_ALGOS))


if __name__ == '__main__':
    test_agents()
