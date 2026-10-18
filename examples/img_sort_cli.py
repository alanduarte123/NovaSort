#!/usr/bin/env python3
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image

from nova_sort import nova_vs_radix, nova, algorithms

ALGO = {
    'novasuper': ('NovaSuper v1', nova_vs_radix.nova_super_v1),
    'novasort': ('NovaSort v3', nova.nova_v3),
    'radix': ('Radix LSD', algorithms.radix_lsd_sort),
    'quick': ('Quick Sort', algorithms.quick_sort),
}


def main():
    if len(sys.argv) < 3:
        print('Uso: python3 img_sort_cli.py <imagen> <novasuper|novasort|radix|quick>')
        sys.exit(1)
    path = sys.argv[1]
    ak = sys.argv[2]
    if ak not in ALGO:
        print('algoritmo inválido'); sys.exit(1)
    name, func = ALGO[ak]
    if not Path(path).exists():
        print('imagen no existe'); sys.exit(1)
    img = Image.open(path).convert('RGB')
    arr = np.array(img)
    h,w,c = arr.shape
    flat = arr.reshape(-1,c).astype(np.int64)
    rng = np.random.default_rng(42)
    perm = rng.permutation(len(flat))
    flat_sh = flat[perm].copy()
    # empaquetar RGB en clave única
    keys = flat_sh[:,0]*65536 + flat_sh[:,1]*256 + flat_sh[:,2]
    # correr algoritmo (ordena in-place sobre copia)
    kw = keys.copy()
    t0 = time.perf_counter()
    func(kw)
    t1 = time.perf_counter()
    # reconstruir imagen desde kw ya ordenado
    lut = {}
    for i, k in enumerate(keys):
        if k not in lut:
            lut[k] = flat_sh[i]
    flat_res = np.empty_like(flat_sh)
    for i, k in enumerate(kw):
        flat_res[i] = lut[k]
    flat_res = flat_res.astype(np.uint8)
    res = Image.fromarray(flat_res.reshape(h,w,c))
    out = f'/content/sorted_{ak}.png'
    res.save(out)
    print(f'{name}: {t1-t0:.4f}s -> {out}')


if __name__ == '__main__':
    main()
