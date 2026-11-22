// Optional development verification. Requires Playwright and installed Chrome, not used by hosting.
const output=process.env.GM_TEST_OUTPUT || '/tmp/ghostmesh-reader-checks';
const siteOrigin=(process.env.GM_SITE_ORIGIN || 'http://127.0.0.1:8765').replace(/\/$/,'');
require('fs').mkdirSync(output+'/screenshots',{recursive:true});
const { chromium } = require('playwright');
const fs=require('fs');
const {archiveComplete,currentReaderShell,readerShellProblems}=require('./browser_assertions.cjs');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:"chrome"});
 const cat=JSON.parse(fs.readFileSync('content/catalog.json'));
 const arg=process.argv.indexOf('--reader');
 const latest=process.argv.includes('--latest');
 if(arg!==-1 && latest)throw Error('Choose --reader SLUG or --latest, not both');
 const selected=latest ? [...cat.readers].sort((a,b)=>b.editorialOrder-a.editorialOrder)[0]?.slug
     : arg===-1?null:process.argv[arg+1];
 if((arg!==-1 && !selected) || (selected && !cat.readers.some(r=>r.slug===selected)))throw Error('Unknown Reader target');
 const paths=selected?[selected]:['','readers',...cat.readers.map(r=>r.slug)];
 const results=[];const failures=[];
 for(const width of [390,1440])for(const theme of ['light','dark']){
  const context=await browser.newContext({viewport:{width,height:1000},colorScheme:theme,reducedMotion:'reduce'});
  await context.addInitScript(()=>localStorage.setItem('gm-appearance','system'));
  await context.route('**/*',route=>route.request().url().startsWith(siteOrigin)?route.continue():route.abort());
  const page=await context.newPage();page.on('pageerror',e=>failures.push(e.message));
  for(const path of paths){
   await page.goto(siteOrigin+'/'+path+'/');
   const result=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth,theme:document.documentElement.dataset.theme,brief:!!document.getElementById('at-a-glance'),h1:document.querySelectorAll('h1').length,preload:[...document.querySelectorAll('iframe')].some(f=>f.src&&!f.src.startsWith('about:'))}));
   if(result.scroll>width+1||result.theme!==theme||result.preload)failures.push({path,width,theme,...result});
   if(selected){
    const before=await currentReaderShell(page);
    const issues=readerShellProblems(before,width);
    if(issues.length)failures.push({path,width,theme,stage:'initial',issues,metrics:before});
    const toggle=page.locator('[data-theme-toggle]');
    if(await toggle.count()===1){
     await toggle.click();
     const after=await currentReaderShell(page);
     const nextProblems=readerShellProblems(after,width);
     if(after.theme===before.theme)nextProblems.push('appearance click did not change theme');
     if(nextProblems.length)failures.push({path,width,theme,stage:'after-toggle',issues:nextProblems,metrics:after});
    }else failures.push({path,width,theme,issues:['appearance toggle missing']});
   }
   results.push({path,width,theme,...result});
   await page.screenshot({path:`${output}/screenshots/${path||'home'}-${width}-${theme}.png`,fullPage:false});
  }
  await context.close();
 }
 if(selected){
  await browser.close();
  fs.writeFileSync(output+'/browser-evidence.json',JSON.stringify({target:selected,cases:results.length,results,failures},null,2));
  console.log(JSON.stringify({target:selected,cases:results.length,failures},null,2));
  if(failures.length)process.exitCode=1;
  return;
 }
 const context=await browser.newContext({viewport:{width:390,height:844}});await context.route('**/*',r=>r.request().url().startsWith(siteOrigin)?r.continue():r.abort());const page=await context.newPage();
 await page.goto(siteOrigin+'/');if(await page.locator('html').getAttribute('data-theme')!=='dark')failures.push('canonical dark default');
 await page.goto(siteOrigin+'/readers/');await page.locator('#search').fill('Strix');if(await page.locator('.gm-card:visible').count()!==1)failures.push('search Strix');
 await page.locator('button[type=reset]').click();await page.locator('#category').selectOption('Business');if(await page.locator('.gm-card:visible').count()!==2)failures.push('category Business');
 await page.locator('#tag').selectOption('security');if(await page.locator('.gm-card:visible').count()!==0)failures.push('combined filters');
 await page.locator('[data-theme-toggle]').click();await page.reload();if(await page.locator('html').getAttribute('data-theme')!=='light')failures.push('theme persistence');
 await page.emulateMedia({colorScheme:'dark'});if(await page.locator('html').getAttribute('data-theme')!=='light')failures.push('explicit preference');
 await page.evaluate(()=>localStorage.setItem('gm-appearance','system'));await page.reload();if(await page.locator('html').getAttribute('data-theme')!=='dark')failures.push('system preference');
 for(const r of cat.readers){await page.goto(siteOrigin+'/'+r.slug+'/');const play=page.locator('#play,#play-cover,#play-source,#play-reel,#play-video').first();if(await play.count()){await play.click();if(!(await page.locator('iframe[src^="https://"]').count()))failures.push('player '+r.slug)}else failures.push('play control missing '+r.slug);}
 await context.close();
 const nojs=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:844}});const np=await nojs.newPage();await np.goto('http://127.0.0.1:8765/readers/');if(!(await archiveComplete(np,cat)))failures.push('no-JS archive');
 await nojs.close();await browser.close();fs.writeFileSync(output+'/browser-evidence.json',JSON.stringify({cases:results.length,results,failures},null,2));console.log(JSON.stringify({cases:results.length,failures},null,2));if(failures.length)process.exit(1);
})();
