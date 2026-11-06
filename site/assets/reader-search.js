/* Search only visible text from the generated public Reader articles. */
(() => {
  let indexPromise;
  const load = () => indexPromise ||= fetch('/readers/search-index.json')
    .then(response => {
      if (!response.ok) throw new Error('Reader index unavailable');
      return response.json();
    })
    .then(index => {
      if (index.schema !== 'ghostmesh-public-reader-text-v1' || !Array.isArray(index.readers) ||
          !Number.isSafeInteger(index.readerCount) || index.readerCount < 1 || index.readers.length !== index.readerCount ||
          index.readers.some(article => !/^\/[a-z0-9-]+\/$/.test(article.url) ||
            !/^reader:[a-z0-9-]+$/.test(article.id) ||
            typeof article.title !== 'string' || typeof article.text !== 'string' || article.text.length < 100))
        throw new Error('Reader index invalid');
      return index.readers;
    });
  window.gmLoadReaderIndex = load;

  /* Optional verified cross-site projection. Reader-only search remains usable if absent. */
  let unifiedPromise;
  const loadUnified = () => unifiedPromise ||= fetch('/readers/unified-search-index.json')
    .then(response => {
      if (!response.ok) throw new Error('Unified index unavailable');
      return response.json();
    })
    .then(index => {
      const sources = index.sources;
      if (index.schema !== 'ghostmesh-unified-search-v1' || !Array.isArray(index.records) ||
          !sources || !sources.Readers || !sources.SharePlane ||
          !Number.isSafeInteger(sources.Readers.count) || !Number.isSafeInteger(sources.SharePlane.count) ||
          sources.Readers.count < 1 || sources.SharePlane.count < 1 ||
          index.records.length !== sources.Readers.count + sources.SharePlane.count ||
          !/^[a-f0-9]{64}$/i.test(sources.SharePlane.sourceCatalogSha256 || '') ||
          index.records.some(record => !['Readers', 'SharePlane'].includes(record.source) ||
            typeof record.title !== 'string' || !record.title.trim() ||
            typeof record.text !== 'string' || !record.text.trim() ||
            typeof record.url !== 'string' || !/^https:\/\//.test(record.url) ||
            (() => { try {
              const url = new URL(record.url);
              return url.protocol !== 'https:' || url.username || url.password ||
                url.hostname !== (record.source === 'Readers' ? 'youtube.shareplane.malott.ai' : 'shareplane.malott.ai') ||
                (record.source === 'SharePlane' && !/^\/(artifacts|market)\/[a-z0-9-]+\/$/.test(url.pathname)) ||
                url.search || url.hash;
            } catch (_) { return true; } })())) throw new Error('Unified index invalid');
      return index.records;
    });


  const normalize = value => value.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase();
  const excerpt = (article, term) => {
    const normalized = normalize(article);
    const at = normalized.indexOf(term);
    if (at < 0) return article.slice(0, 190).trim() + '…';
    const start = Math.max(0, at - 85);
    const end = Math.min(article.length, at + 130);
    return (start ? '…' : '') + article.slice(start, end).trim() + (end < article.length ? '…' : '');
  };
  const findMatches = (articles, query) => {
    const terms = query.split(/\s+/).filter(Boolean);
    if (!terms.length) return [];
    const corpus = article => normalize(article.title + ' ' + (article.category || '') + ' ' + article.text);
    const phraseMatches = articles.filter(article => corpus(article).includes(query));
    return phraseMatches.length ? phraseMatches :
      articles.filter(article => terms.every(term => corpus(article).includes(term)));
  };
  const dialog = document.querySelector('[data-reader-search]');
  const trigger = document.querySelector('[data-reader-search-open]');
  if (!dialog || !trigger || typeof dialog.showModal !== 'function') return;
  const input = dialog.querySelector('#gm-search-input');
  const results = dialog.querySelector('[data-reader-search-results]');
  const status = dialog.querySelector('[data-reader-search-status]');
  let openedBy;
  let renderRevision = 0;
  let activeSource = 'All';
  const sourceFilters = document.createElement('div');
  sourceFilters.className = 'gm-search-source-filters';
  sourceFilters.setAttribute('role', 'group');
  sourceFilters.setAttribute('aria-label', 'Search result source');
  sourceFilters.hidden = true;
  for (const source of ['All', 'Readers', 'SharePlane']) {
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = source === 'All' ? 'All sources' : source;
    button.dataset.source = source;
    button.setAttribute('aria-pressed', String(source === activeSource));
    button.addEventListener('click', () => {
      activeSource = source;
      for (const item of sourceFilters.querySelectorAll('button'))
        item.setAttribute('aria-pressed', String(item.dataset.source === source));
      render();
    });
    sourceFilters.append(button);
  }
  results.before(sourceFilters);
  const render = async () => {
    const revision = ++renderRevision;
    const query = normalize(input.value.trim());
    const terms = query.split(/\s+/).filter(Boolean);
    results.replaceChildren();
    if (!terms.length) { status.textContent = 'Type to search the public Reader articles.'; return; }
    status.textContent = 'Searching published Reader articles…';
    try {
      let articles, limited = false;
      try { articles = await loadUnified(); }
      catch (_) { articles = await load(); limited = true; }
      if (!dialog.open || revision !== renderRevision || normalize(input.value.trim()) !== query) return;
      results.replaceChildren();
      sourceFilters.hidden = limited;
      const matches = findMatches(articles, query).filter(article => limited || activeSource === 'All' || article.source === activeSource);
      status.textContent = matches.length ?
        `${matches.length} of ${articles.length} public ${limited ? 'Reader articles' : 'Reader and SharePlane works'} match.${limited ? ' SharePlane search is temporarily unavailable.' : ''}` :
        `No ${limited ? 'Reader articles' : 'public works'} match. Try another claim, source or phrase.${limited ? ' SharePlane search is temporarily unavailable.' : ''}`;
      for (const article of matches) {
        const link = document.createElement('a');
        link.href = article.url;
        const type = document.createElement('small');
        type.textContent = (article.source === 'SharePlane' ? 'SHAREPLANE / ' : 'READER / ') + (article.category || 'PUBLIC WORK');
        const title = document.createElement('strong');
        title.textContent = article.title;
        const snippet = document.createElement('span');
        snippet.textContent = excerpt(article.text,
          normalize(article.text).includes(query) ? query : (terms.find(term => normalize(article.text).includes(term)) || terms[0]));
        link.append(type, title, snippet);
        results.append(link);
      }
    } catch (_) {
      if (!dialog.open || revision !== renderRevision) return;
      results.replaceChildren();
      sourceFilters.hidden = true;
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
    activeSource = 'All';
    for (const item of sourceFilters.querySelectorAll('button'))
      item.setAttribute('aria-pressed', String(item.dataset.source === 'All'));
    render();
  });
  dialog.querySelector('[data-reader-search-close]').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
  dialog.addEventListener('close', () => openedBy?.focus());
  input.addEventListener('input', render);
  input.addEventListener('keydown', event => {
    if (event.key === 'ArrowDown') { const first = results.querySelector('a'); if (first) { event.preventDefault(); first.focus(); } }
  });

  const homeInput = document.getElementById('home-query');
  if (homeInput) {
    const panel = document.createElement('div');
    panel.className = 'gm-home-live';
    panel.setAttribute('aria-live', 'polite');
    panel.hidden = true;
    homeInput.closest('form').after(panel);
    homeInput.addEventListener('input', async () => {
      const query = normalize(homeInput.value.trim());
      panel.replaceChildren();
      panel.hidden = !query;
      if (!query) return;
      panel.textContent = 'Searching published Reader articles…';
      try {
        let articles, limited = false;
        try { articles = await loadUnified(); }
        catch (_) { articles = await load(); limited = true; }
        if (normalize(homeInput.value.trim()) !== query) return;
        const matches = findMatches(articles, query);
        panel.replaceChildren();
        const summary = document.createElement('p');
        summary.textContent = matches.length ? `${matches.length} public ${limited ? 'Reader article' : 'work'}${matches.length === 1 ? '' : 's'} match as you type.${limited ? ' SharePlane search unavailable.' : ''}` :
          `No public ${limited ? 'Reader articles' : 'works'} match. Try another phrase.`;
        panel.append(summary);
        for (const article of matches.slice(0, 5)) {
          const link = document.createElement('a');
          link.href = article.url;
          const label = document.createElement('strong');
          label.textContent = article.title;
          const snippet = document.createElement('span');
          snippet.textContent = excerpt(article.text, normalize(article.text).includes(query) ? query : query.split(/\s+/)[0]);
          const type = document.createElement('small');
          type.textContent = article.source === 'SharePlane' ? 'SHAREPLANE' : 'READER';
          link.append(type, label, snippet);
          panel.append(link);
        }
      } catch (_) {
        panel.textContent = 'Live article search is unavailable. Submit the query to browse the Reader archive.';
      }
    });
  }
})();
