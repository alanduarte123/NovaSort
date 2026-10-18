// Código fuente para mostrar en las pestañas
const CODE_SOURCES = {
    python: {
        novasuper: `def nova_super_v1(a: np.ndarray) -> None:
    if a.dtype.kind not in "iu":
        _fallback(a); return
    n = a.shape[0]
    if n < 32:
        _insertion_small(a); return
    if n > 1:
        limit = min(4096, n-1)
        sorted_f = True
        for i in range(limit):
            if a[i+1] < a[i]:
                sorted_f=False; break
        if sorted_f and np.all(a[1:]>=a[:-1]): return
        rev_f = True
        for i in range(limit):
            if a[i+1] > a[i]:
                rev_f=False; break
        if rev_f and np.all(a[1:]<=a[:-1]):
            a[:] = a[::-1]; return
    mn = int(a.min()); mx = int(a.max())
    r = mx-mn+1
    if r <= max(65536, n):
        cnts = np.bincount(a-mn, minlength=r)
        a[:] = np.repeat(np.arange(mn,mx+1,dtype=a.dtype), cnts)
        return
    v = a - mn if mn else a.copy()
    chunk = 512
    # radix 16-bit low then high
    d0 = v & 0xFFFF
    if int(d0.min()) != int(d0.max()):
        order = np.argsort(d0, kind='stable')
        out = np.empty_like(v)
        for s in range(0,n,chunk):
            e = min(s+chunk,n); out[s:e]=v[order[s:e]]
        v = out
    d1 = v >> 16
    if int(d1.min()) != int(d1.max()):
        order = np.argsort(d1, kind='stable')
        out = np.empty_like(v)
        for s in range(0,n,chunk):
            e = min(s+chunk,n); out[s:e]=v[order[s:e]]
        v = out
    if mn: v += mn
    a[:] = v`,
        novasort: `# NovaSort v3 - implementación de referencia`,
        radix: `# Radix LSD`,
        quick: `# Quick Sort`
    },
    javascript: {
        novasuper: `function novaSuper(a){
  let n = a.length;
  if(n <= 1) return a.slice();
  if(n < 32){ /* inserción */ }
  let minv=a[0], maxv=a[0];
  for(let i=1;i<n;i++){ if(a[i]<minv) minv=a[i]; if(a[i]>maxv) maxv=a[i]; }
  let r=maxv-minv+1, limit=Math.max(65536,n);
  if(r>=1 && r<=limit){
    let cnt=new Array(r).fill(0);
    for(let i=0;i<n;i++) cnt[a[i]-minv]++;
    let k=0,out=new Array(n);
    for(let i=0;i<r;i++){
      let v=minv+i,c=cnt[i];
      for(let j=0;j<c;j++) out[k++]=v;
    }
    return out;
  }
  let v=a.slice(); let msk=0xFFFF;
  let voff=v.map(x=>x-minv);
  let d0=voff.map(x=>x&msk);
  let idx0=argsortStable(d0);
  let v1=idx0.map(i=>voff[i]);
  let d1=v1.map(x=>(x>>16)&msk);
  let idx1=argsortStable(d1);
  return idx1.map(i=>v1[i]+minv);
}`,
        novasort: `// NovaSort v3`,
        radix: `// Radix LSD`,
        quick: `// Quick Sort`
    },
    c: {
        novasuper: `void nova_super(int64_t *a, int n){
  if(n<=1) return;
  if(n<32){ insertion_small(a,n); return; }
  int64_t minv=a[0],maxv=a[0];
  for(int i=1;i<n;i++){ if(a[i]<minv)minv=a[i]; if(a[i]>maxv)maxv=a[i]; }
  int64_t r=maxv-minv+1; int limit=max(65536,n);
  if(r>=1 && r<=limit){
    int *cnt=calloc(limit>r?r:limit,sizeof(int));
    // counting
  }
  // radix 16-bit
}`,
        novasort: `// NovaSort v3`,
        radix: `// Radix LSD`,
        quick: `// Quick Sort`
    },
    java: {
        novasuper: `public static void sort(long[] a){
  int n=a.length;
  if(n<32){ insertion(a); return; }
  long minv=a[0],maxv=a[0];
  for(int i=1;i<n;i++){ if(a[i]<minv)minv=a[i]; if(a[i]>maxv)maxv=a[i]; }
  long r=maxv-minv+1; int limit=Math.max(65536,n);
  if(r>=1 && r<=limit){
    int[] cnt=new int[(int)r];
    for(int i=0;i<n;i++) cnt[(int)(a[i]-minv)]++;
    int k=0;
    for(int i=0;i<(int)r;i++){
      long v=minv+i; int c=cnt[i];
      Arrays.fill(a,k,k+c,v); k+=c;
    }
    return;
  }
  // radix
}`,
        novasort: `// NovaSort v3`,
        radix: `// Radix LSD`,
        quick: `// Quick Sort`
    },
    php: {
        novasuper: `function nova_super($a){
  $n=count($a); if($n<=1) return $a;
  $arr=array_values($a);
  $minv=$arr[0]; $maxv=$arr[0];
  for($i=1;$i<$n;$i++){
    if($arr[$i]<$minv)$minv=$arr[$i]; if($arr[$i]>$maxv)$maxv=$arr[$i];
  }
  $r=$maxv-$minv+1; $limit=max(65536,$n);
  if($r>=1 && $r<=$limit){
    $cnt=array_fill(0,$r,0);
    for($i=0;$i<$n;$i++) $cnt[$arr[$i]-$minv]++;
    $out=[]; for($i=0;$i<$r;$i++){
      $val=$minv+$i; $c=$cnt[$i];
      for($j=0;$j<$c;$j++) $out[]=$val;
    }
    return $out;
  }
  // radix 16-bit
}`,
        novasort: `// NovaSort v3`,
        radix: `// Radix LSD`,
        quick: `// Quick Sort`
    }
};

