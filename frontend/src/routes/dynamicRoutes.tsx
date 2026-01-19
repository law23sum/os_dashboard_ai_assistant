import { lazy, Suspense } from 'react'
import type { ReactElement } from 'react'

import Spinner from '../components/ui/Spinner'

type DynamicRoute = {
  path: string
  element: ReactElement
}

const pageModules = import.meta.glob('../pages/**/*.tsx')

const normalizeSegment = (segment: string): string => {
  // Convert CamelCase to kebab, replace non-alphanumerics with dashes, and lowercase.
  const kebab = segment
    .replace(/([a-z0-9])([A-Z])/g, '$1-$2')
    .replace(/[^a-zA-Z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .toLowerCase()
  return kebab || 'index'
}

const buildPathFromFile = (filePath: string): string => {
  // filePath example: '../pages/Mission/Orchestrator.tsx'
  const withoutPrefix = filePath.replace('../pages', '')
  const withoutExt = withoutPrefix.replace(/\.tsx$/i, '')
  const segments = withoutExt.split('/').filter(Boolean).map(normalizeSegment)
  return '/' + segments.join('/')
}

export const dynamicRoutes: DynamicRoute[] = Object.entries(pageModules).map(([filePath, importer]) => {
  const path = buildPathFromFile(filePath)
  const Page = lazy(importer as () => Promise<{ default: React.ComponentType }>)
  return {
    path,
    element: (
      <Suspense fallback={<div className="flex justify-center py-10"><Spinner /></div>}>
        <Page />
      </Suspense>
    ),
  }
})
