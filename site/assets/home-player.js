/* Static Reader previews. Third-party players load only after a deliberate click. */
(() => {
  for (const panel of document.querySelectorAll('[data-home-player]')) {
    const poster = panel.querySelector('img');
    if (poster) {
      const failed = () => poster.replaceWith(Object.assign(document.createElement('p'), {
        className: 'gm-home-source-fallback', textContent: 'Source thumbnail unavailable. Use the original source link below.'
      }));
      poster.addEventListener('error', failed, { once: true });
      if (poster.complete && poster.naturalWidth === 0) failed();
    }
    const button = panel.querySelector('[data-home-play]');
    if (!button) continue;
    const platform = panel.dataset.sourcePlatform;
    const id = panel.dataset.sourceId;
    const safe = platform === 'YouTube' ? /^[A-Za-z0-9_-]{11}$/.test(id) :
      platform === 'Instagram' && /^[A-Za-z0-9_-]+$/.test(id);
    if (!safe) continue;
    button.hidden = false;
    button.addEventListener('click', () => {
      const frame = document.createElement('iframe');
      frame.title = platform === 'YouTube' ? 'Original YouTube source video' : 'Original Instagram Reel';
      frame.loading = 'lazy';
      frame.referrerPolicy = 'strict-origin-when-cross-origin';
      frame.allow = 'encrypted-media; picture-in-picture; fullscreen';
      frame.allowFullscreen = true;
      frame.src = platform === 'YouTube' ?
        `https://www.youtube-nocookie.com/embed/${id}?playsinline=1` :
        `https://www.instagram.com/reel/${id}/embed`;
      panel.replaceChildren(frame);
      frame.focus();
    }, { once: true });
  }
})();
