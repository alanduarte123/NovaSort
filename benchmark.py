"""Runner de benchmark: ejecuta cada algoritmo EN SERIE en un subproceso
propio con timeout, así ningún algoritmo lento congela el proyecto.

Cada hijo regenera el mismo dataset determinista, corre su algoritmo,
y guarda tiempo + frames (downsampled) en results/runs/*.npz + .json.
El padre nunca tiene más de un hijo vivo (anti-lag / anti-memoria).
"""

from __future__ import annotations

import json
import multiprocessing as mp
import os
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

RUNS_DIR = Path(__file__).resolve().parent / "results" / "runs"


@dataclass
class RunResult:
    name: str
    seconds: float
    ok: bool
    family: str
    timed_out: bool = False
    frames: list = field(repr=False, default_factory=list)
    capture_seconds: float = 0.0

    @property
    def label(self) -> str:
        if self.timed_out:
            return "no terminó (timeout)"
        return f"{self.seconds:.4f}s"


def make_data(n: int = 50_000, high: int = 10_000_000, seed: int = 2026) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.integers(0, high, size=n).astype(np.int64)


def profile_data(profile: str, n: int = 50_000, high: int = 10_000_000, seed: int = 2026) -> np.ndarray:
    rng = np.random.default_rng(seed)
    if profile == "random":
        return rng.integers(0, high, size=n).astype(np.int64)
    if profile == "nearly_sorted":
        a = rng.integers(0, high, size=n).astype(np.int64)
        a.sort()
        idx = rng.choice(n, size=max(1, n // 50), replace=False)
        a[idx] = rng.integers(0, high, size=idx.size).astype(np.int64)
        return a
    if profile == "reversed":
        return np.sort(rng.integers(0, high, size=n).astype(np.int64))[::-1].copy()
    if profile == "few_unique":
        return rng.integers(0, 50, size=n).astype(np.int64)
    raise ValueError(profile)


def algorithm_names(include_nova_history: bool = False, include_variants: bool = False) -> list[str]:
    from .algorithms import ALGORITHMS

    names = [a.name for a in ALGORITHMS]
    if include_nova_history:
        names += ["NovaSort v1", "NovaSort v2"]
    names.append("NovaSort v3 (nuevo)")
    if include_variants:
        from . import nova_variants
        names.extend([a.name for a in nova_variants.VARIANT_ALGOS])
    return names


def _lookup(name: str):
    from . import nova
    from .algorithms import ALGORITHMS

    for a in ALGORITHMS:
        if a.name == name:
            return a.func, a.estimate, a.family
    mapping = {
        "NovaSort v1": (nova.NOVA_V1, lambda n: 8, "nuevo - hibrido"),
        "NovaSort v2": (nova.NOVA_V2, lambda n: 8, "nuevo - hibrido"),
        "NovaSort v3 (nuevo)": (nova.NOVA_V3, lambda n: 20, "nuevo - hibrido"),
    }
    if name in mapping:
        return mapping[name]
    try:
        from . import nova_variants
        for a in nova_variants.VARIANT_ALGOS:
            if a.name == name:
                return a.func, a.estimate, a.family
    except Exception:
        pass
    raise KeyError(name)


def _worker(name: str, n: int, high: int, seed: int, out_dir: str) -> None:
    from . import recorder
    from .benchmark import make_data

    data = make_data(n, high, seed)
    func, estimate, family = _lookup(name)
    arr = data.copy()
    expected = np.sort(data)
    recorder.bind_array(arr)
    recorder.activate(estimate(arr.shape[0]), max_frames=48)
    t0 = time.perf_counter()
    func(arr)
    wall = time.perf_counter() - t0
    rec = recorder.deactivate()
    recorder.set_state(None)
    seconds = max(0.0, wall - rec["capture_seconds"])
    ok = bool(np.array_equal(arr, expected))

    mins = np.stack([f[0] for f in rec["frames"]]) if rec["frames"] else np.zeros((0, 0), np.float32)
    maxs = np.stack([f[1] for f in rec["frames"]]) if rec["frames"] else np.zeros((0, 0), np.float32)
    slug = "".join(c if c.isalnum() else "_" for c in name)
    out = Path(out_dir)
    np.savez_compressed(out / f"{slug}.npz", mins=mins, maxs=maxs)
    (out / f"{slug}.json").write_text(
        json.dumps(
            {
                "name": name,
                "family": family,
                "seconds": seconds,
                "capture_seconds": rec["capture_seconds"],
                "ok": ok,
                "timed_out": False,
                "n": n,
            }
        )
    )


def run_one(name: str, n: int = 50_000, high: int = 10_000_000, seed: int = 2026,
            timeout: float = 60.0) -> RunResult:
    from .algorithms import ALGORITHMS

    family = next((a.family for a in ALGORITHMS if a.name == name), "nuevo - hibrido")
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    slug = "".join(c if c.isalnum() else "_" for c in name)
    for ext in ("npz", "json"):
        p = RUNS_DIR / f"{slug}.{ext}"
        if p.exists():
            p.unlink()

    ctx = mp.get_context("fork")
    p = ctx.Process(target=_worker, args=(name, n, high, seed, str(RUNS_DIR)))
    p.start()
    p.join(timeout)
    if p.is_alive():
        p.terminate()
        p.join(5)
        if p.is_alive():
            p.kill()
            p.join()
        return RunResult(name=name, seconds=timeout, ok=False, family=family, timed_out=True)

    meta_path = RUNS_DIR / f"{slug}.json"
    if not meta_path.exists():
        return RunResult(name=name, seconds=0.0, ok=False, family=family, timed_out=True)
    meta = json.loads(meta_path.read_text())
    npz_path = RUNS_DIR / f"{slug}.npz"
    frames = []
    if npz_path.exists():
        with np.load(npz_path) as z:
            mins, maxs = z["mins"], z["maxs"]
        frames = [(mins[i], maxs[i]) for i in range(mins.shape[0])]
    return RunResult(
        name=meta["name"],
        seconds=meta["seconds"],
        ok=meta["ok"],
        family=meta["family"],
        capture_seconds=meta["capture_seconds"],
        frames=frames,
    )


def run_all(n: int = 50_000, include_nova_history: bool = False, include_variants: bool = False,
            timeout: float = 60.0, on_result=None, high: int = 10_000_000, seed: int = 2026) -> list[RunResult]:
    results = []
    for name in algorithm_names(include_nova_history, include_variants=include_variants):
        res = run_one(name, n=n, high=high, seed=seed, timeout=timeout)
        results.append(res)
        if on_result is not None:
            on_result(res)
    return results
