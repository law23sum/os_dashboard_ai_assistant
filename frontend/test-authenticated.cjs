const { chromium } = require('@playwright/test');

const TEST_PAGES = [
  { route: '/projects', keywords: ['project', 'task', 'create'] },
  { route: '/tasks', keywords: ['task', 'priority', 'status'] },
  { route: '/dashboard', keywords: ['dashboard', 'overview'] },
  { route: '/ai/autofix', keywords: ['auto', 'fix'] },
  { route: '/workspaces/writer', keywords: ['writer', 'document'] },
];

async function test() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  console.log('='.repeat(70));
  console.log('  Testing Integrated SaaS with Authentication');
  console.log('='.repeat(70));

  // Login
  console.log('\n[1/3] Logging in...');
  await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);

  try {
    await page.fill('input[id="username"]', 'admin');
    await page.fill('input[id="password"]', 'admin123');
    await page.click('button[type="submit"]');

    // Wait for navigation after login
    await page.waitForTimeout(3000);

    const url = page.url();
    if (url.includes('/login')) {
      console.log('  Login may have failed, checking anyway...');
    } else {
      console.log('  Login successful, redirected to:', url);
    }
  } catch (e) {
    console.log('  Login form interaction failed:', e.message);
  }

  // Test pages
  console.log('\n[2/3] Testing pages...');
  const results = [];

  for (const { route, keywords } of TEST_PAGES) {
    await page.goto(`http://localhost:5173${route}`, { waitUntil: 'networkidle', timeout: 15000 });
    await page.waitForTimeout(2000);

    const text = await page.evaluate(() => document.body.innerText.toLowerCase());
    const found = keywords.filter(k => text.includes(k));
    const isLogin = text.includes('sign in to your account');

    const status = isLogin ? 'LOGIN' : found.length > 0 ? 'OK' : 'PARTIAL';
    results.push({ route, status, found: found.length, total: keywords.length });

    console.log(`  ${status === 'OK' ? '✓' : status === 'PARTIAL' ? '~' : '✗'} ${route} - ${status} (${found.length}/${keywords.length} keywords)`);
  }

  // Summary
  console.log('\n[3/3] Summary');
  console.log('='.repeat(70));
  const ok = results.filter(r => r.status === 'OK').length;
  const partial = results.filter(r => r.status === 'PARTIAL').length;
  const login = results.filter(r => r.status === 'LOGIN').length;

  console.log(`  OK: ${ok}, PARTIAL: ${partial}, LOGIN: ${login}`);
  console.log('='.repeat(70));

  await browser.close();
  return results;
}

test()
  .then(r => process.exit(r.filter(x => x.status === 'LOGIN').length === r.length ? 1 : 0))
  .catch(e => { console.error(e); process.exit(1); });
