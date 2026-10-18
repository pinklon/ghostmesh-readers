/* Local preference only. No network service, tracking or runtime dependency. */
(() => {
  if (window.gmThemeReady) return;
  window.gmThemeReady = true;
  const root = document.documentElement;
  const system = matchMedia('(prefers-color-scheme: dark)');
  // The established GhostMesh landing page opens in dark mode. Visitors can
  // still choose light or system, and that explicit preference persists.
  let choice = 'dark';
  try { const saved = localStorage.getItem('gm-appearance'); if (['light','dark','system'].includes(saved)) choice = saved; } catch (_) {}
  function apply() {
    root.dataset.theme = choice === 'system' ? (system.matches ? 'dark' : 'light') : choice;
    document.querySelectorAll('[data-theme-choice]').forEach(control => { control.value = choice; });
  }
  apply();
  system.addEventListener('change', apply);
  document.addEventListener('DOMContentLoaded', () => {
    apply();
    document.querySelectorAll('[data-theme-choice]').forEach(control => control.addEventListener('change', () => {
      choice = control.value;
      try { localStorage.setItem('gm-appearance', choice); } catch (_) {}
      apply();
    }));
  });
})();
