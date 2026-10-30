const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const article = fs.readFileSync(path.join(__dirname, '../content/readers/the-model-is-not-the-demonstration.html'), 'utf8');
const match = article.match(/<script>(\(\(\)=>\{const panel=.*?\}\)\(\);)<\/script>/s);
assert.ok(match, 'Kimi opt-in player script exists');

function renderPoster({ complete, naturalWidth }) {
  const poster = {
    complete, naturalWidth, replacement: null, onError: null,
    addEventListener(event, handler) { if (event === 'error') this.onError = handler; },
    replaceWith(node) { this.replacement = node; }
  };
  const button = { hidden: true, addEventListener() {} };
  const panel = { querySelector(selector) { return selector === 'img' ? poster : null; } };
  const status = {};
  const document = {
    getElementById(id) { return { player: panel, play: button, 'player-status': status }[id]; },
    createElement(tag) { assert.equal(tag, 'p'); return {}; }
  };
  vm.runInNewContext(match[1], { document });
  assert.equal(button.hidden, false, 'opt-in control remains available');
  return poster;
}

const normal = renderPoster({ complete: true, naturalWidth: 480 });
assert.equal(normal.replacement, null, 'loaded thumbnail stays in place');
normal.onError();
assert.equal(normal.replacement.className, 'gm-home-source-fallback');
assert.equal(normal.replacement.textContent, 'Source thumbnail unavailable. Use the original source link below.');

const failedBeforeScript = renderPoster({ complete: true, naturalWidth: 0 });
assert.equal(failedBeforeScript.replacement.className, 'gm-home-source-fallback');
