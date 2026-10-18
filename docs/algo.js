(function(global){
  'use strict';

  function snap(steps, arr, idx, type){
    steps.push({arr: arr.slice(), idx: (idx||[]).slice(), type: type||''});
  }

  function argsortStable(keys){
    const n = keys.length;
    const idx = new Array(n);
    for(let i=0;i<n;i++) idx[i]=i;
    idx.sort(function(i,j){ return keys[i]-keys[j] || i-j; });
    return idx;
  }

  function reorder(a, idx){
    const out = new Array(a.length);
    for(let i=0;i<a.length;i++) out[i]=a[idx[i]];
    return out;
  }

  // ---------- Quick Sort (pivote = a[l]) ----------
  function quickSort(input){
    const steps = [];
    const a = input.slice();
    function q(l, r){
      if(l>=r) return;
      const p = a[l];
      let i=l+1, j=r;
      snap(steps, a, [l], 'pivot');
      while(true){
        while(i<=j && a[i]<=p) i++;
        while(i<=j && a[j]>p) j--;
        if(i>j) break;
        const t=a[i]; a[i]=a[j]; a[j]=t;
        snap(steps, a, [i,j], 'swap');
        i++; j--;
      }
      const t2=a[l]; a[l]=a[j]; a[j]=t2;
      snap(steps, a, [l,j], 'swap');
      q(l, j-1);
      q(j+1, r);
    }
    q(0, a.length-1);
    snap(steps, a, [], 'done');
    return {name:'Quick Sort', steps:steps};
  }

  // ---------- Radix LSD base 256 ----------
  function radixLSD(input){
    const steps = [];
    let a = input.slice();
    const mn = Math.min.apply(null, a);
    let v = a.map(function(x){ return x-mn; });
    for(const shift of [0,8,16,24]){
      const keys = v.map(function(x){ return (x >> shift) & 0xFF; });
      const idx = argsortStable(keys);
      v = reorder(v, idx);
      snap(steps, v.map(function(x){ return x+mn; }), [], 'pass');
    }
    const out = v.map(function(x){ return x+mn; });
    snap(steps, out, [], 'done');
    return {name:'Radix LSD', steps:steps};
  }

  // ---------- Counting sort (rango pequeño) con frames de escritura ----------
  function countingSteps(a, lo, hi, steps){
    const r = hi-lo+1;
    const cnt = new Array(r).fill(0);
    for(let i=0;i<a.length;i++) cnt[a[i]-lo]++;
    const out = a.slice();
    let k=0;
    for(let i=0;i<r;i++){
      for(let c=0;c<cnt[i];c++){ out[k++] = lo+i; }
      snap(steps, out, [k-1], 'write');
    }
    return out;
  }

  // ---------- NovaSort v3 ----------
  function novaSort(input){
    const steps = [];
    const a = input.slice();
    const n = a.length;
    if(n < 2){ snap(steps,a,[],'done'); return {name:'NovaSort v3', steps:steps}; }
    if(n < 48){
      for(let i=1;i<n;i++){
        let vv=a[i], j=i-1;
        while(j>=0 && a[j]>vv){ a[j+1]=a[j]; j--; }
        a[j+1]=vv;
        snap(steps,a,[i],'swap');
      }
      snap(steps,a,[],'done');
      return {name:'NovaSort v3', steps:steps};
    }
    let sorted=true, rev=true;
    for(let i=1;i<n;i++){ if(a[i]<a[i-1]) sorted=false; if(a[i]>a[i-1]) rev=false; }
    if(sorted){ snap(steps,a,[],'done'); return {name:'NovaSort v3', steps:steps}; }
    if(rev){ a.reverse(); snap(steps,a,[],'done'); return {name:'NovaSort v3', steps:steps}; }
    const mn=Math.min.apply(null,a), mx=Math.max.apply(null,a), r=mx-mn+1;
    if(r===1){ snap(steps,a,[],'done'); return {name:'NovaSort v3', steps:steps}; }
    if(r <= Math.max(65536,n)){
      const out = countingSteps(a, mn, mx, steps);
      snap(steps,out,[],'done');
      return {name:'NovaSort v3', steps:steps};
    }
    let v = a.map(function(x){ return x-mn; });
    let idx0 = argsortStable(v.map(function(x){ return x & 0xFFFF; }));
    v = reorder(v, idx0);
    snap(steps, v.map(function(x){ return x+mn; }), [], 'pass');
    const top = Math.max.apply(null, v) >> 16;
    if(top!==0){
      const idx1 = argsortStable(v.map(function(x){ return (x >> 16) & 0xFFFF; }));
      v = reorder(v, idx1);
    }
    const out = v.map(function(x){ return x+mn; });
    snap(steps, out, [], 'done');
    return {name:'NovaSort v3', steps:steps};
  }

  // ---------- NovaSuper v1 ----------
  function novaSuper(input){
    const steps = [];
    const a = input.slice();
    const n = a.length;
    if(n < 2){ snap(steps,a,[],'done'); return {name:'NovaSuper v1', steps:steps}; }
    if(n < 32){
      for(let i=1;i<n;i++){
        let vv=a[i], j=i-1;
        while(j>=0 && a[j]>vv){ a[j+1]=a[j]; j--; }
        a[j+1]=vv;
        snap(steps,a,[i],'swap');
      }
      snap(steps,a,[],'done');
      return {name:'NovaSuper v1', steps:steps};
    }
    let sorted=true, rev=true;
    for(let i=1;i<n;i++){ if(a[i]<a[i-1]) sorted=false; if(a[i]>a[i-1]) rev=false; }
    if(sorted){ snap(steps,a,[],'done'); return {name:'NovaSuper v1', steps:steps}; }
    if(rev){ a.reverse(); snap(steps,a,[],'done'); return {name:'NovaSuper v1', steps:steps}; }
    const mn=Math.min.apply(null,a), mx=Math.max.apply(null,a);
    const r=mx-mn+1;
    if(r===1){ snap(steps,a,[],'done'); return {name:'NovaSuper v1', steps:steps}; }
    if(r <= Math.max(65536,n)){
      const out = countingSteps(a, mn, mx, steps);
      snap(steps, out, [], 'done');
      return {name:'NovaSuper v1', steps:steps};
    }
    let v = a.map(function(x){ return x-mn; });
    const d0 = v.map(function(x){ return x & 0xFFFF; });
    if(Math.min.apply(null,d0)!==Math.max.apply(null,d0)){
      const idx = argsortStable(d0);
      v = reorder(v, idx);
      snap(steps, v.map(function(x){ return x+mn; }), [], 'pass');
    }
    const top = Math.max.apply(null, v) >> 16;
    if(top !== 0){
      const d1 = v.map(function(x){ return (x >> 16) & 0xFFFF; });
      const idx1 = argsortStable(d1);
      v = reorder(v, idx1);
    }
    const out = v.map(function(x){ return x+mn; });
    snap(steps, out, [], 'done');
    return {name:'NovaSuper v1', steps:steps};
  }

  const ALGOS = {
    quick: quickSort,
    radix: radixLSD,
    novasort: novaSort,
    novasuper: novaSuper
  };

  function run(algorithm, input){
    const fn = ALGOS[algorithm] || quickSort;
    return fn(input.slice());
  }

  function sortedCopy(a){ return a.slice().sort(function(x,y){ return x-y; }); }
  function isSorted(a){
    for(let i=1;i<a.length;i++) if(a[i]<a[i-1]) return false;
    return true;
  }

  global.NSAlgo = {run:run, sortedCopy:sortedCopy, isSorted:isSorted, ALGOS:ALGOS};
})(typeof window !== 'undefined' ? window : globalThis);
