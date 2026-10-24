const { chromium } = require('playwright');
const assert = require('node:assert/strict');

const base = 'http://127.0.0.1:8765';
const readerCount = require('../content/catalog.json').readers.length;
const relationshipCount = require('../content/catalog.json').readers.reduce((count, reader) => count + reader.relationships.length, 0);
const routes = ['/', '/readers/', '/knowledge/', '/map/', '/ask-for-the-outcome-keep-the-boundary/', '/a-challenge-is-not-a-verdict/', '/the-engine-is-not-the-service/'];

async function deepInferColors(page) {
  return page.evaluate(() => {
    const rgb = value => value.match(/[\d.]+/g).slice(0, 3).map(Number);
    const luminance = value => {
      const [r, g, b] = rgb(value).map(channel => {
        const n = channel / 255;
        return n <= 0.04045 ? n / 12.92 : ((n + 0.055) / 1.055) ** 2.4;
      });
      return 0.2126 * r + 0.7152 * g + 0.0722 * b;
    };
    const background = element => {
      for (let node = element; node; node = node.parentElement) {
        const color = getComputedStyle(node).backgroundColor;
        if (color !== 'rgba(0, 0, 0, 0)' && color !== 'transparent') return color;
      }
      throw new Error('Missing opaque background');
    };
    const selectors = ['h1', '.deck', '.source-panel p', '.source-panel a', '.source-panel aside', '.story p', '.pull', '.matrix th', '.endnote', '.gm-brief .gm-brief-point p', '.gm-evidence-intro p:not(.gm-kicker)', '.gm-claim-proposition', '.gm-share-label', '.gm-share-button', '.gm-share-email'];
    const colors = Object.fromEntries(selectors.map(selector => {
      const element = document.querySelector(selector);
      if (!element) throw new Error(`DeepInfer theme target missing: ${selector}`);
      const foreground = getComputedStyle(element).color;
      const backdrop = background(element);
      const a = luminance(foreground), b = luminance(backdrop);
      return [selector, { foreground, backdrop, contrast: (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05) }];
    }));
    return { body: getComputedStyle(document.body).color, background: background(document.body), colors };
  });
}

