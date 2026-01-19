const { chromium } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

// Gather routes from page files
function getRoutesFromPages() {
  const pagesDir = path.join(__dirname, 'src', 'pages');
  const routes = new Set();

  function scanDir(dir, prefix = '') {
    try {
      const entries = fs.readdirSync(dir, { withFileTypes: true });
      for (const entry of entries) {
        if (entry.name.startsWith('__')) continue; // Skip __tests__

        if (entry.isDirectory()) {
          scanDir(path.join(dir, entry.name), `${prefix}/${entry.name.toLowerCase()}`);
        } else if (entry.name.endsWith('.tsx') && !entry.name.includes('.test.')) {
          // Convert filename to route
          const name = entry.name.replace('.tsx', '');
          if (name === 'index' || name === 'Index') {
            routes.add(prefix || '/');
          } else {
            routes.add(`${prefix}/${name.toLowerCase()}`);
          }
        }
      }
    } catch (e) {
      console.warn(`Warning: Could not scan ${dir}: ${e.message}`);
    }
  }

  scanDir(pagesDir);
  return Array.from(routes).slice(0, 100); // Limit to first 100 for speed
}

// Key routes to test
const KEY_ROUTES = [
  '/',
  '/dashboard',
  '/projects',
  '/tasks',
  '/settings',
  '/ai',
  '/mission',
  '/workspaces',
  '/observability',
  '/governance',
  '/drivers',
  '/docs',
  '/ai/autofix',
  '/ai/workflows',
  '/ai/security',
  '/mission/overview',
  '/mission/architecture',
  '/workspaces/writer',
  '/workspaces/dev',
  '/governance/security',
  '/observability/health',
  '/drivers/marketplace',
  '/ipm',
  '/ipm/projects',
];

async function testRoutes() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  console.log('='.repeat(70));
  console.log('  Comprehensive Route Testing');
  console.log('='.repeat(70));

  // Login
  console.log('\n[1/4] Logging in...');
  await page.goto('http://localhost:5173/login');
  await page.waitForLoadState('networkidle');
  await page.fill('input[id="username"]', 'admin');
  await page.fill('input[id="password"]', 'admin123');
  await page.click('button[type="submit"]');
  await page.waitForURL(url => !url.href.includes('/login'), { timeout: 10000 });
  console.log('  Login successful');

  // Get routes from pages
  console.log('\n[2/4] Gathering routes...');
  const pageRoutes = getRoutesFromPages();
  const allRoutes = [...new Set([...KEY_ROUTES, ...pageRoutes])];
  console.log(`  Found ${allRoutes.length} routes to test`);

  // Test routes
  console.log('\n[3/4] Testing routes...');
  const results = { ok: [], fail: [] };

  for (const route of allRoutes) {
    try {
      const response = await page.goto(`http://localhost:5173${route}`, {
        waitUntil: 'domcontentloaded',
        timeout: 10000,
      });

      const status = response?.status() || 0;
      const content = await page.content();

      // Check for actual 404 page (not API errors)
      const is404Page = content.includes('<h1>404</h1>') ||
                       (content.includes('Page not found') && content.length < 5000);

      const isLoginRedirect = content.includes('Sign in to your account') && content.length < 20000;

      if (status >= 200 && status < 400 && !is404Page && !isLoginRedirect) {
        results.ok.push({ route, status, length: content.length });
        process.stdout.write('.');
      } else {
        results.fail.push({ route, status, reason: is404Page ? '404 page' : isLoginRedirect ? 'login redirect' : `status ${status}` });
        process.stdout.write('X');
      }
    } catch (error) {
      results.fail.push({ route, status: 0, reason: error.message.substring(0, 50) });
      process.stdout.write('E');
    }
  }

  console.log('\n');

  // Summary
  console.log('\n[4/4] Summary');
  console.log('='.repeat(70));
  console.log(`  Passed: ${results.ok.length}`);
  console.log(`  Failed: ${results.fail.length}`);
  console.log(`  Total: ${allRoutes.length}`);

  if (results.fail.length > 0 && results.fail.length <= 30) {
    console.log('\n  Failed routes:');
    results.fail.forEach(r => {
      console.log(`    - ${r.route}: ${r.reason}`);
    });
  } else if (results.fail.length > 30) {
    console.log(`\n  First 30 failed routes:`);
    results.fail.slice(0, 30).forEach(r => {
      console.log(`    - ${r.route}: ${r.reason}`);
    });
    console.log(`    ... and ${results.fail.length - 30} more`);
  }

  // Save results
  const reportPath = path.join(__dirname, 'route-test-results.json');
  fs.writeFileSync(reportPath, JSON.stringify({ ok: results.ok.length, fail: results.fail.length, failed: results.fail }, null, 2));
  console.log(`\n  Results saved to ${reportPath}`);

  await browser.close();
  return results;
}

testRoutes()
  .then(results => {
    const failRate = results.fail.length / (results.ok.length + results.fail.length);
    process.exit(failRate > 0.5 ? 1 : 0); // Only fail if more than 50% routes are broken
  })
  .catch(err => {
    console.error('Test failed:', err);
    process.exit(1);
  });
