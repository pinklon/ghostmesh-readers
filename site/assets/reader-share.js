(function () {
  "use strict";
  const bar=document.querySelector('[data-gm-share]');
  if(!bar) return;
  const canonical=document.querySelector('link[rel="canonical"]')?.href || location.href;
  const title=document.title.split(' | ')[0].split(' — GhostMesh')[0].trim();
  const description=document.querySelector('meta[name="gm-share-description"]')?.content?.trim() ||
    document.querySelector('meta[property="og:description"]')?.content?.trim() ||
    'An independent GhostMesh Reader with the original source, evidence and explicit limits.';
  const notice=bar.querySelector('[data-gm-share-message]');
  const shareIcon='<svg class="gm-share-icon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="18" cy="5" r="2"/><circle cx="6" cy="12" r="2"/><circle cx="18" cy="19" r="2"/><path d="m8 11 8-5M8 13l8 5"/></svg>';
  const copyIcon='<svg class="gm-share-icon" viewBox="0 0 24 24" aria-hidden="true"><rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2"/></svg>';
  const shareButton=bar.querySelector('[data-native-share]');
  const copyButton=bar.querySelector('[data-copy-link]');
  if(shareButton) shareButton.insertAdjacentHTML('afterbegin',shareIcon);
  if(copyButton) copyButton.insertAdjacentHTML('afterbegin',copyIcon);
  function show(message){notice.textContent=message;notice.setAttribute('role','status');}
  async function copyLink(){
    try{
      if(!navigator.clipboard?.writeText) throw new Error('Clipboard API unavailable');
      await navigator.clipboard.writeText(canonical);
    }catch(_){
      const field=document.createElement('textarea');
      field.value=canonical;
      field.style.position='fixed';field.style.left='-9999px';
      document.body.appendChild(field);field.focus();field.select();
      const ok=document.execCommand('copy');
      field.remove();
      if(!ok){show('Copy the address from your browser bar.');return;}
    }
    show('Link copied.');
  }
  bar.querySelector('[data-copy-link]')?.addEventListener('click',copyLink);
  bar.querySelector('[data-native-share]')?.addEventListener('click',async()=>{
    if(typeof navigator.share!=='function'){await copyLink();return;}
    try{await navigator.share({title, text:description, url:canonical});show('Share panel opened.');}
    catch(e){if(e?.name!=='AbortError')await copyLink();}
  });
  const mail=bar.querySelector('[data-email-link]');
  if(mail) mail.href='mailto:?subject='+encodeURIComponent('GhostMesh Reader: '+title)+'&body='+encodeURIComponent(description+'\n\n'+canonical);
  // Enhance timestamped publisher rows only when an opt-in source player exists.
  // Older articles with their own chapter controls keep those controls untouched.
  const play=document.getElementById('play');
  const player=document.getElementById('player');
  if(play && player){
    document.querySelectorAll('.chapters .chapter').forEach(chapter=>{
      if(chapter.querySelector('button')) return;
      const source=chapter.querySelector('a[href*="youtube.com/watch"],a[href*="youtu.be/"]');
      const time=chapter.querySelector('time');
      if(!source || !time) return;
      let start;
      try { start=Number(new URL(source.href).searchParams.get('t')?.replace(/s$/,'')); }
      catch(_) { return; }
      if(!Number.isSafeInteger(start) || start<0) return;
      const action=document.createElement('div');
      action.className='gm-chapter-actions';
      const button=document.createElement('button');
      button.type='button';
      button.textContent='Play from '+time.textContent.trim()+' ↑';
      button.setAttribute('aria-label','Play original video from '+time.textContent.trim());
      button.addEventListener('click',()=>{
        play.click();
        const frame=player.querySelector('iframe');
        if(frame){
          const url=new URL(frame.src);
          url.searchParams.set('start',String(start));
          frame.src=url.toString();
          const reduceMotion=window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
          player.scrollIntoView({behavior:reduceMotion?'auto':'smooth',block:'center'});
        }else window.open(source.href,'_blank','noopener,noreferrer');
      });
      source.textContent='YouTube ↗';
      const holder=source.closest('p');
      action.append(button,source);
      if(holder && holder.children.length===0 && !holder.textContent.trim()) holder.remove();
      chapter.append(action);
    });
  }
})();
