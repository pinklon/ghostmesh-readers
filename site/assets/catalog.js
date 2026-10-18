(() => {
  const container = document.getElementById('catalog-results');
  const cards = [...container.children];
  const form = document.querySelector('.gm-filters');
  const search = document.getElementById('search');
  const category = document.getElementById('category');
  const tag = document.getElementById('tag');
  const sort = document.getElementById('sort');
  function update() {
    const query = search.value.trim().toLocaleLowerCase();
    let count = 0;
    cards.sort((a,b) => sort.value === 'title' ? a.querySelector('h3').textContent.localeCompare(b.querySelector('h3').textContent) : sort.value === 'relevance' ? Number(a.dataset.rank)-Number(b.dataset.rank) : b.dataset.date.localeCompare(a.dataset.date) || Number(a.dataset.rank)-Number(b.dataset.rank));
    cards.forEach(card => {
      card.hidden = !(card.textContent.toLocaleLowerCase().includes(query) && (!category.value || card.dataset.category === category.value) && (!tag.value || card.dataset.tags.split(' ').includes(tag.value)));
      if (!card.hidden) count++;
      container.appendChild(card);
    });
    document.getElementById('result-count').textContent = count ? `${count} Reader${count === 1 ? '' : 's'}` : 'No Readers match. Clear a filter or reset your search.';
  }
  form.addEventListener('input', update);
  form.addEventListener('change', update);
  form.addEventListener('reset', () => setTimeout(update, 0));
})();
