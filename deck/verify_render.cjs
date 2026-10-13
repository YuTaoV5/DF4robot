// Render and inspect the offline deck with a real Chromium engine.
// Set NODE_PATH to your installed Playwright package directory if needed.
const {chromium}=require('playwright');
const fs=require('fs'); const path=require('path'); const {pathToFileURL}=require('url');
(async()=>{
 const out=path.resolve(__dirname,'rendered');fs.mkdirSync(out,{recursive:true});
 const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME||'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const page=await browser.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:1});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(pathToFileURL(path.resolve(__dirname,'deck.html')).href);
 await page.evaluate(()=>document.fonts.ready);
 const count=await page.locator('.slide').count();const layout=[];
 for(let i=1;i<=count;i++){
  if(i>1)await page.keyboard.press('ArrowRight');
  await page.waitForTimeout(70);
  const checks=await page.evaluate(()=>{
   const s=document.querySelector('.slide.active');const sr=s.getBoundingClientRect();const problems=[];
   for(const el of s.querySelectorAll('h1,.sub,.kicker,td,th,.card,.mathcard,.event-controls,.reading a,svg text')){
    const r=el.getBoundingClientRect();
    if(r.right>sr.right-30||r.bottom>sr.bottom-30||r.left<sr.left-1)problems.push({text:el.textContent.slice(0,90),reason:'stage bounds',rect:[r.x,r.y,r.width,r.height]});
    if(el.tagName.toLowerCase()==='text'){
     const v=el.closest('svg').getBoundingClientRect();
     if(r.left<v.left-2||r.right>v.right+2||r.top<v.top-2||r.bottom>v.bottom+2)problems.push({text:el.textContent,reason:'svg bounds'});
    }
    if(el.scrollWidth>el.clientWidth+3 && ['TD','TH','H1'].includes(el.tagName))problems.push({text:el.textContent,reason:'overflow'});
   }
   return {page:Number(location.hash.slice(1)),title:s.dataset.title,problems};
  });layout.push(checks);
  await page.screenshot({path:path.join(out,`slide-${String(i).padStart(2,'0')}.png`)});
 }
 // Interaction checks: navigation, Gaussian calculation, timeline, animation, notes.
 await page.keyboard.press('Home');await page.keyboard.press('1');await page.keyboard.press('0');await page.waitForTimeout(650);
 const initial=await page.evaluate(()=>window.gaussianResult);
 if(Math.abs(initial.mean-1.1047619047619048)>1e-9)errors.push('Gaussian default mismatch');
 await page.locator('#sigma').fill('3');await page.locator('#sigma').dispatchEvent('input');
 const changed=await page.evaluate(()=>window.gaussianResult);
 if(!(changed.variance>initial.variance))errors.push('Gaussian variance response failed');
 await page.locator('#sigma').fill('0.2');await page.locator('#sigma').dispatchEvent('input');
 const narrow=await page.evaluate(()=>({result:window.gaussianResult,paths:[...document.querySelectorAll('#gaussPlot path')].map(p=>{const b=p.getBBox();return {y:b.y,bottom:b.y+b.height};})}));
 if(narrow.paths.some(p=>p.y<0||p.bottom>500))errors.push('Narrow Gaussian curve clipped');
 await page.screenshot({path:path.join(out,'gaussian-narrow.png')});
 await page.locator('#gaussReset').click();
 await page.keyboard.press('1');await page.keyboard.press('4');await page.waitForTimeout(650);
 await page.locator('[data-event="2"]').click();
 if(!(await page.locator('#eventText').innerText()).includes('75'))errors.push('Timeline interaction failed');
 await page.keyboard.press('2');await page.keyboard.press('2');await page.waitForTimeout(650);
 const first=await page.locator('.slide.active [data-a].on').count();
 for(let k=0;k<4;k++)await page.keyboard.press('j');
 const last=await page.locator('.slide.active [data-a].on').count();
 if(first!==1||last!==5)errors.push('Animation stages failed');
 await page.screenshot({path:path.join(out,'animation-final.png')});
 await page.keyboard.press('n');
 if(!(await page.locator('#notes').isVisible()))errors.push('Notes failed');
 const report={slides:count,errors,layout:layout.filter(p=>p.problems.length),gaussian:{initial,changed,narrow},animation:{first,last},generated:new Date().toISOString()};
 fs.writeFileSync(path.resolve(__dirname,'validation.json'),JSON.stringify(report,null,2));
 await browser.close();console.log(JSON.stringify(report,null,2));
 if(errors.length||report.layout.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
