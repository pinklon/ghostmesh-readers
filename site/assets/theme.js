/* Local preference only. No network service, tracking or runtime dependency. */
(() => {
  if (window.gmThemeReady) return;
  window.gmThemeReady = true;
  const root = document.documentElement;
  const system = matchMedia('(prefers-color-scheme: dark)');
  // Follow the visitor's system preference until they explicitly choose a theme.
  let choice = 'system';
  try { const saved = localStorage.getItem('gm-appearance'); if (['light','dark','system'].includes(saved)) choice = saved; } catch (_) {}
  function apply() {
    root.dataset.theme = choice === 'system' ? (system.matches ? 'dark' : 'light') : choice;
    const isLight = root.dataset.theme === 'light';
    document.querySelectorAll('[data-theme-toggle]').forEach(control => {
      control.hidden = false;
      control.setAttribute('aria-label', 'Light appearance');
      control.setAttribute('aria-pressed', String(isLight));
      control.title = `Light appearance ${isLight ? 'on' : 'off'}`;
    });
  }
  apply();
  system.addEventListener('change', apply);
  document.addEventListener('DOMContentLoaded', () => {
    apply();
    document.querySelectorAll('[data-theme-toggle]').forEach(control => control.addEventListener('click', () => {
      choice = root.dataset.theme === 'dark' ? 'light' : 'dark';
      try { localStorage.setItem('gm-appearance', choice); } catch (_) {}
      apply();
    }));
  });
})();
