const { chromium } = require('playwright');
const assert = require('node:assert/strict');

const base = 'http://127.0.0.1:8765';
const readerCount = require('../content/catalog.json').readers.length;
(async () => {
  const browser = await chromium.launch({ headless: true, channel: 'chrome' });
  let cases = 0;
  try {
    for (const width of [390, 1440]) for (const theme of ['light', 'dark']) {
      const context = await browser.newContext({ viewport: { width, height: 900 } });
      await context.addInitScript(value => localStorage.setItem('gm-appearance', value), theme);
      await context.route('**/*', route => route.request().url().startsWith(base) ? route.continue() : route.abort());
      const page = await context.newPage();
      await page.goto(base + '/', { waitUntil: 'domcontentloaded' });
      const header = page.locator('.gm-site-header');
      const box = await header.boundingBox();
      assert(box.height <= (width === 390 ? 100 : 70), `header size ${width} ${theme}: ${box.height}`);
      await page.locator('#home-query').fill('not a company policy');
      await page.waitForFunction(() => document.querySelector('.gm-home-live')?.textContent.includes('1 Reader article match as you type'));
      assert.equal(await page.locator('.gm-home-live > a').count(), 1);
      assert.equal(await page.locator('.gm-home-live > a').getAttribute('href'), '/ask-for-the-outcome-keep-the-boundary/');
      assert.match(await page.locator('.gm-search-control').getAttribute('aria-label'), /^Search Reader articles; without JavaScript, browse the Reader archive$/);
      await page.locator('.gm-search-control').click();
      assert.equal(await page.locator('[data-reader-search]').getAttribute('open'), '');
      await page.locator('#gm-search-input').fill('not a company policy');
      await page.waitForFunction(expectedCount => document.querySelector('[data-reader-search-status]')?.textContent.includes(`1 of ${expectedCount}`), readerCount);
      const result = page.locator('[data-reader-search-results] > a');
      assert.equal(await result.count(), 1);
      assert.equal(await result.getAttribute('href'), '/ask-for-the-outcome-keep-the-boundary/');
      assert.match(await result.textContent(), /not a company policy/i);
      await page.locator('#gm-search-input').fill('false positives and useful work lost');
      await page.waitForFunction(expectedCount => document.querySelector('[data-reader-search-status]')?.textContent.includes(`1 of ${expectedCount}`), readerCount);
      assert.equal(await result.getAttribute('href'), '/the-fleet-does-not-prove-the-forecast/');
      await page.locator('#gm-search-input').press('ArrowDown');
      assert.equal(await result.evaluate(el => el === document.activeElement), true);
      await page.keyboard.press('Escape');
      assert.equal(await page.locator('[data-reader-search]').getAttribute('open'), null);
      assert.equal(await page.locator('.gm-search-control').evaluate(el => el === document.activeElement), true);
      await page.locator('.gm-search-control').click();
      await page.locator('#gm-search-input').fill('not-a-real-reader-phrase-xyz');
      await page.waitForFunction(() => document.querySelector('[data-reader-search-status]')?.textContent.startsWith('No Reader articles match'));
      assert.equal(await page.locator('[data-reader-search-results] > a').count(), 0);
      await page.locator('[data-reader-search-close]').click();

      await page.goto(base + '/readers/', { waitUntil: 'domcontentloaded' });
      await page.locator('#search').fill('not a company policy');
      await page.waitForFunction(() => document.querySelectorAll('#catalog-results .gm-card:not([hidden])').length === 1);
      assert.equal(await page.locator('#catalog-results .gm-card:visible h3').textContent(), 'Ask for the Outcome. Keep the Boundary');
      assert.match(await page.locator('#catalog-results .gm-library-match-snippet:visible').textContent(), /not a company policy/i);
      await page.locator('#search').fill('false positives and useful work lost');
      await page.waitForFunction(() => document.querySelectorAll('#catalog-results .gm-card:not([hidden])').length === 1);
      assert.equal(await page.locator('#catalog-results .gm-card:visible h3').textContent(), 'The Fleet Does Not Prove the Forecast');
      assert.match(await page.locator('#catalog-results .gm-library-match-snippet:visible').textContent(), /false positives and useful work lost/i);
      await page.locator('#search').fill('not-a-real-reader-phrase-xyz');
      assert.match(await page.locator('#result-count').textContent(), /^No Readers match/);
      cases++;
      await context.close();
    }
    const slow = await browser.newContext();
    await slow.route('**/readers/search-index.json', async route => {
      await new Promise(resolve => setTimeout(resolve, 1000));
      await route.continue();
    });
    const slowPage = await slow.newPage();
    await slowPage.goto(base + '/', { waitUntil: 'domcontentloaded' });
    await slowPage.locator('.gm-search-control').click();
    await slowPage.locator('#gm-search-input').fill('not');
    await slowPage.locator('#gm-search-input').fill('not a company policy');
    await slowPage.waitForFunction(expectedCount => document.querySelector('[data-reader-search-status]')?.textContent.includes(`1 of ${expectedCount}`), readerCount);
    assert.equal(await slowPage.locator('[data-reader-search-results] > a').count(), 1);
    assert.equal(await slowPage.locator('[data-reader-search-results] > a').getAttribute('href'),
      '/ask-for-the-outcome-keep-the-boundary/');
    await slow.close();

    const missing = await browser.newContext();
    await missing.route('**/readers/search-index.json', route => route.abort());
    const missingPage = await missing.newPage();
    await missingPage.goto(base + '/readers/', { waitUntil: 'domcontentloaded' });
    await missingPage.waitForFunction(() => document.querySelector('#result-count')?.textContent.includes('Article-text search is unavailable'));
    await missingPage.locator('#search').fill('not a company policy');
    assert.match(await missingPage.locator('#result-count').textContent(), /Article-text search is unavailable/);
    await missing.close();

    const context = await browser.newContext({ javaScriptEnabled: false });
    const page = await context.newPage();
    await page.goto(base + '/', { waitUntil: 'domcontentloaded' });
    assert.equal(await page.locator('.gm-search-control').getAttribute('href'), '/readers/#search');
    assert.match(await page.locator('.gm-search-control').getAttribute('aria-label'), /without JavaScript, browse the Reader archive/);
    await page.locator('.gm-search-control').click();
    assert.match(page.url(), /\/readers\/#search$/);
    assert.equal(await page.locator('#catalog-results .gm-card').count(), readerCount);
    await context.close();
    const index = await (await fetch(base + '/readers/search-index.json')).json();
    assert.equal(index.readers.length, readerCount);
    assert(index.readers.every(article => article.text.length > 100));
    assert(index.readers.some(article => article.text.includes('not a company policy')));
    console.log(JSON.stringify({ cases, delayedIndexRace: true, unavailableIndexFallback: true,
      noJavaScriptFallback: true, indexedReaderArticles: readerCount }));
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
