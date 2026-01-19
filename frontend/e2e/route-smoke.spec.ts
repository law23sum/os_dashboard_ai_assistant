import { test, expect } from '@playwright/test'
import fs from 'node:fs'
import path from 'node:path'
import { routeComponentRoutes } from '../src/navigation/routeComponentMap'

const placeholderMarkers = [
  'Page Under Construction',
  'MVP Scaffold',
  'Coming soon',
  'TODO',
]

const sanitizeRoute = (route: string) =>
  route
    .replace(/^\/+/, '')
    .replace(/\/+$/g, '')
    .replace(/[^a-zA-Z0-9_-]/g, '_') || 'root'

test.describe('Route Smoke', () => {
  test('routes render without placeholder markers', async ({ page }) => {
    test.setTimeout(15 * 60 * 1000)

    const failures: Array<{ route: string; marker: string; screenshot: string }> = []

    for (const route of routeComponentRoutes) {
      await test.step(route, async () => {
        const target = route.startsWith('/') ? route : `/${route}`
        await page.goto(target, { waitUntil: 'domcontentloaded' })
        await page.waitForLoadState('networkidle', { timeout: 5000 }).catch(() => {})
        await page.waitForTimeout(250)

        const bodyText = (await page.textContent('body')) || ''
        const marker = placeholderMarkers.find((entry) => bodyText.includes(entry))
        if (!marker) return

        const slug = sanitizeRoute(target)
        const screenshotPath = path.join(process.cwd(), 'test-results', 'route-smoke', `${slug}.png`)
        fs.mkdirSync(path.dirname(screenshotPath), { recursive: true })
        await page.screenshot({ path: screenshotPath, fullPage: true })
        failures.push({ route: target, marker, screenshot: screenshotPath })
      })
    }

    if (failures.length > 0) {
      const todoPath = path.join(process.cwd(), 'test-results', 'route-smoke', 'todo.json')
      fs.mkdirSync(path.dirname(todoPath), { recursive: true })
      fs.writeFileSync(todoPath, JSON.stringify(failures, null, 2), 'utf8')
    }

    expect(failures, `Routes with placeholder markers: ${failures.length}`).toEqual([])
  })
})
