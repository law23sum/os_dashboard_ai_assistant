import fs from 'node:fs'
import path from 'node:path'
import { test, expect } from './fixtures'

type RouteEntry = {
  path: string
  sources: Array<{ kind?: string; template?: string }>
}

const repoRoot = path.resolve(__dirname, '..', '..')
const routesPath = path.join(repoRoot, 'routes.json')

const routeManifest = JSON.parse(fs.readFileSync(routesPath, 'utf8')) as {
  routes: RouteEntry[]
}

const apiBase = process.env.E2E_API_BASE_URL || 'http://127.0.0.1:8000'
const demoCredentials = {
  username: process.env.E2E_USERNAME || 'admin',
  password: process.env.E2E_PASSWORD || 'admin123',
}

let accessToken: string | null = null
let userProfile: Record<string, unknown> | null = null

const isPublicRoute = (entry: RouteEntry) =>
  entry.sources?.some((source) => source.kind === 'public-route')

const seedCheck = async (token: string, request: any) => {
  const response = await request.get(`${apiBase}/api/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  expect(response.ok(), 'seed check: /api/auth/me should return 200').toBeTruthy()
  const data = await response.json()
  expect(data).toBeTruthy()
  return data
}

const loginOnce = async (request: any) => {
  if (accessToken) return
  const response = await request.post(`${apiBase}/api/auth/login`, {
    data: demoCredentials,
  })
  expect(response.ok(), 'login should return 200').toBeTruthy()
  const payload = await response.json()
  accessToken = payload.access_token
  userProfile = payload.user
  expect(accessToken, 'login should provide access_token').toBeTruthy()
}

const assertPageHealth = async ({ page, diagnostics }: { page: any; diagnostics: any }) => {
  await expect(page.locator('main.page-container')).toBeVisible()
  await expect(page.getByRole('heading', { name: '404' })).toHaveCount(0)

  const aiToggle = page.locator('#ai-assistant-toggle-button')
  await expect(aiToggle).toBeVisible()
  await aiToggle.click()
  await expect(page.getByRole('heading', { name: 'AI Assistant' })).toBeVisible()
  await expect(aiToggle).toHaveText(/Hide Assistant/i)
  await aiToggle.click()
  await expect(aiToggle).toHaveText(/AI Assistant/i)

  expect(diagnostics.consoleErrors, 'console errors').toEqual([])
  expect(diagnostics.pageErrors, 'page errors').toEqual([])
  expect(diagnostics.requestFailures, 'request failures').toEqual([])
}

test.beforeAll(async ({ request }) => {
  await loginOnce(request)
})

test.describe('route smoke', () => {
  for (const entry of routeManifest.routes) {
    const title = entry.path
    test(title, async ({ page, request, diagnostics }) => {
      if (isPublicRoute(entry)) {
        await page.goto(entry.path)
        if (entry.path === '/login') {
          await expect(page.getByRole('heading', { name: /OS Dashboard AI/i })).toBeVisible()
          await expect(page.locator('#username')).toBeVisible()
        } else if (entry.path === '/signup') {
          await expect(page.getByRole('heading', { name: /Create Account/i })).toBeVisible()
          await expect(page.locator('#email')).toBeVisible()
        } else {
          await expect(page.getByRole('heading')).toBeVisible()
        }
        return
      }

      if (!accessToken) {
        throw new Error('Missing access token for protected route')
      }

      await seedCheck(accessToken, request)
      await page.addInitScript(
        ({ token, user }) => {
          localStorage.setItem('access_token', token)
          if (user) {
            localStorage.setItem('user', JSON.stringify(user))
          }
        },
        { token: accessToken, user: userProfile },
      )

      await page.goto(entry.path)
      await assertPageHealth({ page, diagnostics })
    })
  }
})
