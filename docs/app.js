const CODE_SOURCES = {
  python:{quick:"def quick_sort(a):\n    def _q(l,r):\n        if l>=r: return\n        p=a[l]; i=l+1; j=r\n        while True:\n            while i<=j and a[i]<=p: i+=1\n            while i<=j and a[j]>p: j-=1\n            if i>j: break\n            a[i],a[j]=a[j],a[i]; i+=1;j-=1\n        a[l],a[j]=a[j],a[l]\n        _q(l,j-1); _q(j+1,r)\n    _q(0,len(a)-1)"},
  javascript:{quick:"function quickSort(arr,l,r){\n  if(l>=r)return; let p=arr[l],i=l+1,j=r;\n  while(true){\n    while(i<=j&&arr[i]<=p)i++;\n    while(i<=j&&arr[j]>p)j--;\n    if(i>j)break;\n    [arr[i],arr[j]]=[arr[j],arr[i]]; i++; j--;\n  }\n  [arr[l],arr[j]]=[arr[j],arr[l]];\n  quickSort(arr,l,j-1); quickSort(arr,j+1,r);\n}"},
  c:{},java:{},php:{}
};
const PSEUDOCODE={quick:"1.Pivote 2.Particionar 3.Swap 4.Colocar pivote 5.Recursivo"};
let array=[],algorithm='quick',speed=30,isPlaying=false,intervalId=null,comparisons=0,swaps=0,steps=[],stepIndex=0;
function clone(a){return a.slice();}
function gen(n){
  array=[]; for(let i=0;i<n;i++) array.push(Math.floor(Math.random()*90)+10);
  comparisons=0; swaps=0; stepIndex=0; steps=[]; update(); build(); render();
}
function build(){
  steps=[]; let a=clone(array);
  if(algorithm==='quick'){
    function qs(l,r){
      if(l>=r)return;
      let p=a[l],i=l+1,j=r;
      steps.push({t:'p',idx:[l],arr:clone(a)});
      while(true){
        while(i<=j&&a[i]<=p)i++;
        while(i<=j&&a[j]>p)j--;
        if(i>j)break;
        let tmp=a[i]; a[i]=a[j]; a[j]=tmp;
        steps.push({t:'s',idx:[i,j],arr:clone(a)});
        i++; j--;
      }
      let t2=a[l]; a[l]=a[j]; a[j]=t2;
      steps.push({t:'s',idx:[l,j],arr:clone(a)});
      qs(l,j-1); qs(j+1,r);
    }
    qs(0,a.length-1);
  }
  steps.push({t:'d',arr:clone(a)});
}
function render(){
  let c=document.getElementById('bars'); c.innerHTML='';
  let m=Math.max(...array); array.forEach(v=>{
    let b=document.createElement('div'); b.className='bar'; b.style.height=(v/m*100)+'%'; c.appendChild(b);
  });
}
function apply(s){
  array=s.arr; render();
  let bars=document.querySelectorAll('.bar');
  bars.forEach(x=>x.classList.remove('comparing','swapping','pivot','sorted'));
  if(s.t==='p') bars[s.idx[0]]?.classList.add('pivot');
  if(s.t==='s') s.idx.forEach(i=>bars[i]?.classList.add('swapping'));
  if(s.t==='d') bars.forEach(x=>x.classList.add('sorted'));
  update();
}
function update(){
  document.getElementById('comparisons').textContent=comparisons;
  document.getElementById('swaps').textContent=swaps;
  document.getElementById('status').textContent=isPlaying?'Ejecutando':(steps.length&&stepIndex>=steps.length?'Finalizado':'Listo');
}
function next(){
  if(stepIndex>=steps.length) return false;
  let s=steps[stepIndex++]; if(s.t==='s') swaps++; apply(s); update(); return true;
}
function play(){
  if(isPlaying)return; isPlaying=true;
  document.getElementById('play').disabled=true; document.getElementById('pause').disabled=false; document.getElementById('step').disabled=true;
  intervalId=setInterval(()=>{ if(!next()){ clearInterval(intervalId); isPlaying=false; document.getElementById('play').disabled=false; document.getElementById('pause').disabled=true; document.getElementById('step').disabled=false; update();}}, 1000/speed);
}
function pause(){
  if(!isPlaying)return; isPlaying=false;
  clearInterval(intervalId);
  document.getElementById('play').disabled=false; document.getElementById('pause').disabled=true; document.getElementById('step').disabled=false; update();
}
document.getElementById('generate').onclick=()=>{gen(parseInt(document.getElementById('arraySize').value));};
document.getElementById('play').onclick=play;
document.getElementById('pause').onclick=pause;
document.getElementById('step').onclick=()=>{if(!isPlaying) next();};
document.getElementById('reset').onclick=()=>{pause(); gen(parseInt(document.getElementById('arraySize').value));};
document.getElementById('arraySize').oninput=e=>{document.getElementById('sizeValue').textContent=e.target.value; if(!isPlaying) gen(parseInt(e.target.value));};
document.getElementById('speed').oninput=e=>{document.getElementById('speedValue').textContent=e.target.value; speed=parseInt(e.target.value); if(isPlaying){clearInterval(intervalId); intervalId=setInterval(()=>{if(!next()){pause();}},1000/speed);}};
document.getElementById('algorithm').onchange=()=>{algorithm=document.getElementById('algorithm').value; stepIndex=0; steps=[]; build(); render(); update();};
document.querySelectorAll('.tab-button').forEach(b=>b.onclick=()=>{
  document.querySelectorAll('.tab-button').forEach(x=>x.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(x=>x.classList.remove('active'));
  b.classList.add('active');
  document.getElementById('tab-'+b.dataset.tab).classList.add('active');
});
gen(20);
