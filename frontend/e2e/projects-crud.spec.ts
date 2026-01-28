import { test, expect } from './fixtures'

test('projects CRUD: create -> verify -> delete', async ({ page }) => {
  const suffix = `${Date.now()}`
  const projectName = `E2E Project ${suffix}`

  await page.goto('/projects')

  await page.getByTestId('projects-new').click()
  await page.getByTestId('project-form-name').fill(projectName)
  await page.getByTestId('project-form-description').fill('Created by Playwright e2e')
  await page.getByTestId('project-form-priority').selectOption('MEDIUM')
  await page.getByTestId('project-form-status').selectOption('active')
  await page.getByTestId('project-form-submit').click()

  // Verify it shows up in the page
  await expect(page.getByText(projectName)).toBeVisible()

  // Delete the project
  page.once('dialog', (dialog) => dialog.accept())
  await page.getByTestId(`project-delete:${projectName}`).click()

  // Verify it disappears (give backend a moment)
  await expect(page.getByText(projectName)).not.toBeVisible({ timeout: 15_000 })
})
