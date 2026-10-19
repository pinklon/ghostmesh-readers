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
  let articleIndexUnavailable = false;
  const normalize = value => value.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase();
  const searchable = new Map(cards.map(card => [card, { text: card.dataset.search, complete: false }]));
  const snippets = new Map(cards.map(card => {
    const snippet = document.createElement('p');
    snippet.className = 'gm-library-match-snippet';
    snippet.hidden = true;
    card.querySelector('.gm-library-copy > p:not(.gm-kicker)')?.after(snippet);
    return [card, snippet];
  }));
  function update() {
    const query = normalize(search.value.trim());
    const terms = query.split(/\s+/).filter(Boolean);
    const exact = cards.some(card => normalize(searchable.get(card).text).includes(query));
    let count = 0;
    cards.sort((a,b) => sort.value === 'title' ? a.querySelector('h3').textContent.localeCompare(b.querySelector('h3').textContent) : sort.value === 'relevance' ? Number(a.dataset.rank)-Number(b.dataset.rank) : b.dataset.date.localeCompare(a.dataset.date) || Number(a.dataset.rank)-Number(b.dataset.rank));
    cards.forEach(card => {
      const document = searchable.get(card);
      const matchingText = normalize(document.text);
      card.hidden = !((!terms.length || (exact ? matchingText.includes(query) : terms.every(term => matchingText.includes(term)))) && (!category.value || card.dataset.category === category.value) && (!tag.value || card.dataset.tags.split(' ').includes(tag.value)));
      if (!card.hidden) count++;
      const snippet = snippets.get(card);
      const term = matchingText.includes(query) ? query : terms.find(value => matchingText.includes(value));
      const at = term ? normalize(document.text).indexOf(term) : -1;
      snippet.hidden = !document.complete || !terms.length || at < 0 || card.hidden;
      if (!snippet.hidden) snippet.textContent = 'In the Reader: ' + (at > 75 ? '…' : '') +
        document.text.slice(Math.max(0, at - 75), Math.min(document.text.length, at + 145)).trim() + '…';
      container.appendChild(card);
    });
    status.textContent = (count ? `${count} of ${cards.length} Readers` : 'No Readers match. Clear filters to see all Readers.') +
      (articleIndexUnavailable ? ' Article-text search is unavailable; title and topic filtering remains.' : '');
  }
  form.addEventListener('submit', event => event.preventDefault());
  form.addEventListener('input', update);
  form.addEventListener('change', update);
  form.addEventListener('reset', () => setTimeout(update, 0));
  update();
  (window.gmLoadReaderIndex ? window.gmLoadReaderIndex() : fetch('/readers/search-index.json').then(r => r.json()).then(x => x.readers))
    .then(articles => {
      const byURL = new Map(articles.map(article => [article.url, article]));
      for (const card of cards) {
        const article = byURL.get(card.querySelector('h3 a')?.getAttribute('href'));
        if (article) searchable.set(card, { text: article.title + ' ' + article.category + ' ' + article.text, complete: true });
      }
      update();
    })
    .catch(() => { articleIndexUnavailable = true; update(); });
})();
