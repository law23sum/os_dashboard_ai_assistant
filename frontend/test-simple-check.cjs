const { chromium } = require('@playwright/test');

async function test() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  // Capture console errors
  const errors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') errors.push(msg.text());
  });
  page.on('pageerror', err => errors.push(err.message));

  console.log('Loading page...');
  await page.goto('http://localhost:5174/', { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(5000);

  console.log('Page URL:', page.url());

  const content = await page.content();
  console.log('Page content length:', content.length);

  const text = await page.evaluate(() => document.body.innerText);
  console.log('Body text:', text.substring(0, 500));

  if (errors.length > 0) {
    console.log('\nConsole errors:');
    errors.slice(0, 10).forEach(e => console.log('  -', e.substring(0, 100)));
  }

  await browser.close();
}

test().catch(console.error);
