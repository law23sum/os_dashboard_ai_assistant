const { chromium } = require('@playwright/test');

const RESTORED_PAGES = [
  '/timeline',
  '/settings/audit',
  '/tasks/analytics',
  '/drivers/publishing',
  '/drivers/versioning',
  '/projects/settings',
  '/projects/templates',
  '/docs/integrations',
  '/observability/health',
  '/workspaces/writer',
  '/workspaces/finance',
  '/mission/orchestrator',
  '/mission/architecture',
  '/ai/workflows',
  '/ai/autofix',
  '/ai/security',
  '/governance/security',
  '/data/observability',
];

async function testPages() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  console.log('='.repeat(70));
  console.log('  Testing Restored Pages with Headless Browser');
  console.log('='.repeat(70));

  // Login first
  console.log('\n[1/3] Logging in...');
  await page.goto('http://localhost:5173/login');
  await page.waitForLoadState('networkidle');

  await page.fill('input[id="username"]', 'admin');
  await page.fill('input[id="password"]', 'admin123');
  await page.click('button[type="submit"]');

  // Wait for redirect after login
  await page.waitForURL(url => !url.href.includes('/login'), { timeout: 10000 });
  console.log('  Login successful');

  // Test each page
  console.log('\n[2/3] Testing restored pages...');
  const results = [];

  for (const route of RESTORED_PAGES) {
    try {
      const response = await page.goto(`http://localhost:5173${route}`, {
        waitUntil: 'networkidle',
        timeout: 15000,
      });

      const status = response?.status() || 0;
      const content = await page.content();
      const contentLength = content.length;

      // Check for error indicators
      const hasError = content.includes('404') && content.includes('not found');
      const hasApiContent = content.includes('useQuery') ||
                           contentLength > 2000 ||
                           content.includes('Loading') ||
                           content.includes('data-') ||
                           !content.includes('template-based');

      const isOk = status >= 200 && status < 400 && !hasError;

      results.push({
        route,
        status,
        contentLength,
        hasApiContent,
        ok: isOk,
      });

      const statusIcon = isOk ? '✓' : '✗';
      console.log(`  ${statusIcon} ${route} - ${status} (${contentLength} chars)`);

    } catch (error) {
      results.push({
        route,
        status: 0,
        contentLength: 0,
        hasApiContent: false,
        ok: false,
        error: error.message,
      });
      console.log(`  ✗ ${route} - Error: ${error.message}`);
    }
  }

  // Summary
  console.log('\n[3/3] Summary');
  console.log('='.repeat(70));
  const okCount = results.filter(r => r.ok).length;
  const failCount = results.filter(r => !r.ok).length;

  console.log(`  Passed: ${okCount}`);
  console.log(`  Failed: ${failCount}`);
  console.log(`  Total: ${results.length}`);

  if (failCount > 0) {
    console.log('\n  Failed routes:');
    results.filter(r => !r.ok).forEach(r => {
      console.log(`    - ${r.route}: ${r.error || `status ${r.status}`}`);
    });
  }

  await browser.close();
  return results;
}

testPages()
  .then(results => {
    process.exit(results.every(r => r.ok) ? 0 : 1);
  })
  .catch(err => {
    console.error('Test failed:', err);
    process.exit(1);
  });
