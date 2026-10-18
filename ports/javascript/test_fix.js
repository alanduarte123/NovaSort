const {novaSuper}=require('./nova_super');
const fs=require('fs');
const data=JSON.parse(fs.readFileSync('/tmp/cross.json'));
let s=novaSuper(data.a);
for(let i=0;i<s.length;i++){
  if(s[i]!==data.exp[i]){ console.log('bad',i); process.exit(1);}
}
console.log('ok');
