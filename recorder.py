"""Instrumentación: captura frames (downsampled) durante la ejecución de un algoritmo.

Diseño anti-lag / anti-desbordamiento:
- Solo un algoritmo se ejecuta a la vez (secuencial).
- Cada frame se guarda *reducido* a resolución de pantalla (~ancho de gráfico),
  no los 50,000 elementos crudos, así la memoria por algoritmo queda en KBs.
- El tiempo de captura se mide aparte y se descuenta del tiempo reportado.
"""

from __future__ import annotations

import numpy as np

_active = False
_state = None
_ops = 0
_next_at = 0
_step = 1
_max_frames = 0
_frames = []
_capture_seconds = 0.0


def activate(estimate_ops: int, max_frames: int = 48, display_width: int = 900) -> None:
    global _active, _state, _ops, _next_at, _step, _max_frames, _frames, _capture_seconds, _dw
    _active = True
    _state = None
    _ops = 0
    _dw = int(display_width)
    _max_frames = int(max_frames)
    _frames = []
    _capture_seconds = 0.0
    # Espaciado lineal de frames a lo largo de la corrida estimada
    estimate_ops = max(int(estimate_ops), _max_frames)
    _step = max(1, estimate_ops // _max_frames)
    _next_at = 0


def set_state(obj) -> None:
    """Permite que algoritmos que trabajan sobre una copia (p. ej. list) expongan su estado."""
    global _state
    _state = obj


def tick(ops: int = 1) -> None:
    """Los algoritmos llaman esto en puntos de control (por pase, partición, chunk...)."""
    global _ops, _next_at
    if not _active:
        return
    _ops += ops
    if _ops >= _next_at:
        _capture_frame()
        _next_at = _ops + _step


def _capture_frame() -> None:
    global _capture_seconds
    src = _state if _state is not None else _current_arr
    if src is None:
        return
    t0 = __import__("time").perf_counter()
    a = np.asarray(src)
    n = a.shape[0]
    w = _dw
    if n > w:
        buckets = n // w
        trimmed = a[: w * buckets].reshape(w, buckets)
        mins = trimmed.min(axis=1)
        maxs = trimmed.max(axis=1)
        _frames.append((mins.astype(np.float32), maxs.astype(np.float32)))
    else:
        _frames.append((a.astype(np.float32), a.astype(np.float32)))
    _capture_seconds += __import__("time").perf_counter() - t0


_current_arr = None


def bind_array(arr) -> None:
    """Asocia el ndarray que los algoritmos mutan in-place (estado por defecto)."""
    global _current_arr
    _current_arr = arr
    _state = None


def deactivate() -> dict:
    global _active
    _active = False
    return {
        "frames": _frames,
        "capture_seconds": _capture_seconds,
        "ops": _ops,
    }


def is_active() -> bool:
    return _active