(async () => {
  const browser = await chromium.launch({ headless: true, channel: 'chrome' });
  let cases = 0;
  try {
    for (const width of [390, 1440]) for (const theme of ['dark', 'light']) {
      const context = await browser.newContext({ viewport: { width, height: 900 }, reducedMotion: 'reduce' });
      await context.addInitScript(choice => localStorage.setItem('gm-appearance', choice), theme);
      await context.addInitScript(() => Object.defineProperty(navigator, 'share', { configurable: true,
        value: data => { window.__gmShared = data; return Promise.resolve(); } }));
      await context.route('**/*', route => route.request().url().startsWith(base) ? route.continue() : route.abort());
      const page = await context.newPage();
      for (const route of routes) {
        const response = await page.goto(base + route, { waitUntil: 'domcontentloaded' });
        assert.equal(response.status(), 200, `${route}: response`);
        const state = await page.evaluate(() => ({
          headers: document.querySelectorAll('header.gm-site-header').length,
          themeChoices: document.querySelectorAll('[data-theme-toggle]').length,
          theme: document.documentElement.dataset.theme,
          headings: document.querySelectorAll('h1').length,
          overflow: document.documentElement.scrollWidth > innerWidth,
          frames: document.querySelectorAll('iframe').length,
        }));
        assert.deepEqual(state, { headers: 1, themeChoices: 1, theme, headings: 1, overflow: false, frames: 0 }, `${route} ${width} ${theme}`);
        const toggle = page.locator('[data-theme-toggle]');
        assert.equal(await toggle.getAttribute('aria-label'), 'Light appearance');
        assert.equal(await toggle.getAttribute('aria-pressed'), String(theme === 'light'));
        if (route === '/') {
          assert.equal(await page.locator('.gm-home-card').count(), 7);
          assert.equal(await page.locator('.gm-home-player[data-source-platform="YouTube"]').count(), 7);
          assert.equal(await page.locator('.gm-home-player[data-source-platform="Instagram"]').count(), 0);
          const signal = await page.evaluate(() => ({
            flow: getComputedStyle(document.querySelector('.signal-flow')).stroke,
            face: getComputedStyle(document.querySelector('.signal-face-top')).fill,
            motion: getComputedStyle(document.querySelector('.signal-flow')).animationName,
          }));
          assert.equal(signal.motion, 'none');
          if (theme === 'light') {
            assert.equal(signal.flow, 'rgb(140, 33, 62)');
            assert.equal(signal.face, 'rgb(255, 255, 255)');
          }
          await page.locator('.gm-home-player[data-source-platform="YouTube"] button').first().click();
          const source = await page.locator('.gm-home-player iframe').first().getAttribute('src');
          assert.match(source, /^https:\/\/www\.youtube-nocookie\.com\/embed\//);
          assert(!source.includes('autoplay='));
          await page.locator('#home-query').fill('not a company policy');
          await page.locator('.gm-home-search button').click();
          await page.waitForURL(/\/readers\/\?q=not.a.company.policy/);
          assert.equal(await page.locator('#search').inputValue(), 'not a company policy');
          await page.waitForFunction(() => document.querySelectorAll('#catalog-results .gm-card:not([hidden])').length === 1);
          assert((await page.locator('#catalog-results .gm-card:visible').count()) < readerCount);
        }
        if (route === '/readers/') {
          assert.equal(await page.locator('#catalog-results .gm-card').count(), readerCount);
          const numbered = () => page.locator('#catalog-results .gm-card:visible .gm-archive-index').allTextContents();
          assert.deepEqual(await numbered(), Array.from({ length: readerCount }, (_, i) => String(i + 1).padStart(2, '0')));
          await page.locator('#search').fill('not a company policy');
          await page.waitForFunction(() => document.querySelectorAll('#catalog-results .gm-card:not([hidden])').length === 1);
          const visible = await page.locator('#catalog-results .gm-card:visible').count();
          assert(visible > 0 && visible < readerCount);
          assert.match(await page.locator('#result-count').textContent(), new RegExp(`^${visible} of ${readerCount} Readers$`));
          assert.deepEqual(await numbered(), ['01']);
          await page.locator('.gm-reset').click();
          await page.waitForFunction(expectedCount => document.querySelectorAll('#catalog-results .gm-card:not([hidden])').length === expectedCount, readerCount);
          assert.deepEqual(await numbered(), Array.from({ length: readerCount }, (_, i) => String(i + 1).padStart(2, '0')));
          await page.locator('#sort').selectOption('title');
          assert.deepEqual(await numbered(), Array.from({ length: readerCount }, (_, i) => String(i + 1).padStart(2, '0')));
          assert.equal(await page.locator('.gm-library-frame[data-home-player]').count(), readerCount);
          assert.equal(await page.locator('.gm-library-frame[data-gm-aspect="9:16"]').count(), 1);
          await page.locator('.gm-library-frame[data-source-platform="YouTube"] button').first().click();
          assert.match(await page.locator('.gm-library-frame iframe').first().getAttribute('src'), /^https:\/\/www\.youtube-nocookie\.com\/embed\//);
        }
        if (route === '/map/') {
          assert.equal(await page.locator('.gm-atlas-entry').count(), readerCount);
          assert.equal(await page.locator('.gm-atlas-link').count(), relationshipCount);
          assert.equal(await page.locator('.gm-question-list li').count(), 4);
        }
        if (route.startsWith('/ask-') || route.startsWith('/a-challenge')) {
          assert.equal(await page.locator('[data-gm-share]').count(), 1);
          assert.equal(await page.locator('.gm-reader-footer').count(), 1);
          await page.locator('[data-native-share]').click();
          const shared = await page.evaluate(() => window.__gmShared);
          assert.equal(shared.url, await page.locator('link[rel="canonical"]').getAttribute('href'));
          assert.equal(shared.text, await page.locator('meta[name="gm-share-description"]').getAttribute('content'));
        }
        if (route === '/the-engine-is-not-the-service/') {
          const before = await deepInferColors(page);
          for (const [selector, sample] of Object.entries(before.colors))
            assert(sample.contrast >= 4.5, `${route} ${width} ${theme} ${selector}: ${sample.contrast}`);
          await toggle.click();
          const after = await deepInferColors(page);
          assert.notEqual(after.body, before.body, 'DeepInfer theme toggle must change computed foreground');
          assert.notEqual(after.background, before.background, 'DeepInfer theme toggle must change computed background');
          for (const [selector, sample] of Object.entries(after.colors))
            assert(sample.contrast >= 4.5, `${route} ${width} toggled ${selector}: ${sample.contrast}`);
          await toggle.click();
        }
        cases++;
      }
      const toggle = page.locator('[data-theme-toggle]');
      await toggle.click();
      assert.equal(await toggle.getAttribute('aria-label'), 'Light appearance');
      assert.equal(await toggle.getAttribute('aria-pressed'), String(theme !== 'light'));
      assert.equal(await page.locator('html').getAttribute('data-theme'), theme === 'light' ? 'dark' : 'light');
      await context.close();
    }
    const context = await browser.newContext({ javaScriptEnabled: false, viewport: { width: 390, height: 844 } });
    await context.route('**/*', route => route.request().url().startsWith(base) ? route.continue() : route.abort());
    const page = await context.newPage();
    await page.goto(base + '/readers/', { waitUntil: 'domcontentloaded' });
    assert.equal(await page.locator('#catalog-results .gm-card').count(), readerCount);
    await page.goto(base + '/', { waitUntil: 'domcontentloaded' });
    assert.equal(await page.locator('.gm-home-open').count(), 7);
    assert.equal(await page.locator('.gm-home-source').count(), 7);
    assert.equal(await page.locator('iframe').count(), 0);
    await page.goto(base + '/map/', { waitUntil: 'domcontentloaded' });
    assert.equal(await page.locator('.gm-atlas-entry').count(), readerCount);
    assert.equal(await page.locator('.gm-atlas-link').count(), relationshipCount);
    assert.equal(await page.locator('[data-theme-toggle]:visible').count(), 0);
    console.log(JSON.stringify({ cases, noJavaScript: true, failures: [] }));
    await context.close();
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
