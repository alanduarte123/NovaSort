"""Visualización secuencial (uno termina, empieza el otro).
Genera animación y gráfico comparativo sin lag (usa frames downsampled a ~900 cols)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation, colors

from .benchmark import run_all, algorithm_names, RUNS_DIR


def _load_frames(name: str):
    slug = "".join(c if c.isalnum() else "_" for c in name)
    p = RUNS_DIR / f"{slug}.npz"
    if not p.exists():
        return np.zeros((0, 0), np.float32), np.zeros((0, 0), np.float32)
    with np.load(p) as z:
        mins, maxs = z["mins"], z["maxs"]
    return mins, maxs


def animate_sequence(n: int = 50_000, high: int = 10_000_000, seed: int = 2026,
                     include_nova_history: bool = False, out_path: str | None = None) -> None:
    names = algorithm_names(include_nova_history)
    Path(RUNS_DIR).mkdir(parents=True, exist_ok=True)
    Path("sorting_showdown/results").mkdir(parents=True, exist_ok=True)

    # Ejecutar secuencial guardando frames
    results = run_all(n=n, high=high, seed=seed, include_nova_history=include_nova_history,
                      timeout=300.0)

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.set_xlim(0, 900)
    ax.set_ylim(0, 10_000_000)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Sorting Showdown: 50,000 elementos (secuencial)")

    y = np.arange(900)
    barmin = ax.bar(y, np.zeros(900), width=1.0, color="#d73027", alpha=0.7)
    barmax = ax.bar(y, np.zeros(900), width=1.0, color="#1a9850", alpha=0.3)
    text = ax.text(10, 10_000_000 * 0.95, "", fontsize=9, family="monospace")

    frame_idx_global = 0
    total_frames = sum(max(1, _load_frames(r.name)[0].shape[0]) for r in results)

    def update(frame):
        nonlocal frame_idx_global
        cur = 0
        for r in results:
            mins, maxs = _load_frames(r.name)
            fcount = mins.shape[0] if mins.size else 1
            if frame_idx_global < cur + fcount:
                k = frame_idx_global - cur
                if fcount == 0:
                    k = 0
                # render frame k
                m1 = mins[k] if mins.shape[0] > k else (mins[-1] if mins.size else np.zeros(900))
                m2 = maxs[k] if maxs.shape[0] > k else (maxs[-1] if maxs.size else np.zeros(900))
                for b, h in zip(barmin, m1):
                    b.set_height(float(h))
                for b, h in zip(barmax, m2 - m1 if False else m2):
                    b.set_height(float(max(0, m2 - m1)))
                # simpler: draw min+range? use stacked by setting bottom=min? easier: two bars
                # redraw properly
                for i, (mi, ma) in enumerate(zip(m1, m2)):
                    barmin[i].set_height(float(mi))
                    barmax[i].set_y(float(mi))
                    barmax[i].set_height(float(max(0, ma - mi)))
                text.set_text(f"{r.name}  ({k+1}/{fcount})  ok={r.ok}")
                frame_idx_global += 1
                return barmin, barmax, text
            cur += fcount
        frame_idx_global += 1
        return barmin, barmax, text

    # rebuild bars properly per frame by patching update
    return _animate_with_frames(results, fig, ax, barmin, barmax, text, total_frames, out_path)


def _animate_with_frames(results, fig, ax, barmin, barmax, text, total_frames, out_path):
    def update(i):
        acc = 0
        for r in results:
            mins, maxs = _load_frames(r.name)
            fcount = mins.shape[0] if mins.size else 1
            if i < acc + fcount:
                k = i - acc
                if mins.size == 0:
                    m1 = np.zeros(900)
                    m2 = np.zeros(900)
                else:
                    m1 = mins[k % fcount]
                    m2 = maxs[k % fcount]
                for j in range(900):
                    barmin[j].set_height(float(m1[j]))
                    barmax[j].set_y(float(m1[j]))
                    barmax[j].set_height(float(max(0.0, m2[j] - m1[j])))
                text.set_text(f"{r.name}  ({k+1}/{fcount})  ok={r.ok}  sec={r.seconds:.3f}")
                return barmin, barmax, text
            acc += fcount
        for j in range(900):
            barmin[j].set_height(0)
            barmax[j].set_height(0)
        text.set_text("Completado")
        return barmin, barmax, text

    anim = animation.FuncAnimation(fig, update, frames=max(1, total_frames), interval=30,
                                  blit=False, repeat=False)
    if out_path is None:
        out_path = "sorting_showdown/results/sorting_showdown.mp4"
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    try:
        anim.save(out_path, writer=animation.FFMpegWriter(fps=30))
    except Exception:
        try:
            anim.save(out_path.replace(".mp4", ".gif"), writer=animation.PillowWriter(fps=30))
        except Exception:
            pass
    plt.close(fig)
    return out_path
