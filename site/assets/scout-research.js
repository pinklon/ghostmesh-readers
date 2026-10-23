(() => {
  const form = document.getElementById('scout-research-filters');
  const results = document.getElementById('research-results');
  const count = document.getElementById('research-count');
  if (!form || !results || !count) return;
  const cards = [...results.querySelectorAll('[data-research-card]')];
  const query = document.getElementById('research-query');
  const type = document.getElementById('research-type');
  const topic = document.getElementById('research-topic');
  const norm = text => text.toLocaleLowerCase().trim();
  function update() {
    const words = norm(query.value).split(/\s+/).filter(Boolean);
    let shown = 0;
    for (const card of cards) {
      const tags = card.dataset.topic.split(' ');
      const show = words.every(word => norm(card.dataset.search).includes(word)) &&
        (!type.value || card.dataset.type === type.value) &&
        (!topic.value || tags.includes(topic.value));
      card.hidden = !show;
      if (show) shown++;
    }
    count.textContent = `${shown} of ${cards.length} public works shown.`;
  }
  const params = new URLSearchParams(location.search);
  if (params.has('q')) query.value = params.get('q');
  form.addEventListener('input', update);
  form.addEventListener('change', update);
  form.addEventListener('reset', () => requestAnimationFrame(update));
  form.addEventListener('submit', event => { event.preventDefault(); update(); });
  update();
})();
