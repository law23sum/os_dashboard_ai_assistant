const { chromium } = require('@playwright/test');

const TEST_PAGES = [
  { route: '/projects', expects: ['project', 'task', 'create', 'status'] },
  { route: '/tasks', expects: ['task', 'status', 'priority', 'create'] },
  { route: '/dashboard', expects: ['dashboard', 'overview', 'metric'] },
  { route: '/ai/autofix', expects: ['auto', 'fix', 'error', 'resolve'] },
  { route: '/workspaces/writer', expects: ['writer', 'document', 'content'] },
  { route: '/drivers/marketplace', expects: ['driver', 'marketplace', 'install'] },
];

async function testContentQuality() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  console.log('='.repeat(70));
  console.log('  Testing Page Content Quality');
  console.log('='.repeat(70));

  for (const { route, expects } of TEST_PAGES) {
    console.log(`\n--- ${route} ---`);

    await page.goto(`http://localhost:5173${route}`, {
      waitUntil: 'networkidle',
      timeout: 15000,
    });

    // Wait for React to render
    await page.waitForTimeout(2000);

    // Get rendered text content
    const textContent = await page.evaluate(() => document.body.innerText.toLowerCase());
    const htmlContent = await page.content();

    // Check for expected keywords
    const found = expects.filter(kw => textContent.includes(kw.toLowerCase()));
    const missing = expects.filter(kw => !textContent.includes(kw.toLowerCase()));

    // Check for API indicators in source
    const hasUseQuery = htmlContent.includes('useQuery') || htmlContent.includes('isLoading');
    const hasApiCall = htmlContent.includes('apiClient') || htmlContent.includes('apiPath');

    console.log(`  Content length: ${textContent.length} chars`);
    console.log(`  Keywords found: ${found.join(', ') || 'none'}`);
    console.log(`  Keywords missing: ${missing.join(', ') || 'none'}`);
    console.log(`  Has loading states: ${htmlContent.includes('Loading') || htmlContent.includes('Spinner')}`);

    // Show snippet of actual content
    const snippet = textContent.substring(0, 300).replace(/\s+/g, ' ').trim();
    console.log(`  Preview: ${snippet.substring(0, 150)}...`);
  }

  await browser.close();
}

testContentQuality()
  .then(() => process.exit(0))
  .catch(e => { console.error(e); process.exit(1); });
