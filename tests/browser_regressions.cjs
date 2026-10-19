// Real-browser fixtures for the publication checkers, isolated from public content.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const os=require('node:os');
const path=require('node:path');
const {spawnSync}=require('node:child_process');
const {chromium}=require('playwright');
const {archiveComplete}=require('../scripts/browser_assertions.cjs');
const {inspectContrast,writeReport}=require('../scripts/contrast_check.cjs');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'chrome'});
 try{
  if(process.argv.includes('--bad-contrast')){
   const page=await browser.newPage();
   await page.setContent('<body style="background:white"><p style="color:#eee">Deliberately unreadable fixture</p></body>');
   const bad=await inspectContrast(page);
   assert(bad.length>0,'fixture must exercise contrast detection');
   writeReport([{slug:'negative-fixture',theme:'light',bad}]);
   return;
  }
  const context=await browser.newContext({javaScriptEnabled:false});
  const page=await context.newPage();
  const catalog=JSON.parse(fs.readFileSync('content/catalog.json'));
  const expanded={...catalog,readers:[...catalog.readers,{slug:'fourteenth-reader-fixture'}]};
  assert.equal(expanded.readers.length,14);
  await page.setContent(expanded.readers.map(r=>`<article class="gm-card">${r.slug}</article>`).join(''));
  assert.equal(await archiveComplete(page,expanded),true,'14-card no-JS archive must pass for 14 Readers');
  assert.equal(await archiveComplete(page,catalog),false,'extra card must fail');
  await page.setContent(catalog.readers.map(r=>`<article class="gm-card">${r.slug}</article>`).join(''));
  assert.equal(await archiveComplete(page,expanded),false,'missing fourteenth card must fail');
  await page.setContent('<body style="background:white"><p style="color:black">Readable fixture</p></body>');
  assert.deepEqual(await inspectContrast(page),[]);
  await context.close();
 }finally{await browser.close();}
 if(!process.argv.includes('--bad-contrast')){
  const output=fs.mkdtempSync(path.join(os.tmpdir(),'gm-contrast-negative-'));
  try{
   const result=spawnSync(process.execPath,[__filename,'--bad-contrast'],{env:{...process.env,GM_TEST_OUTPUT:output},encoding:'utf8'});
   assert.equal(result.status,1,result.stderr||result.stdout);
   const report=JSON.parse(fs.readFileSync(path.join(output,'contrast.json')));
   assert(report[0].bad.some(v=>v.text==='Deliberately unreadable fixture'));
   console.log('PASS: contrast violation exits 1 with evidence; readable text passes; 14-card no-JS archive and count mismatches checked');
  }finally{fs.rmSync(output,{recursive:true,force:true});}
 }
})().catch(error=>{console.error(error);process.exitCode=1;});
