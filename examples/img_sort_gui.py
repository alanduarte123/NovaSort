#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import numpy as np
import time

from sorting_showdown import nova_vs_radix, nova, algorithms

ALGORITHMS = {
    'NovaSuper v1': nova_vs_radix.nova_super_v1,
    'NovaSort v3': nova.nova_v3,
    'Radix LSD': algorithms.radix_lsd_sort,
    'Quick Sort': algorithms.quick_sort,
}


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Image Sorter - Visual')
        self.geometry('1040x460')
        self.img_original = None
        self.img_shuffled = None
        self.img_sorted = None

        ctrl = ttk.Frame(self, padding=10)
        ctrl.pack(fill=tk.X)

        ttk.Label(ctrl, text='Algoritmo:').pack(side=tk.LEFT, padx=5)
        self.algo_var = tk.StringVar(value='NovaSuper v1')
        ttk.Combobox(ctrl, textvariable=self.algo_var, values=list(ALGORITHMS.keys()), state='readonly', width=18).pack(side=tk.LEFT, padx=5)
        ttk.Button(ctrl, text='Cargar imagen', command=self.load_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(ctrl, text='Barajar', command=self.shuffle).pack(side=tk.LEFT, padx=5)
        ttk.Button(ctrl, text='Iniciar', command=self.sort).pack(side=tk.LEFT, padx=5)
        ttk.Button(ctrl, text='Guardar', command=self.save).pack(side=tk.LEFT, padx=5)
        self.lbl_time = ttk.Label(ctrl, text='Tiempo: -')
        self.lbl_time.pack(side=tk.LEFT, padx=10)

        imgs = ttk.Frame(self)
        imgs.pack(fill=tk.BOTH, expand=True)
        self.c_orig = tk.Canvas(imgs, bg='gray', width=330, height=360)
        self.c_shuf = tk.Canvas(imgs, bg='gray', width=330, height=360)
        self.c_sort = tk.Canvas(imgs, bg='gray', width=330, height=360)
        self.c_orig.grid(row=0, column=0, padx=5, pady=5)
        self.c_shuf.grid(row=0, column=1, padx=5, pady=5)
        self.c_sort.grid(row=0, column=2, padx=5, pady=5)
        for i in range(3):
            imgs.columnconfigure(i, weight=1)
        ttk.Label(self.c_orig, text='Original', bg='gray').pack()
        ttk.Label(self.c_shuf, text='Desordenada', bg='gray').pack()
        ttk.Label(self.c_sort, text='Ordenada', bg='gray').pack()

    def _show(self, canvas, img, title=None):
        disp = img.copy()
        disp.thumbnail((320,320))
        tkimg = ImageTk.PhotoImage(disp)
        canvas.image = tkimg
        canvas.delete('all')
        canvas.create_image(165,180, anchor=tk.CENTER, image=tkimg)
        canvas.create_text(165,20, text=title or '', fill='white', font=('Arial',12,'bold'))

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[('Images','*.png *.jpg *.jpeg *.bmp')])
        if not path: return
        self.img_original = Image.open(path).convert('RGB')
        self._show(self.c_orig, self.img_original, f'Original {self.img_original.size}')

    def shuffle(self):
        if self.img_original is None: return
        arr = np.array(self.img_original)
        h,w,c = arr.shape
        flat = arr.reshape(-1,c)
        rng = np.random.default_rng(42)
        perm = rng.permutation(len(flat))
        self.img_shuffled = Image.fromarray(flat[perm].reshape(h,w,c).astype(np.uint8))
        self._show(self.c_shuf, self.img_shuffled, 'Desordenada')

    def sort(self):
        if self.img_shuffled is None: return
        func = ALGORITHMS[self.algo_var.get()]
        arr = np.array(self.img_shuffled).astype(np.int64)
        h,w,c = arr.shape
        flat = arr.reshape(-1,c)
        keys = flat[:,0]*65536 + flat[:,1]*256 + flat[:,2]
        kw = keys.copy()
        t0 = time.perf_counter()
        func(kw)
        t1 = time.perf_counter()
        lut = {}
        for i,k in enumerate(keys):
            if k not in lut: lut[k] = flat[i]
        flat_res = np.array([lut[k] for k in kw], dtype=np.uint8)
        self.img_sorted = Image.fromarray(flat_res.reshape(h,w,c))
        self._show(self.c_sort, self.img_sorted, f'Ordenada {self.algo_var.get()}')
        self.lbl_time.config(text=f'Tiempo: {t1-t0:.4f}s')

    def save(self):
        if self.img_sorted is None: return
        p = filedialog.asksaveasfilename(defaultextension='.png', filetypes=[('PNG','*.png')])
        if p: self.img_sorted.save(p)


if __name__ == '__main__':
    App().mainloop()
