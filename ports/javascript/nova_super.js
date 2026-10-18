function argsortStable(b){
  let idx = Array.from({length:b.length}, (_,i)=>i);
  idx.sort((i,j)=>{
    if(b[i] < b[j]) return -1;
    if(b[i] > b[j]) return 1;
    return i-j;
  });
  return idx;
}
function novaSuper(a){
  let n = a.length;
  if(n <= 1) return a.slice();
  if(n < 32){
    let arr = a.slice();
    for(let i=1;i<arr.length;i++){
      let v=arr[i], j=i-1;
      while(j>=0 && arr[j]>v){ arr[j+1]=arr[j]; j--; }
      arr[j+1]=v;
    }
    return arr;
  }
  let arr = a.slice();
  let minv=arr[0], maxv=arr[0];
  for(let i=1;i<n;i++){ if(arr[i]<minv) minv=arr[i]; if(arr[i]>maxv) maxv=arr[i]; }
  let r = maxv-minv+1;
  let limitCount = Math.max(65536, n);
  if(r >=1 && r <= limitCount){
    let cnt = new Array(r).fill(0);
    for(let i=0;i<n;i++) cnt[arr[i]-minv]++;
    let k=0, out=new Array(n);
    for(let i=0;i<r;i++){
      let v=minv+i; let c=cnt[i];
      if(c>0){
        for(let j=0;j<c;j++) out[k++]=v;
      }
    }
    return out;
  }
  let v = arr.slice();
  let mskv = 0xFFFF;
  let voff = new Array(n);
  for(let i=0;i<n;i++) voff[i] = v[i]-minv;
  // low
  let d0 = new Array(n);
  for(let i=0;i<n;i++) d0[i] = voff[i] & mskv;
  let order0 = argsortStable(d0);
  let v1 = new Array(n);
  for(let i=0;i<n;i++) v1[i] = voff[order0[i]];
  // high
  let d1 = new Array(n);
  for(let i=0;i<n;i++) d1[i] = (v1[i] >> 16) & mskv;
  let order1 = argsortStable(d1);
  let out = new Array(n);
  for(let i=0;i<n;i++) out[i] = v1[order1[i]] + minv;
  return out;
}
module.exports = {novaSuper};
