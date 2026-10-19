(() => {
  const container = document.getElementById('catalog-results');
  const cards = [...container.children];
  const form = document.querySelector('.gm-filters');
  const search = document.getElementById('search');
  const query = new URLSearchParams(location.search).get('q');
  if (query) search.value = query.slice(0, 120);
  const category = document.getElementById('category');
  const tag = document.getElementById('tag');
  const sort = document.getElementById('sort');
  const status = document.getElementById('result-count');
  const normalize = value => value.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase();
  const searchable = new Map(cards.map(card => [card, normalize(card.dataset.search)]));
  function update() {
    const terms = normalize(search.value.trim()).split(/\s+/).filter(Boolean);
    let count = 0;
    cards.sort((a,b) => sort.value === 'title' ? a.querySelector('h3').textContent.localeCompare(b.querySelector('h3').textContent) : sort.value === 'relevance' ? Number(a.dataset.rank)-Number(b.dataset.rank) : b.dataset.date.localeCompare(a.dataset.date) || Number(a.dataset.rank)-Number(b.dataset.rank));
    cards.forEach(card => {
      card.hidden = !(terms.every(term => searchable.get(card).includes(term)) && (!category.value || card.dataset.category === category.value) && (!tag.value || card.dataset.tags.split(' ').includes(tag.value)));
      if (!card.hidden) count++;
      container.appendChild(card);
    });
    status.textContent = count ? `${count} of ${cards.length} Readers` : 'No Readers match. Clear filters to see all Readers.';
  }
  form.addEventListener('submit', event => event.preventDefault());
  form.addEventListener('input', update);
  form.addEventListener('change', update);
  form.addEventListener('reset', () => setTimeout(update, 0));
  update();
})();
