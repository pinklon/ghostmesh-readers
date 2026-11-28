const { chromium } = require('playwright');
const assert = require('node:assert/strict');

const base = 'http://127.0.0.1:8765';
const readerCount = require('../content/catalog.json').readers.length;
(async () => {
  const browser = await chromium.launch({ headless: true, channel: 'chrome' });
  let cases = 0;
  try {
    for (const width of [390, 768, 1440]) for (const theme of ['light', 'dark']) {
      const context = await browser.newContext({ viewport: { width, height: 900 } });
      await context.addInitScript(value => localStorage.setItem('gm-appearance', value), theme);
      await context.route('**/*', route => route.request().url().startsWith(base) ? route.continue() : route.abort());
      await context.route('**/readers/unified-search-index.json', route => route.abort());
      const page = await context.newPage();
      await page.goto(base + '/', { waitUntil: 'domcontentloaded' });
      const header = page.locator('.gm-site-header');
      const box = await header.boundingBox();
      // Current main's responsive header is 113px at 390, 111.8px at 768, and 65px at 1440.
      assert(box.height <= (width <= 768 ? 115 : 70), `header size ${width} ${theme}: ${box.height}`);
      await page.locator('#home-query').fill('not a company policy');
      await page.waitForFunction(() => document.querySelector('.gm-home-live')?.textContent.includes('1 match'));
      assert.equal(await page.locator('.gm-home-live .gm-cross-inventory').textContent(), readerCount+' GhostMesh Readers · SharePlane search unavailable');
      assert.equal(await page.locator('.gm-home-live > a').count(), 1);
      assert.equal(await page.locator('.gm-home-live > a').getAttribute('href'), '/ask-for-the-outcome-keep-the-boundary/');
      assert.match(await page.locator('.gm-search-control').getAttribute('aria-label'), /^Search Reader articles; without JavaScript, browse the Reader archive$/);
      await page.locator('.gm-search-control').click();
      assert.equal(await page.locator('[data-reader-search]').getAttribute('open'), '');
      await page.locator('#gm-search-input').fill('not a company policy');
      await page.waitForFunction(() => document.querySelector('[data-reader-search-status]')?.textContent === '1 match');
      assert.equal(await page.locator('[data-reader-search] .gm-cross-inventory').textContent(), readerCount+' GhostMesh Readers · SharePlane search unavailable');
      const result = page.locator('[data-reader-search-results] > a');
      assert.equal(await result.count(), 1);
      assert.equal(await result.getAttribute('href'), '/ask-for-the-outcome-keep-the-boundary/');
      assert.match(await result.textContent(), /not a company policy/i);
      await page.locator('#gm-search-input').fill('false positives and useful work lost');
      await page.waitForFunction(() => document.querySelector('[data-reader-search-status]')?.textContent === '1 match');
      assert.equal(await page.locator('[data-reader-search] .gm-cross-inventory').textContent(), readerCount+' GhostMesh Readers · SharePlane search unavailable');
      assert.equal(await result.getAttribute('href'), '/the-fleet-does-not-prove-the-forecast/');
      await page.locator('#gm-search-input').press('ArrowDown');
      assert.equal(await result.evaluate(el => el === document.activeElement), true);
      await page.keyboard.press('Escape');
      assert.equal(await page.locator('[data-reader-search]').getAttribute('open'), null);
      assert.equal(await page.locator('.gm-search-control').evaluate(el => el === document.activeElement), true);
      await page.locator('.gm-search-control').click();
      await page.locator('#gm-search-input').fill('not-a-real-reader-phrase-xyz');
      await page.waitForFunction(() => document.querySelector('[data-reader-search-status]')?.textContent === '0 matches');
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
    await slow.route('**/readers/unified-search-index.json', route => route.abort());
    await slow.route('**/readers/search-index.json', async route => {
      await new Promise(resolve => setTimeout(resolve, 1000));
      await route.continue();
    });
    const slowPage = await slow.newPage();
    await slowPage.goto(base + '/', { waitUntil: 'domcontentloaded' });
    await slowPage.locator('.gm-search-control').click();
    await slowPage.locator('#gm-search-input').fill('not');
    await slowPage.locator('#gm-search-input').fill('not a company policy');
    await slowPage.waitForFunction(() => document.querySelector('[data-reader-search-status]')?.textContent === '1 match');
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

    // Synthetic mixed-site fixture exercises UI behavior without publishing a stale cross-site snapshot.
    for (const width of [390, 768, 1440]) {
      const mixed = await browser.newContext({ viewport: { width, height: 900 } });
      const fixture = {
        schema: 'ghostmesh-unified-search-v1',
        sources: { Readers: { count: 1 }, SharePlane: { count: 1, sourceCatalogSha256: 'a'.repeat(64) } },
        records: [
          { id: 'reader:fixture', source: 'Readers', title: 'Reader signal lantern',
            url: 'https://youtube.shareplane.malott.ai/reader-fixture/', category: 'AI', text: 'signal-lantern Reader source context. '.repeat(4) },
          { id: 'work:fixture', source: 'SharePlane', title: 'Work signal lantern',
            url: 'https://shareplane.malott.ai/artifacts/work-fixture/', category: 'Artifact', text: 'signal-lantern SharePlane source context.' }
        ]
      };
      await mixed.route('**/readers/search-index.json', route => route.fulfill({
        status: 200, contentType: 'application/json', body: JSON.stringify({
          schema: 'ghostmesh-public-reader-text-v1', readerCount: 1,
          readers: [{...fixture.records[0], url: '/reader-fixture/'}]
        })
      }));
      await mixed.route('**/readers/unified-search-index.json', route => route.fulfill({
        status: 200, contentType: 'application/json', body: JSON.stringify(fixture)
      }));
      const mixedPage = await mixed.newPage();
      await mixedPage.goto(base + '/', { waitUntil: 'domcontentloaded' });
      await mixedPage.locator('.gm-search-control').click();
      await mixedPage.locator('#gm-search-input').fill('signal-lantern');
      await mixedPage.waitForFunction(() => document.querySelector('[data-reader-search-status]')?.textContent === '2 matches');
      assert.equal(await mixedPage.locator('[data-reader-search] .gm-cross-inventory').textContent(), '2 publications · 1 SharePlane Works · 1 GhostMesh Readers');
      assert.equal(await mixedPage.locator('[data-reader-search-results] > a').count(), 2);
      assert.equal(await mixedPage.locator('.gm-search-source-filters button').count(), 3);
      assert.equal(await mixedPage.locator('[data-reader-search-results] > a[href="https://shareplane.malott.ai/artifacts/work-fixture/"]').count(), 1);
      assert.equal(await mixedPage.locator('[data-reader-search-results] > a[href="https://youtube.shareplane.malott.ai/reader-fixture/"]').count(), 1);
      await mixedPage.locator('.gm-search-source-filters button[data-source="SharePlane"]').click();
      await mixedPage.waitForFunction(() => document.querySelector('[data-reader-search-status]')?.textContent === '1 match');
      assert.equal(await mixedPage.locator('[data-reader-search] .gm-cross-inventory').textContent(), '2 publications · 1 SharePlane Works · 1 GhostMesh Readers');
      assert.equal(await mixedPage.locator('[data-reader-search-results] > a').count(), 1);
      assert.equal(await mixedPage.locator('[data-reader-search-results] > a').getAttribute('href'),
        'https://shareplane.malott.ai/artifacts/work-fixture/');
      assert.equal(await mixedPage.locator('.gm-search-source-filters button[data-source="SharePlane"]').getAttribute('aria-pressed'), 'true');
      await mixedPage.locator('.gm-search-source-filters button[data-source="Readers"]').click();
      await mixedPage.waitForFunction(() => document.querySelector('[data-reader-search-results] a')?.getAttribute('href') === 'https://youtube.shareplane.malott.ai/reader-fixture/');
      assert.equal(await mixedPage.locator('[data-reader-search-results] > a').count(), 1);
      assert.equal(await mixedPage.locator('[data-reader-search-results] > a').getAttribute('href'),
        'https://youtube.shareplane.malott.ai/reader-fixture/');
      await mixedPage.locator('.gm-search-source-filters button[data-source="All"]').click();
      await mixedPage.waitForFunction(() => document.querySelector('[data-reader-search-status]')?.textContent === '2 matches');
      assert.equal(await mixedPage.locator('[data-reader-search-results] > a').count(), 2);
      assert.equal(await mixedPage.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
      await mixed.close();
    }

    // A stale Reader slice must not be presented as unified coverage.
    const stale = await browser.newContext();
    await stale.route('**/readers/unified-search-index.json', route => route.fulfill({
      status: 200, contentType: 'application/json', body: JSON.stringify({
        schema: 'ghostmesh-unified-search-v1',
        sources: { Readers: { count: 1 }, SharePlane: { count: 1, sourceCatalogSha256: 'a'.repeat(64) } },
        records: [
          {id:'reader:old', source:'Readers', title:'Old', url:'https://youtube.shareplane.malott.ai/old/', text:'old reader content'},
          {id:'artifact:old', source:'SharePlane', title:'Old Work', url:'https://shareplane.malott.ai/artifacts/old/', text:'old work content'}
        ]
      })
    }));
    const stalePage = await stale.newPage();
    await stalePage.goto(base + '/');
    await stalePage.locator('.gm-search-control').click();
    await stalePage.waitForFunction(count => document.querySelector('.gm-cross-inventory')?.textContent === count+' GhostMesh Readers · SharePlane search unavailable', readerCount);
    await stale.close();

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
