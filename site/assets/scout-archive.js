(() => {
  const form = document.querySelector('.gm-scout-filters');
  const results = document.querySelector('#scout-results');
  const count = document.querySelector('#scout-count');
  if (!form || !results || !count) return;
  const cards = [...results.querySelectorAll('.gm-scout-archive-card')];
  const field = id => document.getElementById(id);
  const q = field('scout-query');
  const topic = field('scout-topic');
  const type = field('scout-type');
  const call = field('scout-call');
  const sort = field('scout-sort');
  const normalize = value => value.toLocaleLowerCase().trim();
  function update() {
    const words = normalize(q.value).split(/\s+/).filter(Boolean);
    const visible = cards.filter(card =>
      words.every(word => normalize(card.dataset.search).includes(word)) &&
      (!topic.value || card.dataset.topic === topic.value) &&
      (!type.value || card.dataset.type === type.value) &&
      (!call.value || card.dataset.call === call.value));
    visible.sort((a,b) => sort.value === 'title'
      ? a.dataset.title.localeCompare(b.dataset.title)
      : b.dataset.date.localeCompare(a.dataset.date) || a.dataset.title.localeCompare(b.dataset.title));
    cards.forEach(card => { card.hidden = !visible.includes(card); });
    visible.forEach(card => results.appendChild(card));
    count.textContent = `${visible.length} of ${cards.length} public reviews shown.`;
  }
  const params = new URLSearchParams(location.search);
  if (params.has('q')) q.value = params.get('q');
  form.addEventListener('input', update);
  form.addEventListener('change', update);
  form.addEventListener('reset', () => requestAnimationFrame(update));
  form.addEventListener('submit', event => { event.preventDefault(); update(); });
  update();
})();
