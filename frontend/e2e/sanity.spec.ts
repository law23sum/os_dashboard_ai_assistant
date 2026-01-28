import { test, expect } from './fixtures';

test.describe('OS Dashboard E2E Sanity', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should load the dashboard and show top navigation', async ({ page }) => {
    await expect(page).toHaveTitle(/OS Dashboard/);
    await expect(page.getByText('Mission Control')).toBeVisible();
    await expect(page.getByText('Workspaces')).toBeVisible();
    await expect(page.getByText('AI Fabric')).toBeVisible();
  });

  test('should navigate to Projects platform via dropdown', async ({ page }) => {
    // Click "Mission Control" category to open dropdown
    await page.getByRole('button', { name: 'Mission Control' }).click();
    
    // Click "Projects" platform link
    await page.getByRole('link', { name: 'Projects' }).click();
    
    // Verify URL
    await expect(page).toHaveURL(/.*\/projects/);
    
    // Verify Sidebar appears
    await expect(page.getByText('Projects Features')).toBeVisible();
    await expect(page.getByText('All Projects')).toBeVisible();
    await expect(page.getByText('Risk Analysis')).toBeVisible();
  });

  test('should navigate to Writer workspace', async ({ page }) => {
    await page.getByRole('button', { name: 'Workspaces' }).click();
    await page.getByRole('link', { name: 'Writer Workstation' }).click();
    
    await expect(page).toHaveURL(/.*\/work\/writer/);
    await expect(page.getByText('Writer Workstation Features')).toBeVisible();
    await expect(page.getByText('Drafts')).toBeVisible();
    await expect(page.getByText('Publication Pipeline')).toBeVisible();
  });

  test('should toggle AI Assistant panel', async ({ page }) => {
    const aiButton = page.getByRole('button', { name: 'AI Assistant' });
    await expect(aiButton).toBeVisible();
    
    await aiButton.click();
    await expect(page.getByText('Hide Assistant')).toBeVisible();
    
    // Check if panel content is visible (UnifiedAIPanel)
    // This might depend on how the panel is implemented, checking for a known element inside it
    // Assuming "Unified AI Controller" or similar text exists
    // await expect(page.getByText('Unified AI Controller')).toBeVisible();
  });
});
