/* Load the version-pinned original PDF only after a deliberate reader action. */
for (const preview of document.querySelectorAll('[data-paper-preview]')) {
  const button = preview.querySelector('[data-paper-open]');
  const original = preview.querySelector('[data-paper-original]');
  const frame = preview.querySelector('[data-paper-frame]');
  if (!button || !original || !frame) continue;
  button.hidden = false;

  button.addEventListener('click', () => {
    const url = new URL(original.href);
    if (url.origin !== 'https://arxiv.org' || !/^\/pdf\/\d{4}\.\d{4,5}v\d+$/.test(url.pathname)) return;
    frame.src = url.href;
    frame.hidden = false;
    button.hidden = true;
  }, { once: true });
}
