import { test as base, expect, type ConsoleMessage, type Page, type Request, type TestInfo } from '@playwright/test'

type Diagnostics = {
  consoleErrors: string[]
  pageErrors: string[]
  requestFailures: string[]
}

const attachDiagnostics = async (testInfo: TestInfo, diagnostics: Diagnostics) => {
  if (diagnostics.consoleErrors.length) {
    await testInfo.attach('console-errors', {
      body: diagnostics.consoleErrors.join('\n'),
      contentType: 'text/plain',
    })
  }
  if (diagnostics.pageErrors.length) {
    await testInfo.attach('page-errors', {
      body: diagnostics.pageErrors.join('\n'),
      contentType: 'text/plain',
    })
  }
  if (diagnostics.requestFailures.length) {
    await testInfo.attach('request-failures', {
      body: diagnostics.requestFailures.join('\n'),
      contentType: 'text/plain',
    })
  }
}

const test = base.extend<{
  diagnostics: Diagnostics
}>({
  diagnostics: async ({}, use) => {
    await use({ consoleErrors: [], pageErrors: [], requestFailures: [] })
  },
  page: async ({ page, diagnostics }, use, testInfo) => {
    const onConsole = (message: ConsoleMessage) => {
      if (message.type() === 'error') {
        diagnostics.consoleErrors.push(`[console.${message.type()}] ${message.text()}`)
      }
    }
    const onPageError = (error: Error) => {
      diagnostics.pageErrors.push(`[pageerror] ${error.message}`)
    }
    const onRequestFailed = (request: Request) => {
      const failure = request.failure()
      diagnostics.requestFailures.push(
        `[requestfailed] ${request.method()} ${request.url()} ${failure?.errorText ? `=> ${failure.errorText}` : ''}`.trim(),
      )
    }

    page.on('console', onConsole)
    page.on('pageerror', onPageError)
    page.on('requestfailed', onRequestFailed)

    await use(page)
    await attachDiagnostics(testInfo, diagnostics)
  },
})

export { test, expect }
