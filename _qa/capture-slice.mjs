import { mkdir } from 'node:fs/promises';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const port = process.env.GAME_PORT ?? '5245';
const out = new URL('./ui/slice/', import.meta.url).pathname;
await mkdir(out, { recursive: true });
const browser = await chromium.launch({ headless: true });

async function run(viewport, locale, name) {
  const context = await browser.newContext({ viewport, deviceScaleFactor: 1 });
  await context.addInitScript((value) => localStorage.setItem('game_locale', value), locale);
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', (error) => errors.push(`pageerror: ${error.message}`));
  page.on('console', (message) => { if (message.type() === 'error') errors.push(`console: ${message.text()}`); });
  await page.goto(`http://127.0.0.1:${port}/`, { waitUntil: 'networkidle' });
  await page.addStyleTag({ content: '#alteru-guest-banner{display:none!important}' });
  await page.screenshot({ path: `${out}/platform-layout-entry-${name}.png`, fullPage: true });
  await page.locator('.uvq-hotspot').first().click();
  await page.waitForTimeout(2600);
  await page.screenshot({ path: `${out}/platform-layout-video-${name}.png`, fullPage: true });
  const metrics = await page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
    scrollHeight: document.documentElement.scrollHeight,
    clientHeight: document.documentElement.clientHeight,
    buttons: [...document.querySelectorAll('button')].map((button) => {
      const rect = button.getBoundingClientRect();
      return { label: button.getAttribute('aria-label') ?? button.textContent?.trim(), width: rect.width, height: rect.height };
    }),
  }));
  await context.close();
  return { errors, metrics };
}

const primary = await run({ width: 390, height: 844 }, 'zh', '390x844');
const narrow = await run({ width: 320, height: 568 }, 'en', '320x568');
console.log(JSON.stringify({ primary, narrow }, null, 2));
await browser.close();
