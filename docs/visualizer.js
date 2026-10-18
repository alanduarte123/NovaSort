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
        novasort: `# NovaSort v3 - implementación de referencia\n# Ver repositorio: algorithms/nova.py`,
        radix: `# Radix LSD\n# Ver algorithms.py`,
        quick: `def quick_sort(a):
    def _q(l,r):
        if l>=r: return
        p=a[l]; i=l+1;j=r
        while True:
            while i<=j and a[i]<p: i+=1
            while i<=j and a[j]>p: j-=1
            if i>j: break
            a[i],a[j]=a[j],a[i]; i+=1;j-=1
        a[l],a[j]=a[j],a[l]
        _q(l,j-1); _q(j+1,r)
    _q(0,len(a)-1)`,
    },
    javascript: {
        novasuper: `function novaSuper(a){
  let n=a.length; if(n<=1)return a.slice();
  if(n<32){ for(let i=1;i<n;i++){let v=a[i],j=i-1;while(j>=0&&a[j]>v){a[j+1]=a[j];j--;}a[j+1]=v;} return a.slice(); }
  let arr=a.slice();
  let minv=arr[0],maxv=arr[0];
  for(let i=1;i<n;i++){ if(arr[i]<minv)minv=arr[i]; if(arr[i]>maxv)maxv=arr[i]; }
  let r=maxv-minv+1, limit=Math.max(65536,n);
  if(r>=1&&r<=limit){
    let cnt=new Array(r).fill(0);
    for(let i=0;i<n;i++) cnt[arr[i]-minv]++;
    let k=0,out=new Array(n);
    for(let i=0;i<r;i++){ let v=minv+i,c=cnt[i]; for(let j=0;j<c;j++) out[k++]=v; }
    return out;
  }
  let voff=arr.map(x=>x-minv);
  let msk=0xFFFF;
  let d0=voff.map(x=>x&msk);
  let idx0=argsortStable(d0);
  let v1=idx0.map(i=>voff[i]);
  let d1=v1.map(x=>(x>>16)&msk);
  let idx1=argsortStable(d1);
  return idx1.map(i=>v1[i]+minv);
}
function argsortStable(b){ let idx=Array.from({length:b.length},(_,i)=>i); idx.sort((i,j)=>{if(b[i]<b[j])return-1;if(b[i]>b[j])return 1;return i-j;}); return idx; }`,
        novasort: `// NovaSort v3\n// Ver ports/javascript/`,
        radix: `// Radix LSD`,
        quick: `function quickSort(arr,l,r){
  if(l>=r)return; let p=arr[l],i=l+1,j=r;
  while(true){
    while(i<=j&&arr[i]<=p)i++; while(i<=j&&arr[j]>p)j--;
    if(i>j)break; [arr[i],arr[j]]=[arr[j],arr[i]]; i++; j--;
  }
  [arr[l],arr[j]]=[arr[j],arr[l]];
  quickSort(arr,l,j-1); quickSort(arr,j+1,r);
}`,
    },
    c: { novasuper: `// Ver ports/c/nova_super.c`, novasort: `// NovaSort v3`, radix: `// Radix LSD`, quick: `// Quick Sort` },
    java: { novasuper: `// Ver ports/java/NovaSuper.java`, novasort: `// NovaSort v3`, radix: `// Radix LSD`, quick: `// Quick Sort` },
    php: { novasuper: `// Ver ports/php/nova_super.php`, novasort: `// NovaSort v3`, radix: `// Radix LSD`, quick: `// Quick Sort` }
};

const PSEUDOCODE = {
    novasuper: `1. Si n < 32: inserción\n2. Ordenado/invertido? early exit\n3. Rango ≤ max(65536,n)? counting\n4. Sino: radix 16-bit low→high (argsort estable)`,
    novasort: `1. Early check\n2. Inserción pequeña\n3. Camino híbrido optimizado`,
    radix: `1. LSD por bytes (base 256)\n2. Counting por cada dígito`,
    quick: `1. Pivote (Lomuto)\n2. Particionar\n3. Recursión izquierda/derecha`
};

let array = [];
let algorithm = 'novasuper';
let speed = 15;
let isPlaying = false;
let intervalId = null;
let comparisons = 0;
let swaps = 0;
let steps = [];
let stepIndex = 0;

function cloneArr(a){ return a.slice(); }

function generateArray(size){
    array = [];
    for(let i=0;i<size;i++) array.push(Math.floor(Math.random()*100)+1);
    comparisons=0; swaps=0; stepIndex=0; steps=[];
    updateStats(); renderBars(); setStatus('Listo');
    buildQuickSteps();
}

function buildQuickSteps(){
    if(algorithm !== 'quick') return;
    let a = cloneArr(array);
    steps=[];
    function qs(l,r){
        if(l>=r) return;
        let p=a[l], i=l+1, j=r;
        steps.push({type:'pivot', indices:[l], array:cloneArr(a)});
        while(true){
            while(i<=j && a[i]<=p){ i++; comparisons++; steps.push({type:'compare', indices:[i-1,l], array:cloneArr(a)}); }
            while(i<=j && a[j]>p){ j--; comparisons++; steps.push({type:'compare', indices:[i,j], array:cloneArr(a)}); }
            if(i>j) break;
            // swap
            let tmp=a[i]; a[i]=a[j]; a[j]=tmp; swaps++;
            steps.push({type:'swap', indices:[i,j], array:cloneArr(a)});
            i++; j--;
        }
        tmp=a[l]; a[l]=a[j]; a[j]=tmp; swaps++;
        steps.push({type:'swap', indices:[l,j], array:cloneArr(a), pivotDone:true});
        qs(l,j-1); qs(j+1,r);
    }
    qs(0,a.length-1);
    steps.push({type:'done', array:cloneArr(a)});
}

