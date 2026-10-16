const fs=require('fs'), crypto=require('crypto'), assert=require('assert');
const data=JSON.parse(fs.readFileSync('docs/research/og4-branch3-api-golden.json','utf8'));
function len(n){const b=Buffer.alloc(4);b.writeUInt32BE(n);return b}
function E(v){
 if(typeof v==='number'){assert(Number.isFinite(v)); const b=Buffer.alloc(9);b[0]=100;b.writeDoubleBE(v===0?0:v,1);return b}
 if(typeof v==='string'){assert(/^[\x00-\x7f]*$/.test(v));const b=Buffer.from(v,'ascii');return Buffer.concat([Buffer.from('s'),len(b.length),b])}
 if(Array.isArray(v))return Buffer.concat([Buffer.from('l'),len(v.length),...v.map(E)]);
 assert(v && typeof v==='object');const keys=Object.keys(v).sort();
 return Buffer.concat([Buffer.from('m'),len(keys.length),...keys.flatMap(k=>[E(k),E(v[k])])]);
}
for(const vector of data.vectors){
 const p=structuredClone(vector.input);
 if(vector.kind==='blueprint')for(const [field,key] of [['organs','id'],['junctions','id'],['loads','port']])p[field].sort((a,b)=>a[key]<b[key]?-1:a[key]>b[key]?1:0);
 if(vector.kind==='observation')delete p.observation_digest;
 const raw=Buffer.concat([Buffer.from(`morphoacoustics.og4.${vector.kind}.v1\0`,'ascii'),E(p)]);
 assert.equal(raw.toString('hex'),vector.canonical_hex,vector.name+' bytes');
 assert.equal('sha256:'+crypto.createHash('sha256').update(raw).digest('hex'),vector.digest,vector.name+' hash');
}
console.log(`PASS: JavaScript independently matches all ${data.vectors.length} canonical byte/hash vectors`);
