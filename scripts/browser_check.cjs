// Optional development verification. Requires Playwright and installed Chrome, not used by hosting.
const output=process.env.GM_TEST_OUTPUT || '/tmp/ghostmesh-reader-checks';
require('fs').mkdirSync(output+'/screenshots',{recursive:true});
const { chromium } = require('playwright');
const fs=require('fs');
const {archiveComplete}=require('./browser_assertions.cjs');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:"chrome"});
 const cat=JSON.parse(fs.readFileSync('content/catalog.json'));
 const paths=['','readers',...cat.readers.map(r=>r.slug)];const results=[];const failures=[];
 for(const width of [390,1440])for(const theme of ['light','dark']){
  const context=await browser.newContext({viewport:{width,height:1000},colorScheme:theme,reducedMotion:'reduce'});
  await context.route('**/*',route=>route.request().url().startsWith('http://127.0.0.1:8765')?route.continue():route.abort());
  const page=await context.newPage();page.on('pageerror',e=>failures.push(e.message));
  for(const path of paths){
   await page.goto('http://127.0.0.1:8765/'+path+'/');
   const result=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth,theme:document.documentElement.dataset.theme,brief:!!document.getElementById('at-a-glance'),h1:document.querySelectorAll('h1').length,preload:[...document.querySelectorAll('iframe')].some(f=>f.src&&!f.src.startsWith('about:'))}));
   if(result.scroll>width+1||result.theme!==theme||result.preload)failures.push({path,width,theme,...result});
   results.push({path,width,theme,...result});
   await page.screenshot({path:`${output}/screenshots/${path||'home'}-${width}-${theme}.png`,fullPage:false});
  }
  await context.close();
 }
 const context=await browser.newContext({viewport:{width:390,height:844}});await context.route('**/*',r=>r.request().url().startsWith('http://127.0.0.1:8765')?r.continue():r.abort());const page=await context.newPage();
 await page.goto('http://127.0.0.1:8765/readers/');await page.locator('#search').fill('Strix');if(await page.locator('.gm-card:visible').count()!==1)failures.push('search Strix');
 await page.locator('button[type=reset]').click();await page.locator('#category').selectOption('Business');if(await page.locator('.gm-card:visible').count()!==2)failures.push('category Business');
 await page.locator('#tag').selectOption('security');if(await page.locator('.gm-card:visible').count()!==0)failures.push('combined filters');
 await page.locator('[data-theme-choice]').selectOption('dark');await page.reload();if(await page.locator('html').getAttribute('data-theme')!=='dark')failures.push('theme persistence');
 await page.locator('[data-theme-choice]').selectOption('light');await page.emulateMedia({colorScheme:'dark'});if(await page.locator('html').getAttribute('data-theme')!=='light')failures.push('explicit preference');
 await page.locator('[data-theme-choice]').selectOption('system');if(await page.locator('html').getAttribute('data-theme')!=='dark')failures.push('system preference');
 for(const r of cat.readers){await page.goto('http://127.0.0.1:8765/'+r.slug+'/');const play=page.locator('#play,#play-cover,#play-source,#play-reel,#play-video').first();if(await play.count()){await play.click();if(!(await page.locator('iframe[src^="https://"]').count()))failures.push('player '+r.slug)}else failures.push('play control missing '+r.slug);}
 await context.close();
 const nojs=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:844}});const np=await nojs.newPage();await np.goto('http://127.0.0.1:8765/readers/');if(!(await archiveComplete(np,cat)))failures.push('no-JS archive');
 await nojs.close();await browser.close();fs.writeFileSync(output+'/browser-evidence.json',JSON.stringify({cases:results.length,results,failures},null,2));console.log(JSON.stringify({cases:results.length,failures},null,2));if(failures.length)process.exit(1);
})();
