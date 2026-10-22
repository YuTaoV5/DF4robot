// Deterministic verification of every animation stage and interactive formula.
const {chromium}=require('playwright');
const fs=require('fs'),path=require('path'),{pathToFileURL}=require('url');
(async()=>{
 const out=path.join(__dirname,'rendered');fs.mkdirSync(out,{recursive:true});
 const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME||'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const page=await browser.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:1});
 await page.context().setOffline(true);
 const errors=[],layout=[],animation=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(pathToFileURL(path.join(__dirname,'deck.html')).href);
 await page.evaluate(()=>document.fonts.ready);
 const count=await page.locator('.slide').count();
 for(let n=1;n<=count;n++){
  await page.evaluate(n=>window.deck.go(n),n);
  for(let k=0;k<4;k++){
   await page.evaluate(k=>window.deck.setStep(k),k);
   const problems=await page.evaluate(()=>{
    const sl=document.querySelector('.slide.active'),problems=[];
    for(const el of sl.querySelectorAll('h1,.sub,.kicker,.caption,.mathhint,.step,svg text')){
     const r=el.getBoundingClientRect();
     if(r.left<120||r.right>1800||r.bottom>1005||r.top<35)problems.push({text:el.textContent,reason:'stage bounds',rect:[r.x,r.y,r.width,r.height]});
     if(el.tagName.toLowerCase()==='text'){
      const v=el.closest('svg').getBoundingClientRect();if(r.left<v.left-2||r.right>v.right+2||r.top<v.top-2||r.bottom>v.bottom+2)problems.push({text:el.textContent,reason:'svg bounds'});
     }else if(el.scrollWidth>el.clientWidth+3)problems.push({text:el.textContent,reason:'overflow'});
    }return problems;
   });if(problems.length)layout.push({page:n,step:k,problems});
   await page.screenshot({path:path.join(out,`phase-${String(n).padStart(2,'0')}-${k}.png`)});
  }
  await page.screenshot({path:path.join(out,`slide-${String(n).padStart(2,'0')}.png`)});
  let moves=[];
  for(let k=0;k<4;k++){
   await page.evaluate(k=>{window.deck.setStep(k);window.deck.advance(-3.8);},k);
   const a=await page.locator('.slide.active svg').innerHTML();await page.evaluate(()=>window.deck.advance(1.9));
   const b=await page.locator('.slide.active svg').innerHTML();moves.push(a!==b);
  }
  animation.push({page:n,withinStageMotion:moves.some(Boolean),movingStages:moves});
  if(!moves.some(Boolean))errors.push(`Page ${n} has no moving geometry`);
 }
 await page.evaluate(()=>window.deck.go(3));await page.evaluate(()=>window.deck.setStep(3));
 const initial=await page.evaluate(()=>window.kalmanResult);
 if(Math.abs(initial.mean-1.6)>1e-10||Math.abs(initial.variance-.8)>1e-10)errors.push('Kalman numeric example failed');
 await page.locator('#noise').fill('9');await page.locator('#noise').dispatchEvent('input');
 const noisy=await page.evaluate(()=>window.kalmanResult);
 if(!(noisy.gain<initial.gain&&noisy.variance>initial.variance))errors.push('Noise response failed');
 if(!(await page.locator('.slide.active .caption').innerText()).includes(noisy.variance.toFixed(2)))errors.push('Caption not synchronized with formula');
 await page.locator('#noise').fill('0.25');await page.locator('#noise').dispatchEvent('input');
 const narrow=await page.locator('.slide.active svg').evaluate(svg=>[...svg.querySelectorAll('path')].every(p=>{const b=p.getBBox();return b.y>=0&&b.y+b.height<=530;}));
 if(!narrow)errors.push('Kalman narrow curve clips');
 await page.locator('#noise').fill('1');await page.locator('#noise').dispatchEvent('input');
 await page.screenshot({path:path.join(out,'kalman-detail.png')});
 await page.evaluate(()=>document.activeElement.blur());
 await page.keyboard.press('Home');await page.evaluate(()=>window.deck.pause());await page.keyboard.press('j');
 if((await page.evaluate(()=>window.deck.getState())).step!==1)errors.push('J key failed');
 await page.keyboard.press('k');if((await page.evaluate(()=>window.deck.getState())).step!==0)errors.push('K key failed');
 await page.keyboard.press('p');await page.waitForTimeout(400);
 if(!(await page.evaluate(()=>window.deck.getState())).playing)errors.push('Playback failed');
 await page.keyboard.press('p');let before=await page.evaluate(()=>window.deck.getState().elapsed);await page.waitForTimeout(200);
 if(Math.abs((await page.evaluate(()=>window.deck.getState().elapsed))-before)>.02)errors.push('Pause failed');
 await page.keyboard.press('n');if(!await page.locator('#notes').isVisible())errors.push('Notes failed');await page.keyboard.press('Escape');
 await page.keyboard.press('g');await page.locator('#nav button[data-page="8"]').click();
 if((await page.evaluate(()=>window.deck.getState())).page!==9)errors.push('Menu failed');
 await page.keyboard.press('End');if((await page.evaluate(()=>window.deck.getState())).page!==count)errors.push('End failed');
 await page.keyboard.press('Home');await page.keyboard.press('1');await page.keyboard.press('4');await page.waitForTimeout(600);
 if((await page.evaluate(()=>window.deck.getState())).page!==14)errors.push('Numeric navigation failed');
 const figures=[];
 for(const n of [14,18,20,23,24]){
  await page.evaluate(n=>window.deck.go(n),n);
  await page.locator('.slide.active [data-paper]').click();
  await page.waitForFunction(()=>document.querySelector('#figure-full').naturalWidth>0);
  const loaded=await page.locator('#figure-full').evaluate(img=>img.src.startsWith('data:image/')&&img.naturalWidth>0);
  if(!loaded||!await page.locator('#figure-modal').isVisible())errors.push(`Paper image failed on page ${n}`);
  await page.keyboard.press('Escape');
  if(await page.locator('#figure-modal').isVisible())errors.push(`Image close failed on page ${n}`);
  const links=await page.locator('.slide.active .source-links a').evaluateAll(as=>as.map(a=>a.href));
  if(!links.length||links.some(x=>!x.startsWith('https://')))errors.push(`Source links failed on page ${n}`);
  figures.push({page:n,loaded,links});
 }
 const report={slides:count,stagesChecked:count*4,offline:true,figures,errors,layout,animation,kalman:{initial,noisy,narrow},generated:new Date().toISOString()};
 fs.writeFileSync(path.join(__dirname,'validation.json'),JSON.stringify(report,null,2));
 await browser.close();console.log(JSON.stringify(report,null,2));if(errors.length||layout.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
