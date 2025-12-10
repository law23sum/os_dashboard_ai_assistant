import rawTokens from './theme/tokens.json'

export interface ThemeDefinition {
  label: string
  tokens: Record<string, string>
  gradients?: Record<string, string>
}

type ThemeCatalog = Record<string, ThemeDefinition>

const themeCatalog = rawTokens as ThemeCatalog

export type ThemeName = keyof typeof themeCatalog | string

const selectFallbackTheme = (): string => {
  if ('dark' in themeCatalog) return 'dark'
  if ('plain' in themeCatalog) return 'plain'
  const keys = Object.keys(themeCatalog)
  return keys[0] || 'dark'
}

export const defaultTheme: ThemeName = selectFallbackTheme()

export const availableThemes: ThemeName[] = Object.keys(themeCatalog) as ThemeName[]

export const describeTheme = (name: ThemeName): string => {
  if (typeof name !== 'string' || !name) return themeCatalog[defaultTheme]?.label ?? String(defaultTheme)
  return themeCatalog[name]?.label ?? name
}

export const getThemeDefinition = (
  themeName?: ThemeName,
): { name: string; definition: ThemeDefinition } => {
  const normalized = typeof themeName === 'string' && themeName ? themeName : defaultTheme
  const definition =
    themeCatalog[normalized] ??
    themeCatalog[defaultTheme] ??
    themeCatalog[availableThemes[0]]
  const resolvedName =
    definition === themeCatalog[normalized] ? normalized : defaultTheme

  return { name: resolvedName, definition }
}

export const applyTheme = (themeName?: ThemeName) => {
  if (typeof document === 'undefined') return

  const { name, definition } = getThemeDefinition(themeName)
  const root = document.documentElement

  Object.entries(definition.tokens).forEach(([token, value]) => {
    root.style.setProperty(`--osd-${token}`, value)
  })

  if (definition.gradients) {
    Object.entries(definition.gradients).forEach(([token, value]) => {
      root.style.setProperty(`--osd-gradient-${token}`, value)
    })
  }

  root.dataset.theme = name
}
