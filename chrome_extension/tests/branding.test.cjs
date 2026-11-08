const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.join(__dirname, '..');
const read = name => fs.readFileSync(path.join(root, name), 'utf8');
const manifest = JSON.parse(read('manifest.json'));

test('extension and side panel use the exact requested display name', () => {
  assert.equal(manifest.name, 'dobby’s catch');
  assert.equal(manifest.version, '0.3.4');
  assert.equal(manifest.action.default_title, 'Open dobby’s catch');
  assert.match(read('sidepanel.html'), /<title>dobby’s catch<\/title>/);
  assert.match(read('sidepanel.html'), /<strong>dobby’s catch<\/strong>/);
  for (const file of ['sidepanel.html', 'sidepanel.js', 'background.js', 'content.js']) {
    assert.doesNotMatch(read(file), /Hookline/);
  }
});

test('toolbar and extension list package all four valid PNG icon sizes', () => {
  const sizes = [16, 32, 48, 128];
  assert.deepEqual(Object.keys(manifest.icons), sizes.map(String));
  assert.deepEqual(manifest.action.default_icon, manifest.icons);
  for (const size of sizes) {
    assert.equal(manifest.icons[size], `icons/icon-${size}.png`);
    const png = fs.readFileSync(path.join(root, manifest.icons[size]));
    assert.deepEqual(png.subarray(0, 8), Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]));
    assert.equal(png.toString('ascii', 12, 16), 'IHDR');
    assert.equal(png.readUInt32BE(16), size);
    assert.equal(png.readUInt32BE(20), size);
  }
});

test('header displays the packaged artwork rather than the former hook emoji', () => {
  const html = read('sidepanel.html');
  const brand = html.match(/<div class="brand">(.*?)<\/div>/)[1];
  assert.match(brand, /<img class="brand-icon" src="icons\/icon-128\.png"/);
  assert.match(brand, /alt="" aria-hidden="true"/);
  assert.doesNotMatch(brand, /🪝/);
});

test('branding keeps the existing permissions and session-storage identity', () => {
  assert.deepEqual(manifest.permissions, ['sidePanel', 'storage']);
  assert.deepEqual(manifest.host_permissions, ['https://mail.google.com/*', 'http://127.0.0.1/*']);
  assert.equal(manifest.background.service_worker, 'background.js');
  assert.equal(manifest.side_panel.default_path, 'sidepanel.html');
  assert.match(read('background.js'), /const SESSION_KEY = "hooklineConnection";/);
  assert.match(read('content.js'), /const HIGHLIGHT_NAME = "hookline-evidence";/);
});
