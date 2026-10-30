// No dependencies, no external network, mock DOM in Node to run actual inline UI script.
// These are software smoke / privacy / fail-closed tests, NOT linguistic correctness.
"use strict";
const fs=require("node:fs");
const path=require("node:path");
const vm=require("node:vm");
const assert=require("node:assert/strict");

async function main(){
 const root=__dirname;
 const html=fs.readFileSync(path.join(root,"index.html"),"utf8");
 const match=html.match(/<script>([\s\S]*?)<\/script>/);
 assert(match,"standalone inline script required");
 const js=match[1];
 const nodes=new Map(), messages=[];
 function elt(){
  return {
   value:"",textContent:"",className:"",disabled:false,children:[],style:{},
   classList:{toggle(){}},
   replaceChildren(){this.children=[];},
   appendChild(child){this.children.push(child);},
   addEventListener(){},remove(){},click(){},
  };
 }
 const storage=new Map(), windowHooks={};
 let failStorage=false, lastExport;
 const doc={
  getElementById(id){if(!nodes.has(id))nodes.set(id,elt());return nodes.get(id);},
  createElement(){return elt();},
  body:{appendChild(){}},
 };
 const ctx={
  document:doc,
  window:{addEventListener:(name,fn)=>{windowHooks[name]=fn;}},
  localStorage:{
   getItem:k=>storage.get(k)||null,
   setItem:(k,v)=>{if(failStorage)throw Error("quota exceeded");storage.set(k,v);},
  },
  URL:{createObjectURL:blob=>{lastExport=blob;return "blob:local";},revokeObjectURL(){}},
  Blob,Date,Math,console,alert:s=>messages.push(s),confirm:()=>true,setTimeout:()=>{},
 };
 vm.createContext(ctx);
 vm.runInContext(js,ctx,{filename:"index.html:inline-script"});
 const evaluate=(s)=>vm.runInContext(s,ctx);
 const example=JSON.parse(fs.readFileSync(path.join(root,"sample_cases.json"),"utf8"));
 ctx.testFile={size:Buffer.byteLength(JSON.stringify(example)),text:async()=>JSON.stringify(example)};
 await evaluate("importJson(testFile)");
 assert.equal(evaluate("data.cases.length"),3);

 // Two Codex P2 fixtures must be refused, without poisoning current state.
 const malformed=structuredClone(example);
 malformed.cases[0].annotation.status="MULTI";
 malformed.cases[0].annotation.paths=["ニンキ","ニンキ"];
 ctx.testFile={size:Buffer.byteLength(JSON.stringify(malformed)),text:async()=>JSON.stringify(malformed)};
 await evaluate("importJson(testFile)");
 assert(messages.some(s=>s.includes("読めません")),"duplicate MULTI was accepted");
 assert.equal(evaluate("data.cases[0].annotation.status"),"UNANNOTATED");
 malformed.cases[0].annotation.status="UNKNOWN";
 malformed.cases[0].annotation.paths=["ニンキ"];
 ctx.testFile={size:Buffer.byteLength(JSON.stringify(malformed)),text:async()=>JSON.stringify(malformed)};
 await evaluate("importJson(testFile)");
 assert(messages.filter(s=>s.includes("読めません")).length>=2,"false UNKNOWN gold was accepted");
 malformed.cases[0].annotation.status="SINGLE";
 malformed.cases[0].annotation.paths=[];
 ctx.testFile={size:Buffer.byteLength(JSON.stringify(malformed)),text:async()=>JSON.stringify(malformed)};
 await evaluate("importJson(testFile)");
 assert(messages.filter(s=>s.includes("読めません")).length>=3,"empty SINGLE accepted");

 // Actual annotate/save; fail-to-persist must remain clearly visible.
 doc.getElementById("status").value="SINGLE";
 doc.getElementById("paths").value="ヒトケノナイトオリヲアルイタ";
 evaluate("saveCase()");
 assert.equal(evaluate("data.cases[0].annotation.status"),"SINGLE");
 assert(storage.get("smc7-solo-workbench-v1"),"normal local autosave failed");
 assert.equal(typeof windowHooks.beforeunload,"function");
 doc.getElementById("notes").value="まだ保存していない入力";
 const leaveEdit={preventDefault(){this.prevented=true;},returnValue:null};
 windowHooks.beforeunload(leaveEdit);
 assert(leaveEdit.prevented,"missing unload guard for unsaved form");
 doc.getElementById("notes").value=example.cases[0].annotation.notes;
 // After a completed save there must be no spurious unload prompt.
 const leaveClean={preventDefault(){this.prevented=true;},returnValue:null};
 windowHooks.beforeunload(leaveClean);
 assert(!leaveClean.prevented,"clean form is incorrectly blocked");
 failStorage=true;
 doc.getElementById("notes").value="追加メモ";
 evaluate("saveCase()");
 assert(doc.getElementById("storageWarn").textContent.includes("保存失敗"),"quota warning erased");
 assert(doc.getElementById("message").textContent.includes("保存失敗"),"false save success");
 const leaveFailed={preventDefault(){this.prevented=true;},returnValue:null};
 windowHooks.beforeunload(leaveFailed);
 assert(leaveFailed.prevented,"failed browser store lost unload warning");
 evaluate("exportJson()");
 assert(lastExport,"explicit export should work even when browser storage fails");
 const exported=JSON.parse(await lastExport.text());
 assert.equal(exported.cases[0].annotation.notes,"追加メモ");

 // An export >2MiB but <16MiB must be restorable.
 failStorage=false;
 const jumbo={schema:"SMC7_SOLO_WORKBENCH_V1",evidence_tier:"SOLO_DEVELOPMENT_ONLY",cases:[]};
 for(let i=0;i<150;i++){
  const c=structuredClone(example.cases[2]);
  c.id="large-"+String(i);
  c.annotation.status="MULTI";
  c.annotation.paths=Array.from({length:8},(_,k)=>"ア".repeat(511)+String.fromCharCode(0x30A2+k));
  c.annotation.notes="長".repeat(4000);
  jumbo.cases.push(c);
 }
 const json=JSON.stringify(jumbo);
 const size=Buffer.byteLength(json);
 assert(size>2*1024*1024&&size<16*1024*1024,"test needs a >2MiB valid export");
 ctx.testFile={size,text:async()=>json};
 await evaluate("importJson(testFile)");
 assert.equal(evaluate("data.cases.length"),150,"large valid workspace failed import");
 evaluate("exportJson()");
 const recovered=JSON.parse(await lastExport.text());
 assert.equal(recovered.cases.length,150,"large valid export failed");
 console.log("SOLO_OFFLINE_SMOKE_PASSED: import, strict multi/unknown, save failure, JSON backup, >2MiB roundtrip");
}
main().catch(e=>{console.error(e);process.exitCode=1;});
