const {novaSuper}=require('./nova_super');
let n=5000;
let a=[];
const seed=2026;
let x=seed%2147483647; if(x<=0)x+=2147483646;
function next(){ x=(x*48271)%2147483647; return (x-1)/(2147483647-1); }
for(let i=0;i<n;i++) a.push(Math.floor(next()*10000000));
let s2=novaSuper(a);
let exp=a.slice().sort((x,y)=>x-y);
for(let i=0;i<n;i++){ if(s2[i]!==exp[i]){ console.log('bad',i,s2[i],exp[i]); process.exit(1);} }
console.log('ok');
