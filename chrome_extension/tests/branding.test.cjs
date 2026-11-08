const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.join(__dirname, '..');
const read = name => fs.readFileSync(path.join(root, name), 'utf8');
const manifest = JSON.parse(read('manifest.json'));

test('extension and side panel use the exact requested display name', () => {
  assert.equal(manifest.name, 'Dobby’s Catch');
  assert.equal(manifest.version, '0.3.4');
  assert.equal(manifest.action.default_title, 'Open Dobby’s Catch');
  assert.match(read('sidepanel.html'), /<title>Dobby’s Catch<\/title>/);
  assert.match(read('sidepanel.html'), /<strong>Dobby’s Catch<\/strong>/);
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


test('Selected email and Suspicious titles stay outside the hidden home view and connection is last', () => {
  const html = read('sidepanel.html');
  const home = html.slice(html.indexOf('<div id="home-view">'), html.indexOf('<div class="section-label">Selected email</div>'));
  assert.match(home, /<\/div>\s*<section class="panel">\s*$/);
  const selected = html.indexOf('<div class="section-label">Selected email</div>');
  const titles = html.indexOf('aria-labelledby="inbox-heading"');
  const results = html.indexOf('<div id="result-context"');
  const connection = html.indexOf('<details id="connection-settings">');
  assert.ok(selected < titles && titles < results && results < connection);
  assert.doesNotMatch(html.slice(connection), /<section/);
});
