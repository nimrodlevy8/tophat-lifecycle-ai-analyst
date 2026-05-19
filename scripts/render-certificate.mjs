#!/usr/bin/env node

/**
 * Render certificate.html to a crisp PNG for Marp deck insertion.
 *
 * Usage:
 *   node scripts/render-certificate.mjs [input.html] [output.png]
 *
 * Defaults:
 *   input:  certificate.html (in current directory)
 *   output: certificate.png  (in current directory)
 *
 * Renders at 1920x1080 (16:9) with 2x device scale = 3840x2160 output.
 * Requires puppeteer (auto-installed via npx if not present).
 */

import { resolve } from 'path';

const input = resolve(process.argv[2] || 'certificate.html');
const output = resolve(process.argv[3] || 'certificate.png');

async function render() {
  let puppeteer;
  try {
    puppeteer = await import('puppeteer');
  } catch {
    console.log('Installing puppeteer (first time only)...');
    const { execSync } = await import('child_process');
    execSync('npm install puppeteer', { stdio: 'inherit' });
    puppeteer = await import('puppeteer');
  }

  const browser = await puppeteer.default.launch({ headless: 'new' });
  const page = await browser.newPage();

  // 16:9 at 2x device scale for crisp retina output (renders 3840x2160)
  await page.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 2 });

  // Wait for fonts to load (Google Fonts)
  await page.goto(`file://${input}`, { waitUntil: 'networkidle0', timeout: 15000 });

  // Extra wait for font rendering
  await new Promise(r => setTimeout(r, 1000));

  await page.screenshot({ path: output, type: 'png' });
  await browser.close();

  console.log(`\n  Certificate saved: ${output}`);
  console.log(`  Dimensions: 3840x2160 (2x retina of 1920x1080)\n`);
}

render().catch(err => {
  console.error('Render failed:', err.message);
  process.exit(1);
});
