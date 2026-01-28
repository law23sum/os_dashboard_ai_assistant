import { test, expect } from './fixtures'

test('loads dashboard and top navigation', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByText('OS Dashboard · AI Assistant')).toBeVisible()
  await expect(page.getByRole('button', { name: 'Mission Control' })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Workspaces' })).toBeVisible()
  await expect(page.getByRole('button', { name: 'AI Fabric' })).toBeVisible()
})

test('navigates to Projects and shows feature sidebar', async ({ page }) => {
  await page.goto('/projects')
  await expect(page.getByRole('heading', { name: /Master Stack/i })).toBeVisible()
  await expect(page.getByText('Platform features')).toBeVisible()
  await expect(page.getByRole('link', { name: 'Ledger' })).toBeVisible()
})
