// Renders the Bucksley app icon ("Stacks", Afterhours) to the site's PNG icons.
// Run from the repository root: node tools/render-icons.js [out-dir-for-sibling-icons]
// mark.svg is the master drawing; tools/mark-small.svg is the pixel-fitted drawing for small sizes.
// Writes assets/icon.png (512, with a soft shadow), favicon.png (64, small drawing) and
// assets/apple-touch-icon.png (180, full-bleed square; iOS rounds it). With an out dir it also
// writes bucksley-96.png and bucksley-144.png for the More from Project ATOM blocks and protomota.com
// (convert the 96 to WebP with cwebp).
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
const root = path.resolve(__dirname, '..');
const master = fs.readFileSync(path.join(root, 'mark.svg'), 'utf8');
const small = fs.readFileSync(path.join(__dirname, 'mark-small.svg'), 'utf8');
const sized = (svg) => svg.replace('<svg ', '<svg style="display:block;width:100%;height:100%" ');
const rounded = (svg, size) => `<html><body style="margin:0;background:transparent">
  <div style="width:${size}px;height:${size}px;display:grid;place-items:center">
    <div style="width:${size * 0.92}px;height:${size * 0.92}px;border-radius:${size * 0.92 * 0.225}px;box-shadow:0 ${size * 0.01}px ${size * 0.03}px rgba(13,14,23,.32)">
      ${sized(svg)}
    </div></div></body></html>`;
// Full-bleed square for iOS: drop the rounded corners and the edge line.
const squareSvg = master.replace(/<rect width="1024" height="1024" rx="[\d.]+"/, '<rect width="1024" height="1024"').replace(/<rect x="2" y="2"[^>]*\/>/, '');
const square = (size) => `<html><body style="margin:0">${squareSvg.replace('<svg ', `<svg style="display:block;width:${size}px;height:${size}px" `)}</body></html>`;
(async () => {
  const browser = await chromium.launch(process.env.PW_CHROME ? { executablePath: process.env.PW_CHROME } : {});
  const shot = async (html, size, file) => {
    const page = await browser.newPage({ viewport: { width: size, height: size } });
    await page.setContent(html);
    await page.screenshot({ path: file, omitBackground: true });
    await page.close();
  };
  await shot(rounded(master, 512), 512, path.join(root, 'assets/icon.png'));
  await shot(rounded(small, 64), 64, path.join(root, 'favicon.png'));
  await shot(square(180), 180, path.join(root, 'assets/apple-touch-icon.png'));
  const out = process.argv[2];
  if (out) {
    await shot(rounded(master, 96), 96, path.join(out, 'bucksley-96.png'));
    await shot(rounded(master, 144), 144, path.join(out, 'bucksley-144.png'));
  }
  await browser.close();
})();
