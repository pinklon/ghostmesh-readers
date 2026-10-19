/* Optional source-directory controls; every record remains readable without JS. */
(() => {
  const form = document.querySelector('[data-knowledge-tools]');
  if (!form) return;
  const query = form.querySelector('[data-knowledge-query]');
  const filter = form.querySelector('[data-knowledge-filter]');
  const rows = [...document.querySelectorAll('.kx-record')];
  const result = document.querySelector('[data-knowledge-results]');
  const empty = document.querySelector('[data-knowledge-empty]');
  const fold = value => value.toLocaleLowerCase().normalize('NFKD').replace(/[\u0300-\u036f]/g, '');
  const indexed = rows.map(row => ({row, text: fold(row.textContent)}));

  function update() {
    const terms = fold(query.value.trim()).split(/\s+/).filter(Boolean);
    let shown = 0;
    for (const {row, text} of indexed) {
      const matches = terms.every(term => text.includes(term)) &&
        (filter.value === 'all' || row.dataset.trace === filter.value);
      row.hidden = !matches;
      if (matches) shown += 1;
    }
    result.textContent = `Showing ${shown} of ${rows.length} Reader sources`;
    empty.hidden = shown !== 0;
  }

  form.hidden = false;
  form.addEventListener('submit', event => event.preventDefault());
  form.addEventListener('input', update);
  form.addEventListener('change', update);
  form.addEventListener('reset', () => requestAnimationFrame(update));
})();
