const { chromium } = require('@playwright/test');

const PAGES_TO_TEST = [
  '/dashboard',
  '/projects',
  '/tasks',
  '/ai',
  '/ai/autofix',
  '/workspaces/writer',
  '/settings',
  '/billing',
  '/chat',
];

async function test() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  console.log('='.repeat(70));
  console.log('  Comprehensive GUI Test - Verifying Real Content');
  console.log('='.repeat(70));

  // Login
  console.log('\n[1/3] Logging in...');
  await page.goto('http://localhost:5173/login');
  await page.waitForTimeout(2000);

  await page.fill('input[id="username"]', 'admin');
  await page.fill('input[id="password"]', 'admin123');
  await page.click('button[type="submit"]');
  await page.waitForTimeout(3000);

  console.log('  Logged in, current URL:', page.url());

  // Test each page
  console.log('\n[2/3] Testing page content...');
  const results = [];

  for (const route of PAGES_TO_TEST) {
    try {
      await page.goto(`http://localhost:5173${route}`, { waitUntil: 'networkidle', timeout: 20000 });
      await page.waitForTimeout(2000);

      // Get text content
      const text = await page.evaluate(() => document.body.innerText);
      const textLower = text.toLowerCase();

      // Check for template indicators (BAD)
      const isTemplate = textLower.includes('auto-generated') ||
                        textLower.includes('implement the following') ||
                        textLower.includes('routescaffold');

      // Check for real content indicators (GOOD)
      const hasButtons = await page.$$eval('button', btns => btns.length);
      const hasTables = await page.$$eval('table, [role="grid"]', els => els.length);
      const hasCards = await page.$$eval('[class*="card"], [class*="Card"]', els => els.length);
      const hasInputs = await page.$$eval('input, textarea, select', els => els.length);

      // Content analysis
      const contentLen = text.length;
      const isLogin = textLower.includes('sign in to your account');

      let status = 'UNKNOWN';
      if (isLogin) status = 'LOGIN';
      else if (isTemplate) status = 'TEMPLATE';
      else if (contentLen > 500 && (hasButtons > 2 || hasTables > 0 || hasCards > 0)) status = 'REAL';
      else if (contentLen > 300) status = 'PARTIAL';
      else status = 'EMPTY';

      results.push({
        route,
        status,
        contentLen,
        buttons: hasButtons,
        tables: hasTables,
        cards: hasCards,
        inputs: hasInputs
      });

      const icon = status === 'REAL' ? '✓' : status === 'PARTIAL' ? '~' : '✗';
      console.log(`  ${icon} ${route.padEnd(25)} ${status.padEnd(10)} (${contentLen} chars, ${hasButtons} btns, ${hasTables} tables)`);

      // Show content preview for real pages
      if (status === 'REAL' && contentLen > 0) {
        const preview = text.replace(/\s+/g, ' ').substring(0, 100);
        console.log(`     Preview: ${preview}...`);
      }
    } catch (e) {
      results.push({ route, status: 'ERROR', error: e.message });
      console.log(`  ✗ ${route.padEnd(25)} ERROR: ${e.message.substring(0, 40)}`);
    }
  }

  // Summary
  console.log('\n[3/3] Summary');
  console.log('='.repeat(70));
  const real = results.filter(r => r.status === 'REAL').length;
  const partial = results.filter(r => r.status === 'PARTIAL').length;
  const template = results.filter(r => r.status === 'TEMPLATE').length;
  const login = results.filter(r => r.status === 'LOGIN').length;
  const errors = results.filter(r => r.status === 'ERROR').length;

  console.log(`  REAL: ${real} | PARTIAL: ${partial} | TEMPLATE: ${template} | LOGIN: ${login} | ERROR: ${errors}`);
  console.log('='.repeat(70));

  await browser.close();
  return results;
}

test()
  .then(r => {
    const real = r.filter(x => x.status === 'REAL').length;
    process.exit(real > 0 ? 0 : 1);
  })
  .catch(e => { console.error(e); process.exit(1); });