const PSEUDOCODE = {
    novasuper: `1. Si array < 32 elementos: usar inserción\n2. Comprobar si ya está ordenado o invertido\n3. Encontrar min/max\n4. Si rango pequeño: counting sort\n5. Si rango grande: radix 16-bit (bajo + alto) con argsort estable`,
    novasort: `1. Verificar orden\n2. Inserción para n pequeño\n3. Híbrido optimizado`,
    radix: `1. LSD por dígitos base 256\n2. Counting sort por cada byte`,
    quick: `1. Elegir pivote\n2. Particionar\n3. Recursivo por subarrays`
};

// Visualizador simple
let array = [];
let algorithm = 'novasuper';
let speed = 15;
let isPlaying = false;
let intervalId = null;
let comparisons = 0;
let swaps = 0;

function generateArray(size) {
    array = [];
    for (let i = 0; i < size; i++) {
        array.push(Math.floor(Math.random() * 100) + 1);
    }
    comparisons = 0;
    swaps = 0;
    updateStats();
    renderBars();
    setStatus('Listo');
}

function renderBars() {
    const barsContainer = document.getElementById('bars');
    barsContainer.innerHTML = '';
    if (array.length === 0) return;
    const maxVal = Math.max(...array);
    array.forEach(val => {
        const bar = document.createElement('div');
        bar.className = 'bar';
        bar.style.height = (val / maxVal * 100) + '%';
        barsContainer.appendChild(bar);
    });
}

function updateStats() {
    document.getElementById('comparisons').textContent = comparisons;
    document.getElementById('swaps').textContent = swaps;
}

function setStatus(msg) {
    document.getElementById('status').textContent = msg;
}

function updateCode() {
    const lang = document.querySelector('.tab-button.active').dataset.tab;
    const algo = document.getElementById('algorithm').value;
    document.getElementById('code-python').textContent = CODE_SOURCES.python[algo] || '';
    document.getElementById('code-javascript').textContent = CODE_SOURCES.javascript[algo] || '';
    document.getElementById('code-c').textContent = CODE_SOURCES.c[algo] || '';
    document.getElementById('code-java').textContent = CODE_SOURCES.java[algo] || '';
    document.getElementById('code-php').textContent = CODE_SOURCES.php[algo] || '';
    document.getElementById('pseudocode').textContent = PSEUDOCODE[algo] || '';
}

function togglePlay() {
    if (!isPlaying) {
        isPlaying = true;
        document.getElementById('play').disabled = true;
        document.getElementById('pause').disabled = false;
        document.getElementById('step').disabled = true;
        setStatus('Ejecutando...');
        intervalId = setInterval(() => {
            // demo: simple animation
            const bars = document.querySelectorAll('.bar');
            if (bars.length > 0) {
                bars.forEach((b, i) => {
                    b.classList.toggle('comparing', i % 2 === 0);
                });
            }
        }, 1000 / speed);
    }
}

function pause() {
    if (isPlaying) {
        isPlaying = false;
        document.getElementById('play').disabled = false;
        document.getElementById('pause').disabled = true;
        document.getElementById('step').disabled = false;
        clearInterval(intervalId);
        setStatus('Pausado');
        document.querySelectorAll('.bar').forEach(b => b.classList.remove('comparing', 'swapping'));
    }
}

function step() {
    comparisons++;
    updateStats();
    document.querySelectorAll('.bar').forEach(b => b.classList.remove('comparing'));
    const bars = document.querySelectorAll('.bar');
    if (bars.length >= 2) {
        const i = Math.floor(Math.random() * bars.length);
        const j = (i + 1) % bars.length;
        bars[i].classList.add('comparing');
        bars[j].classList.add('comparing');
    }
    setStatus('Paso ejecutado');
}

function reset() {
    pause();
    const size = parseInt(document.getElementById('arraySize').value);
    generateArray(size);
}

document.getElementById('generate').addEventListener('click', () => {
    const size = parseInt(document.getElementById('arraySize').value);
    generateArray(size);
});

document.getElementById('play').addEventListener('click', togglePlay);
document.getElementById('pause').addEventListener('click', pause);
document.getElementById('step').addEventListener('click', step);
document.getElementById('reset').addEventListener('click', reset);

document.getElementById('arraySize').addEventListener('input', (e) => {
    document.getElementById('sizeValue').textContent = e.target.value;
    if (!isPlaying) {
        generateArray(parseInt(e.target.value));
    }
});

document.getElementById('speed').addEventListener('input', (e) => {
    document.getElementById('speedValue').textContent = e.target.value;
    speed = parseInt(e.target.value);
    if (isPlaying && intervalId) {
        clearInterval(intervalId);
        intervalId = setInterval(() => {}, 1000 / speed);
    }
});

document.getElementById('algorithm').addEventListener('change', () => {
    updateCode();
});

document.querySelectorAll('.tab-button').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
        updateCode();
    });
});

// Inicializar
generateArray(50);
updateCode();
