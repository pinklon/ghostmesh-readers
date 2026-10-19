// Optional Chrome render gate for the shared Reader source player. No media is downloaded.
const { chromium } = require('playwright');
const { readFileSync } = require('fs');
const assert = require('node:assert/strict');

const base = 'http://127.0.0.1:8765';
const readers = JSON.parse(readFileSync('content/catalog.json')).readers;
const ratios = { '16:9': 16 / 9, '9:16': 9 / 16, '1:1': 1 };

async function main() {
  const browser = await chromium.launch({ headless: true, channel: 'chrome' });
  const results = [];
  try {
    for (const width of [1440, 390]) {
      const context = await browser.newContext({ viewport: { width, height: width === 390 ? 844 : 900 }, reducedMotion: 'reduce' });
      await context.route('**/*', route => route.request().url().startsWith(base) ? route.continue() : route.abort());
      const page = await context.newPage();
      for (const reader of readers) {
        const response = await page.goto(`${base}/${reader.slug}/`, { waitUntil: 'domcontentloaded' });
        assert.equal(response.status(), 200, `${reader.slug}: route`);
        const frame = page.locator('.gm-media-frame');
        assert.equal(await frame.count(), 1, `${reader.slug}: one shared frame`);
        const before = await frame.evaluate(el => {
          const rect = el.getBoundingClientRect(), parent = el.parentElement.getBoundingClientRect();
          return { aspect: el.dataset.gmAspect, width: rect.width, height: rect.height,
            leftGap: rect.left - parent.left, rightGap: parent.right - rect.right,
            scrollWidth: document.documentElement.scrollWidth, viewportWidth: innerWidth,
            activeFrames: [...document.querySelectorAll('iframe')].filter(f => f.src.startsWith('https://')).length };
        });
        assert.equal(before.aspect, reader.source.mediaAspect, `${reader.slug}: source declaration`);
        assert(Math.abs(before.width / before.height - ratios[before.aspect]) < .015, `${reader.slug}: aspect ratio at ${width}px`);
        assert(before.scrollWidth <= before.viewportWidth + 1, `${reader.slug}: horizontal overflow at ${width}px`);
        assert.equal(before.activeFrames, 0, `${reader.slug}: premature third-party embed`);
        if (before.aspect === '16:9') assert(before.width >= (width === 1440 ? 1000 : 300), `${reader.slug}: squeezed landscape player`);
        if (before.aspect === '9:16') {
          assert(before.width <= 520, `${reader.slug}: oversized portrait player`);
          assert(Math.abs(before.leftGap - before.rightGap) < 2, `${reader.slug}: portrait player not centered`);
        }
        const fallback = await page.evaluate(url => [...document.querySelectorAll('a[href]')].some(a => a.href === url), reader.source.url);
        assert(fallback, `${reader.slug}: missing external source fallback`);
        const play = page.locator('#play,#play-cover,#play-source,#play-reel,#play-video').first();
        assert.equal(await play.count(), 1, `${reader.slug}: missing opt-in play control`);
        await play.click();
        const embedded = frame.locator('iframe[src^="https://"]');
        assert.equal(await embedded.count(), 1, `${reader.slug}: embed did not load on click`);
        const after = await embedded.evaluate(el => {
          const a = el.getBoundingClientRect();
          return { width: a.width, height: a.height };
        });
        assert(Math.abs(after.width / after.height - ratios[before.aspect]) < .015, `${reader.slug}: embedded frame distorted`);
        results.push({ slug: reader.slug, viewport: width, aspect: before.aspect,
          frame: [Math.round(before.width), Math.round(before.height)], optIn: true, fallback: true });
      }
      await page.goto(`${base}/`, { waitUntil: 'domcontentloaded' });
      const motion = await page.locator('.signal-flow').evaluate(el => getComputedStyle(el).animationName);
      assert.equal(motion, 'none', 'reduced motion must disable the homepage signal animation');
      await page.evaluate(() => {
        const container = document.createElement('div');
        container.id = 'aspect-fixtures';
        container.style.cssText = 'width:min(900px,calc(100vw - 40px));margin:0 auto';
        container.innerHTML = ['16:9','9:16','1:1'].map(aspect =>
          `<div class="gm-media-frame" data-gm-aspect="${aspect}"></div>`).join('');
        document.body.append(container);
      });
      const fixtures = await page.locator('#aspect-fixtures .gm-media-frame').evaluateAll(els => els.map(el => {
        const a = el.getBoundingClientRect();
        return { aspect: el.dataset.gmAspect, width: a.width, height: a.height };
      }));
      for (const fixture of fixtures) {
        assert(Math.abs(fixture.width / fixture.height - ratios[fixture.aspect]) < .015,
          `${fixture.aspect} synthetic fixture at ${width}px`);
      }
      await context.close();
    }
    const noJs = await browser.newContext({ viewport: { width: 390, height: 844 }, javaScriptEnabled: false });
    await noJs.route('**/*', route => route.request().url().startsWith(base) ? route.continue() : route.abort());
    const noJsPage = await noJs.newPage();
    for (const reader of readers) {
      await noJsPage.goto(`${base}/${reader.slug}/`, { waitUntil: 'domcontentloaded' });
      const fallback = await noJsPage.evaluate(url => [...document.querySelectorAll('a[href]')].some(a => a.href === url), reader.source.url);
      assert(fallback, `${reader.slug}: no-JavaScript external source fallback`);
      assert.equal(await noJsPage.locator('iframe[src^="https://"]').count(), 0,
        `${reader.slug}: no-JavaScript page preloaded third-party media`);
    }
    await noJs.close();
  } finally { await browser.close(); }
  console.log(JSON.stringify({ readerCases: results.length, syntheticAspectCases: 6,
    reducedMotionCases: 2, noJavaScriptSourceCases: readers.length, failures: [], results }, null, 2));
}
main().catch(error => { console.error(error); process.exitCode = 1; });
