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
    radix:`//`,novasort:`//`,novasuper:`//`
  },
  c:{quick:`//`,radix:`//`,novasort:`//`,novasuper:`//`},
  java:{quick:`//`,radix:`//`,novasort:`//`,novasuper:`//`},
  php:{quick:`//`,radix:`//`,novasort:`//`,novasuper:`//`}
};
const PSEUDOCODE={
  quick:`1. Pivote arr[l]\n2. Particionar\n3. Intercambiar\n4. Reubicar pivote\n5. Recursivo`,
  radix:`LSD`,novasort:`Híbrido`,novasuper:`Counting/Radix 16-bit`
};

let array=[],algorithm='quick',speed=20,isPlaying=false,intervalId=null,comparisons=0,swaps=0,steps=[],stepIndex=0;
function clone(a){return a.slice();}
function generateArray(size){
  array=[];
  for(let i=0;i<size;i++) array.push(Math.floor(Math.random()*100)+1);
  comparisons=0; swaps=0; stepIndex=0; steps=[];
  updateStats(); renderBars(array); buildSteps(); setStatus('Listo');
}
function buildSteps(){
  steps=[]; let a=clone(array);
  if(algorithm==='quick'){
    function qs(l,r){
      if(l>=r) return;
      let p=a[l], i=l+1, j=r;
      steps.push({type:'pivot', array:clone(a), idx:[l]});
      while(true){
        while(i<=j && a[i]<=p){ i++; }
        while(i<=j && a[j]>p){ j--; }
        if(i>j) break;
        let t=a[i]; a[i]=a[j]; a[j]=t;
        steps.push({type:'swap', array:clone(a), idx:[i,j]});
        i++; j--;
      }
      let t2=a[l]; a[l]=a[j]; a[j]=t2;
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
  array=s.array; renderBars(array);
  let bars=document.querySelectorAll('.bar');
  bars.forEach(x=>x.classList.remove('comparing','swapping','pivot','sorted'));
  if(s.type==='pivot'&&s.idx) bars[s.idx[0]]?.classList.add('pivot');
  if(s.type==='swap'&&s.idx) s.idx.forEach(i=>{if(bars[i]) bars[i].classList.add('swapping');});
  if(s.type==='done') bars.forEach(x=>x.classList.add('sorted'));
  updateStats();
}
function updateStats(){document.getElementById('comparisons').textContent=comparisons; document.getElementById('swaps').textContent=swaps;}
function setStatus(m){document.getElementById('status').textContent=m;}
function updateCode(){
  let lang=(document.querySelector('.tab-button.active')||{dataset:{tab:'python'}}).dataset.tab;
  let algo=document.getElementById('algorithm').value;
  ['python','javascript','c','java','php'].forEach(l=>{
    let el=document.getElementById('code-'+l); if(el) el.textContent=(CODE_SOURCES[l]&&CODE_SOURCES[l][algo])||'';
  });
  document.getElementById('pseudocode').textContent=PSEUDOCODE[algo]||'';
}
function nextStep(){
  if(stepIndex < steps.length){
    let s=steps[stepIndex++];
    if(s.type==='swap') swaps++;
    applyState(s);
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

generateArray(30); updateCode();
