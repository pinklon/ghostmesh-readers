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
  const label=bar.querySelector('.gm-share-label');
  if(label){
    const summary=document.createElement('p');
    summary.className='gm-share-description';
    summary.textContent=description;
    label.after(summary);
  }
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
    show('Reader link copied.');
  }
  bar.querySelector('[data-copy-link]')?.addEventListener('click',copyLink);
  bar.querySelector('[data-native-share]')?.addEventListener('click',async()=>{
    if(typeof navigator.share!=='function'){await copyLink();return;}
    try{await navigator.share({title, text:description, url:canonical});show('Share panel opened.');}
    catch(e){if(e?.name!=='AbortError')await copyLink();}
  });
  const mail=bar.querySelector('[data-email-link]');
  if(mail) mail.href='mailto:?subject='+encodeURIComponent('GhostMesh Reader: '+title)+'&body='+encodeURIComponent(description+'\n\n'+canonical);
})();
