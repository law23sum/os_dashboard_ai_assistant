import { test, expect } from '@playwright/test'

test.describe('Import Validation', () => {
  test('should load without import errors', async ({ page }) => {
    // Collect console errors
    const errors: string[] = []
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        errors.push(msg.text())
      }
    })

    // Collect page errors
    page.on('pageerror', (error) => {
      errors.push(error.message)
    })

    // Navigate to the app
    await page.goto('http://localhost:5173', { waitUntil: 'networkidle' })

    // Wait a bit for any async imports to fail
    await page.waitForTimeout(2000)

    // Check for import-related errors
    const importErrors = errors.filter(
      (error) =>
        error.includes('Failed to resolve import') ||
        error.includes('Cannot find module') ||
        error.includes('Module not found') ||
        error.includes('zod') ||
        error.includes('PolicySimulator') ||
        error.includes('IARouteFallback') ||
        error.includes('FeaturePageTemplate')
    )

    if (importErrors.length > 0) {
      console.error('Import errors found:', importErrors)
    }

    // The test should pass if there are no import errors
    expect(importErrors.length).toBe(0)
  })

  test('should render FeaturePageTemplate without errors', async ({ page }) => {
    // Navigate to a route that uses FeaturePageTemplate
    // This will test if the component can be imported and rendered
    await page.goto('http://localhost:5173', { waitUntil: 'networkidle' })

    // Wait for the app to fully load
    await page.waitForTimeout(2000)

    // Check if the page loaded successfully (no 404 or error page)
    const bodyText = await page.textContent('body')
    expect(bodyText).not.toContain('Failed to resolve import')
    expect(bodyText).not.toContain('Module not found')
  })
})







