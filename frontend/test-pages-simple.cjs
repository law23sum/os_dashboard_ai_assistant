const { chromium } = require('@playwright/test');

// Routes to test (some key integrated pages)
const ROUTES = [
  '/',
  '/login',
  '/dashboard',
  '/projects',
  '/tasks',
  '/ai',
  '/ai/autofix',
  '/ai/workflows',
  '/workspaces/writer',
  '/mission/architecture',
  '/governance/security',
  '/observability/health',
  '/drivers/marketplace',
];

async function testPages() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  console.log('='.repeat(70));
  console.log('  Testing Integrated SaaS Pages');
  console.log('='.repeat(70));

  const results = { ok: [], fail: [] };

  for (const route of ROUTES) {
    try {
      const response = await page.goto(`http://localhost:5173${route}`, {
        waitUntil: 'domcontentloaded',
        timeout: 10000,
      });

      const status = response?.status() || 0;
      const content = await page.content();

      // Check if page has real content (not just empty shell)
      const hasContent = content.length > 1000;
      const has404 = content.includes('<h1>404</h1>') || content.includes('Page not found');
      const hasError = content.includes('Error') && content.includes('Cannot');

      if (status >= 200 && status < 400 && hasContent && !has404 && !hasError) {
        results.ok.push({ route, status, length: content.length });
        console.log(`  ✓ ${route} - ${status} (${content.length} chars)`);
      } else {
        const reason = has404 ? '404' : hasError ? 'error' : `${status}/${content.length} chars`;
        results.fail.push({ route, status, reason });
        console.log(`  ✗ ${route} - ${reason}`);
      }
    } catch (error) {
      results.fail.push({ route, error: error.message.substring(0, 50) });
      console.log(`  ✗ ${route} - ${error.message.substring(0, 50)}`);
    }
  }

  console.log('\n' + '='.repeat(70));
  console.log(`  RESULTS: ${results.ok.length} passed, ${results.fail.length} failed`);
  console.log('='.repeat(70));

  await browser.close();
  return results;
}

testPages()
  .then(r => process.exit(r.fail.length > r.ok.length ? 1 : 0))
  .catch(e => { console.error(e); process.exit(1); });
