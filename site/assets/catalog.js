(() => {
  const container = document.getElementById('catalog-results');
  const cards = [...container.children];
  for (const poster of container.querySelectorAll('.gm-library-poster img')) {
    const failed = () => poster.replaceWith(Object.assign(document.createElement('span'), {
      textContent: 'Source thumbnail unavailable. Open the Reader or original source.'
    }));
    poster.addEventListener('error', failed, { once: true });
    if (poster.complete && poster.naturalWidth === 0) failed();
  }
  const form = document.querySelector('.gm-filters');
  const search = document.getElementById('search');
  const category = document.getElementById('category');
  const tag = document.getElementById('tag');
  const sort = document.getElementById('sort');
  const status = document.getElementById('result-count');
  const normalize = value => value.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase();
  const searchable = new Map(cards.map(card => [card, normalize(card.textContent + ' ' + card.dataset.tags)]));
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
