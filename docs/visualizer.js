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
            a[i],a[j]=a[j],a[i]
            i+=1; j-=1
        a[l],a[j]=a[j],a[l]
        _q(l,j-1); _q(j+1,r)
    _q(0,len(a)-1)`,
    radix: `# Radix LSD`,
    novasort: `# NovaSort v3`,
    novasuper: `# NovaSuper v1`
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
    radix: `// Radix`, novasort: `// NovaSort`, novasuper: `// NovaSuper`
  },
  c:{quick:`// quick`,radix:`//`,novasort:`//`,novasuper:`//`},
  java:{quick:`//`,radix:`//`,novasort:`//`,novasuper:`//`},
  php:{quick:`//`,radix:`//`,novasort:`//`,novasuper:`//`}
};
const PSEUDOCODE={
  quick:`1. Pivote arr[l]\n2. Particionar i,j\n3. Intercambiar cuando a[i]>p y a[j]<p\n4. Colocar pivote en j\n5. Recursivo`,
  radix:`1. LSD bytes`,novasort:`1. Híbrido`,novasuper:`1. Counting o Radix 16-bit`
};

let array=[],algorithm='quick',speed=15,isPlaying=false,intervalId=null,comparisons=0,swaps=0,steps=[],stepIndex=0,orig=[];
function clone(a){return a.slice();}
function generateArray(size){
  array=[]; orig=[];
  for(let i=0;i<size;i++){ let v=Math.floor(Math.random()*100)+1; array.push(v); orig.push(v);}
  comparisons=0; swaps=0; stepIndex=0; steps=[];
  updateStats(); renderBars(array); buildSteps(); setStatus('Listo');
}
function buildSteps(){
  steps=[]; let a=clone(array);
  if(algorithm==='quick'){
    function qs(l,r){
      if(l>=r)return;
      let p=a[l], i=l+1, j=r;
      steps.push({type:'pivot', array:clone(a), idx:[l]});
      while(true){
        while(i<=j && a[i]<=p){ comparisons++; steps.push({type:'compare', array:clone(a), idx:[i,l]}); i++; }
        while(i<=j && a[j]>p){ comparisons++; steps.push({type:'compare', array:clone(a), idx:[j,l]}); j--; }
        if(i>j) break;
        let t=a[i]; a[i]=a[j]; a[j]=t; swaps++;
        steps.push({type:'swap', array:clone(a), idx:[i,j]});
        i++; j++;
      }
      let t2=a[l]; a[l]=a[j]; a[j]=t2; swaps++;
      steps.push({type:'swap', array:clone(a), idx:[l,j], placed:true});
      qs(l,j-1); qs(j+1,r);
    }
    qs(0,a.length-1);
  }
  steps.push({type:'done', array:clone(a)});
}
function renderBars(data){
  const c=document.getElementById('bars'); c.innerHTML='';
  let d=data||array; if(d.length===0)return; let m=Math.max(...d);
  d.forEach(v=>{
    let b=document.createElement('div'); b.className='bar'; b.style.height=(v/m*100)+'%'; c.appendChild(b);
  });
}
function applyState(s){
  array = s.array; renderBars(array);
  let bars=document.querySelectorAll('.bar');
  bars.forEach(x=>x.classList.remove('comparing','swapping','pivot','sorted'));
  if(s.type==='pivot'&&s.idx) bars[s.idx[0]]?.classList.add('pivot');
  if(s.type==='compare'&&s.idx) s.idx.forEach(i=>{if(bars[i]) bars[i].classList.add('comparing');});
  if(s.type==='swap'&&s.idx) s.idx.forEach(i=>{if(bars[i]) bars[i].classList.add('swapping');});
  if(s.type==='done') bars.forEach(x=>x.classList.add('sorted'));
  comparisons = s.comparisons!=null?s.comparisons:comparisons;
  swaps = s.swaps!=null?s.swaps:swaps;
  updateStats();
}
function updateStats(){document.getElementById('comparisons').textContent=comparisons; document.getElementById('swaps').textContent=swaps;}
function setStatus(m){document.getElementById('status').textContent=m;}
function updateCode(){
  let lang=document.querySelector('.tab-button.active')?.dataset.tab||'python';
  let algo=document.getElementById('algorithm').value;
  ['python','javascript','c','java','php'].forEach(l=>{
    let el=document.getElementById('code-'+l); if(el) el.textContent=(CODE_SOURCES[l]&&CODE_SOURCES[l][algo])||'';
  });
  let p=document.getElementById('pseudocode'); if(p) p.textContent=PSEUDOCODE[algo]||'';
}
function nextStep(){
  if(stepIndex < steps.length){
    let s=steps[stepIndex++]; applyState(s);
    return true;
  }
  return false;
}
function togglePlay(){
  if(isPlaying) return;
  if(steps.length===0) buildSteps();
  isPlaying=true; document.getElementById('play').disabled=true; document.getElementById('pause').disabled=false; document.getElementById('step').disabled=true;
  intervalId=setInterval(()=>{
    if(!nextStep()){ clearInterval(intervalId); isPlaying=false; document.getElementById('play').disabled=false; document.getElementById('pause').disabled=true; document.getElementById('step').disabled=false; setStatus('Finalizado'); }
  }, 1000/speed);
}
function pause(){ isPlaying=false; clearInterval(intervalId); document.getElementById('play').disabled=false; document.getElementById('pause').disabled=true; document.getElementById('step').disabled=false; setStatus('Pausado'); }
function step(){ if(!isPlaying){ if(steps.length===0) buildSteps(); nextStep(); } }
function reset(){ pause(); generateArray(parseInt(document.getElementById('arraySize').value)); }

document.getElementById('generate').onclick=()=>generateArray(parseInt(document.getElementById('arraySize').value));
document.getElementById('play').onclick=togglePlay;
document.getElementById('pause').onclick=pause;
document.getElementById('step').onclick=step;
document.getElementById('reset').onclick=reset;
document.getElementById('arraySize').oninput=e=>{document.getElementById('sizeValue').textContent=e.target.value; if(!isPlaying) generateArray(parseInt(e.target.value));};
document.getElementById('speed').oninput=e=>{document.getElementById('speedValue').textContent=e.target.value; speed=parseInt(e.target.value); if(isPlaying){clearInterval(intervalId); intervalId=setInterval(()=>{if(!nextStep()){pause();setStatus('Finalizado');}},1000/speed);} };
document.getElementById('algorithm').onchange=()=>{algorithm=document.getElementById('algorithm').value; stepIndex=0; steps=[]; buildSteps(); renderBars(array); updateCode();};

document.querySelectorAll('.tab-button').forEach(b=>b.onclick=()=>{document.querySelectorAll('.tab-button').forEach(x=>x.classList.remove('active'));document.querySelectorAll('.tab-content').forEach(x=>x.classList.remove('active'));b.classList.add('active');document.getElementById('tab-'+b.dataset.tab).classList.add('active');updateCode();});

generateArray(50); updateCode();
