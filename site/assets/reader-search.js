/* Search only visible text from the thirteen generated public Reader articles. */
(() => {
  let indexPromise;
  const load = () => indexPromise ||= fetch('/readers/search-index.json')
    .then(response => {
      if (!response.ok) throw new Error('Reader index unavailable');
      return response.json();
    })
    .then(index => {
      if (index.schema !== 'ghostmesh-public-reader-text-v1' || !Array.isArray(index.readers) || index.readers.length !== 13 ||
          index.readers.some(article => !/^\/[a-z0-9-]+\/$/.test(article.url) ||
            !/^reader:[a-z0-9-]+$/.test(article.id) ||
            typeof article.title !== 'string' || typeof article.text !== 'string' || article.text.length < 100))
        throw new Error('Reader index invalid');
      return index.readers;
    });
  window.gmLoadReaderIndex = load;

  const normalize = value => value.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase();
  const excerpt = (article, term) => {
    const normalized = normalize(article);
    const at = normalized.indexOf(term);
    if (at < 0) return article.slice(0, 190).trim() + '…';
    const start = Math.max(0, at - 85);
    const end = Math.min(article.length, at + 130);
    return (start ? '…' : '') + article.slice(start, end).trim() + (end < article.length ? '…' : '');
  };
  const dialog = document.querySelector('[data-reader-search]');
  const trigger = document.querySelector('[data-reader-search-open]');
  if (!dialog || !trigger || typeof dialog.showModal !== 'function') return;
  const input = dialog.querySelector('#gm-search-input');
  const results = dialog.querySelector('[data-reader-search-results]');
  const status = dialog.querySelector('[data-reader-search-status]');
  let openedBy;
  const render = async () => {
    const query = normalize(input.value.trim());
    const terms = query.split(/\s+/).filter(Boolean);
    results.replaceChildren();
    if (!terms.length) { status.textContent = 'Type to search the public Reader articles.'; return; }
    status.textContent = 'Searching published Reader articles…';
    try {
      const articles = await load();
      if (!dialog.open) return;
      const corpus = article => normalize(article.title + ' ' + article.category + ' ' + article.text);
      const phraseMatches = articles.filter(article => corpus(article).includes(query));
      const matches = phraseMatches.length ? phraseMatches :
        articles.filter(article => terms.every(term => corpus(article).includes(term)));
      status.textContent = matches.length ? `${matches.length} of ${articles.length} Reader articles match.` :
        'No Reader articles match. Try another claim, source or phrase.';
      for (const article of matches) {
        const link = document.createElement('a');
        link.href = article.url;
        const type = document.createElement('small');
        type.textContent = article.category + ' / PUBLIC READER';
        const title = document.createElement('strong');
        title.textContent = article.title;
        const snippet = document.createElement('span');
        snippet.textContent = excerpt(article.text,
          normalize(article.text).includes(query) ? query : (terms.find(term => normalize(article.text).includes(term)) || terms[0]));
        link.append(type, title, snippet);
        results.append(link);
      }
    } catch (_) {
      status.textContent = 'Search is unavailable. Browse the complete Reader library below.';
      const fallback = document.createElement('a');
      fallback.href = '/readers/';
      fallback.textContent = 'Browse all Readers →';
      results.append(fallback);
    }
  };
  trigger.addEventListener('click', event => {
    event.preventDefault();
    openedBy = trigger;
    dialog.showModal();
    input.focus();
    render();
  });
  dialog.querySelector('[data-reader-search-close]').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
  dialog.addEventListener('close', () => openedBy?.focus());
  input.addEventListener('input', render);
  input.addEventListener('keydown', event => {
    if (event.key === 'ArrowDown') { const first = results.querySelector('a'); if (first) { event.preventDefault(); first.focus(); } }
  });
})();
