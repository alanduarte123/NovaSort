'use strict';

const CODE_SOURCES = {
  python: {
    quick: `def quick_sort(a):
    def _q(l,r):
        if l>=r: return
        p=a[l]; i=l+1; j=r
        while True:
            while i<=j and a[i]<=p: i+=1
            while i<=j and a[j]>p: j-=1
            if i>j: break
            a[i],a[j]=a[j],a[i]; i+=1;j-=1
        a[l],a[j]=a[j],a[l]
        _q(l,j-1); _q(j+1,r)
    _q(0,len(a)-1)`,
    radix: `def radix_lsd(a):
    for shift in (0,8,16,24):
        a[:] = sorted(a, key=lambda x:(x>>shift)&0xFF)`,
    novasort: `def nova_v3(a):  # NovaSort v3
    # insercion (n<48) -> orden/invertido -> counting -> radix 16-bit
    ...`,
    novasuper: `def nova_super_v1(a):
    # early-exits -> counting si rango pequeno -> radix 16-bit estable
    ...`
  },
  javascript: {
    quick: `function quickSort(arr,l,r){
  if(l>=r)return; let p=arr[l],i=l+1,j=r;
  while(true){
    while(i<=j&&arr[i]<=p)i++;
    while(i<=j&&arr[j]>p)j--;
    if(i>j)break;
    [arr[i],arr[j]]=[arr[j],arr[i]]; i++; j--;
  }
  [arr[l],arr[j]]=[arr[j],arr[l]];
  quickSort(arr,l,j-1); quickSort(arr,j+1,r);
}`,
    radix: `function radixLSD(a){
  let v=a.map(x=>x-min);
  for(const sh of [0,8,16,24]){
    v = stableSortBy(v, x=>(x>>sh)&0xFF);
  }
  return v.map(x=>x+min);
}`,
    novasort: `// NovaSort v3 (ver docs/algo.js -> novaSort)`,
    novasuper: `// NovaSuper v1 (ver docs/algo.js -> novaSuper)`
  },
  c: { quick: '// ver ports/c', radix: '// ver ports/c', novasort: '// NovaSort v3', novasuper: '// ver ports/c/nova_super.c' },
  java: { quick: '// Quick Sort', radix: '// Radix LSD', novasort: '// NovaSort v3', novasuper: '// ver ports/java/NovaSuper.java' },
  php: { quick: '// Quick Sort', radix: '// Radix LSD', novasort: '// NovaSort v3', novasuper: '// ver ports/php/nova_super.php' }
};

const PSEUDOCODE = {
  quick: "1. Pivote = a[l]\n2. Particionar (i,j)\n3. Intercambiar si a[i]>p y a[j]<p\n4. Colocar pivote en j\n5. Recursivo a ambos lados",
  radix: "1. Offset a no-negativo\n2. Para cada byte (0,8,16,24): orden estable por ese byte\n3. Sumar offset",
  novasort: "1. n<48 -> insercion\n2. Si ordenado/invertido -> salir\n3. Rango <= max(65536,n) -> counting\n4. Sino -> radix 16-bit (bajo luego alto)",
  novasuper: "1. n<32 -> insercion\n2. Early-exit ordenado/invertido\n3. Rango pequeno -> counting\n4. Sino -> radix 16-bit con argsort estable"
};

let array = [];
let algorithm = 'quick';
let speed = 30;
let isPlaying = false;
let intervalId = null;
let comparisons = 0;
let swaps = 0;
let steps = [];
let stepIndex = 0;

const $ = function(id){ return document.getElementById(id); };

function generateArray(size){
  size = Math.max(5, Math.min(size, 40));
  array = [];
  for(let i=0;i<size;i++) array.push(Math.floor(Math.random()*90)+10);
  comparisons = 0; swaps = 0; stepIndex = 0; steps = [];
  buildSteps();
  renderBars(array);
  updateStats();
  setStatus('Listo');
}

function buildSteps(){
  steps = NSAlgo.run(algorithm, array).steps;
  stepIndex = 0;
}

function renderBars(data){
  const c = $('bars');
  c.innerHTML = '';
  if(!data.length) return;
  const m = Math.max.apply(null, data);
  for(let i=0;i<data.length;i++){
    const b = document.createElement('div');
    b.className = 'bar';
    b.style.height = (data[i]/m*100) + '%';
    c.appendChild(b);
  }
}

