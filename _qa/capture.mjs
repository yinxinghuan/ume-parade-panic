import { mkdir } from 'node:fs/promises';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const port = process.env.GAME_PORT ?? '5245';
const out = new URL('./ui/recheck/', import.meta.url).pathname;
await mkdir(out, { recursive: true });
const browser = await chromium.launch({ headless: true });

async function platformRun() {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
  await context.addInitScript(() => localStorage.setItem('game_locale', 'zh'));
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', (error) => errors.push(`pageerror: ${error.message}`));
  page.on('console', (message) => { if (message.type() === 'error') errors.push(`console: ${message.text()}`); });
  await page.goto(`http://127.0.0.1:${port}/`, { waitUntil: 'networkidle' });
  await page.addStyleTag({ content: '#alteru-guest-banner{display:none!important}' });
  await page.screenshot({ path: `${out}/platform-layout-entry-390x844.png`, fullPage: true });
  const names = ['melon', 'lemon', 'guac', 'mango', 'pearl'];
  for (let index = 0; index < names.length; index += 1) {
    await page.locator('.uvq-hotspot').nth(index).click();
    await page.waitForTimeout(2500);
    await page.screenshot({ path: `${out}/platform-layout-video-${names[index]}-390x844.png`, fullPage: true });
    if (index < names.length - 1) {
      await page.locator('.uvq-hotspot').first().waitFor({ state: 'visible', timeout: 10000 });
    }
  }
  await page.locator('.uvq-climax').waitFor({ state: 'visible', timeout: 10000 });
  await page.screenshot({ path: `${out}/platform-layout-climax-ready-390x844.png`, fullPage: true });
  await page.locator('.uvq-climax button').click();
  await page.waitForTimeout(3200);
  await page.screenshot({ path: `${out}/platform-layout-climax-video-390x844.png`, fullPage: true });
  await page.locator('.uvq-result').waitFor({ state: 'visible', timeout: 12000 });
  await page.waitForTimeout(650);
  await page.screenshot({ path: `${out}/platform-layout-result-390x844.png`, fullPage: true });
  const finalMetrics = await page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
    scrollHeight: document.documentElement.scrollHeight,
    clientHeight: document.documentElement.clientHeight,
  }));
  await context.close();
  return { errors, finalMetrics };
}

async function narrowRun() {
  const context = await browser.newContext({ viewport: { width: 320, height: 568 }, deviceScaleFactor: 1 });
  await context.addInitScript(() => localStorage.setItem('game_locale', 'en'));
  const page = await context.newPage();
  await page.goto(`http://127.0.0.1:${port}/`, { waitUntil: 'networkidle' });
  await page.addStyleTag({ content: '#alteru-guest-banner{display:none!important}' });
  await page.screenshot({ path: `${out}/platform-layout-entry-en-320x568.png`, fullPage: true });
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
  return metrics;
}

async function externalRun() {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
  const page = await context.newPage();
  await page.goto(`http://127.0.0.1:${port}/`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1500);
  const banner = await page.locator('#alteru-guest-banner').count();
  await page.screenshot({ path: `${out}/external-guest-entry-390x844.png`, fullPage: true });
  await context.close();
  return { banner };
}

const platform = await platformRun();
const narrow = await narrowRun();
const external = await externalRun();
console.log(JSON.stringify({ platform, narrow, external }, null, 2));
await browser.close();