function renderBars(arrToShow){
    const barsContainer = document.getElementById('bars');
    barsContainer.innerHTML='';
    let data = arrToShow || array;
    if(data.length===0) return;
    const maxVal = Math.max(...data);
    data.forEach((val,idx)=>{
        const bar=document.createElement('div');
        bar.className='bar';
        bar.style.height=(val/maxVal*100)+'%';
        barsContainer.appendChild(bar);
    });
}

function applyStepState(state){
    const bars=document.querySelectorAll('.bar');
    bars.forEach(b=>b.classList.remove('comparing','swapping','pivot','sorted'));
    renderBars(state.array);
    array = state.array;
    updateStats();
    if(state.type==='pivot') document.querySelectorAll('.bar')[state.indices[0]].classList.add('pivot');
    if(state.type==='compare') state.indices.forEach(i=>{ if(document.querySelectorAll('.bar')[i]) document.querySelectorAll('.bar')[i].classList.add('comparing'); });
    if(state.type==='swap') state.indices.forEach(i=>{ if(document.querySelectorAll('.bar')[i]) document.querySelectorAll('.bar')[i].classList.add('swapping'); });
    if(state.type==='done') document.querySelectorAll('.bar').forEach(b=>b.classList.add('sorted'));
}

function updateStats(){
    document.getElementById('comparisons').textContent=comparisons;
    document.getElementById('swaps').textContent=swaps;
}

function setStatus(msg){ document.getElementById('status').textContent=msg; }

function updateCode(){
    const lang=document.querySelector('.tab-button.active').dataset.tab;
    const algo=document.getElementById('algorithm').value;
    document.getElementById('code-python').textContent=CODE_SOURCES.python[algo]||'';
    document.getElementById('code-javascript').textContent=CODE_SOURCES.javascript[algo]||'';
    document.getElementById('code-c').textContent=CODE_SOURCES.c[algo]||'';
    document.getElementById('code-java').textContent=CODE_SOURCES.java[algo]||'';
    document.getElementById('code-php').textContent=CODE_SOURCES.php[algo]||'';
    document.getElementById('pseudocode').textContent=PSEUDOCODE[algo]||'';
}

function togglePlay(){
    if(isPlaying) return;
    if(algorithm==='quick' && steps.length===0) buildQuickSteps();
    isPlaying=true;
    document.getElementById('play').disabled=true;
    document.getElementById('pause').disabled=false;
    document.getElementById('step').disabled=true;
    setStatus('Ejecutando...');
    if(algorithm==='quick'){
        intervalId=setInterval(()=>{
            if(stepIndex < steps.length){
                applyStepState(steps[stepIndex++]);
            }else{
                pause();
                setStatus('Finalizado');
            }
        }, 1000/speed);
    }else{
        intervalId=setInterval(()=>{
            // para otros algoritmos: demo visual
            const bars=document.querySelectorAll('.bar');
            bars.forEach((b,i)=>b.classList.toggle('comparing', i%3===0));
        }, 800);
    }
}

function pause(){
    isPlaying=false;
    document.getElementById('play').disabled=false;
    document.getElementById('pause').disabled=true;
    document.getElementById('step').disabled=false;
    clearInterval(intervalId);
    setStatus('Pausado');
    document.querySelectorAll('.bar').forEach(b=>b.classList.remove('comparing','swapping'));
}

function step(){
    if(algorithm==='quick'){
        if(steps.length===0) buildQuickSteps();
        if(stepIndex < steps.length){
            applyStepState(steps[stepIndex++]);
            comparisons = stepIndex>0 ? (steps[stepIndex-1].type==='compare'?comparisons+1:comparisons) : comparisons;
            swaps = stepIndex>0 ? (steps[stepIndex-1].type==='swap'?swaps+1:swaps) : swaps;
            updateStats();
        }
    }else{
        comparisons++; updateStats();
    }
}

function reset(){
    pause();
    const size=parseInt(document.getElementById('arraySize').value);
    generateArray(size);
    renderBars();
}

document.getElementById('generate').addEventListener('click', ()=>{ const size=parseInt(document.getElementById('arraySize').value); generateArray(size); });
document.getElementById('play').addEventListener('click', togglePlay);
document.getElementById('pause').addEventListener('click', pause);
document.getElementById('step').addEventListener('click', step);
document.getElementById('reset').addEventListener('click', reset);
document.getElementById('arraySize').addEventListener('input', e=>{ document.getElementById('sizeValue').textContent=e.target.value; if(!isPlaying) generateArray(parseInt(e.target.value)); });
document.getElementById('speed').addEventListener('input', e=>{ document.getElementById('speedValue').textContent=e.target.value; speed=parseInt(e.target.value); });
document.getElementById('algorithm').addEventListener('change', ()=>{ algorithm=document.getElementById('algorithm').value; stepIndex=0; steps=[]; if(algorithm==='quick') buildQuickSteps(); updateCode(); renderBars(); });

document.querySelectorAll('.tab-button').forEach(btn=>{
    btn.addEventListener('click', ()=>{
        document.querySelectorAll('.tab-button').forEach(b=>b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c=>c.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById('tab-'+btn.dataset.tab).classList.add('active');
        updateCode();
    });
});

generateArray(50);
updateCode();