function applyState(s){
  array = s.arr.slice();
  renderBars(array);
  const bars = document.querySelectorAll('.bar');
  for(let i=0;i<bars.length;i++){
    bars[i].classList.remove('comparing','swapping','pivot','sorted','write');
  }
  if(s.type==='pivot'){ if(bars[s.idx[0]]) bars[s.idx[0]].classList.add('pivot'); }
  if(s.type==='swap'){ s.idx.forEach(function(i){ if(bars[i]) bars[i].classList.add('swapping'); }); }
  if(s.type==='write'||s.type==='pass'){ s.idx.forEach(function(i){ if(bars[i]) bars[i].classList.add('write'); }); }
  if(s.type==='done'){ for(let i=0;i<bars.length;i++) bars[i].classList.add('sorted'); }
  if(s.type==='swap') swaps++;
  updateStats();
}

function updateStats(){
  $('comparisons').textContent = comparisons;
  $('swaps').textContent = swaps;
}

function setStatus(msg){ $('status').textContent = msg; }

function updateCode(){
  const algo = algorithm;
  ['python','javascript','c','java','php'].forEach(function(l){
    const el = $('code-'+l);
    if(el) el.textContent = (CODE_SOURCES[l] && CODE_SOURCES[l][algo]) || '';
  });
  $('pseudocode').textContent = PSEUDOCODE[algo] || '';
}

function nextStep(){
  if(stepIndex >= steps.length) return false;
  const s = steps[stepIndex++];
  applyState(s);
  return true;
}

function finish(){
  clearInterval(intervalId);
  isPlaying = false;
  $('play').disabled = false;
  $('pause').disabled = true;
  $('step').disabled = false;
  const expected = NSAlgo.sortedCopy(array);
  const ok = JSON.stringify(array) === JSON.stringify(expected);
  setStatus(ok ? 'Ordenado ✔' : 'ERROR: resultado incorrecto');
}

function play(){
  if(isPlaying) return;
  if(stepIndex >= steps.length){ stepIndex = 0; buildSteps(); }
  isPlaying = true;
  $('play').disabled = true;
  $('pause').disabled = false;
  $('step').disabled = true;
  setStatus('Ejecutando...');
  intervalId = setInterval(function(){
    if(!nextStep()) finish();
  }, Math.max(10, 1000/speed));
}

function pause(){
  if(!isPlaying) return;
  isPlaying = false;
  clearInterval(intervalId);
  $('play').disabled = false;
  $('pause').disabled = true;
  $('step').disabled = false;
  setStatus('Pausado');
}

function stepOnce(){
  if(isPlaying) return;
  if(stepIndex >= steps.length) return;
  nextStep();
  if(stepIndex >= steps.length) finish();
}

function reset(){
  pause();
  generateArray(parseInt($('arraySize').value, 10));
}

$('generate').onclick = function(){ pause(); generateArray(parseInt($('arraySize').value,10)); };
$('play').onclick = play;
$('pause').onclick = pause;
$('step').onclick = stepOnce;
$('reset').onclick = reset;

$('arraySize').oninput = function(e){
  const v = Math.max(5, Math.min(parseInt(e.target.value,10), 40));
  $('sizeValue').textContent = v;
  if(!isPlaying) generateArray(v);
};
$('speed').oninput = function(e){
  speed = parseInt(e.target.value,10);
  $('speedValue').textContent = speed;
  if(isPlaying){
    clearInterval(intervalId);
    intervalId = setInterval(function(){ if(!nextStep()) finish(); }, Math.max(10, 1000/speed));
  }
};
$('algorithm').onchange = function(e){
  pause();
  algorithm = e.target.value;
  stepIndex = 0;
  buildSteps();
  renderBars(array);
  updateStats();
  setStatus('Listo');
  updateCode();
};

document.querySelectorAll('.tab-button').forEach(function(b){
  b.onclick = function(){
    document.querySelectorAll('.tab-button').forEach(function(x){ x.classList.remove('active'); });
    document.querySelectorAll('.tab-content').forEach(function(x){ x.classList.remove('active'); });
    b.classList.add('active');
    $('tab-'+b.dataset.tab).classList.add('active');
  };
});

generateArray(20);
updateCode();
