const FLAG_STORAGE_KEY = 'osdash-feature-flags'
const COHORT_STORAGE_KEY = 'osdash-cohort'
const RELEASE_STORAGE_KEY = 'osdash-release-channel'

export type FeatureFlags = Record<string, boolean>

const readJson = <T>(raw: string | null, fallback: T): T => {
  if (!raw) return fallback
  try {
    return JSON.parse(raw) as T
  } catch {
    return fallback
  }
}

export const getFeatureFlags = (): FeatureFlags =>
  readJson<FeatureFlags>(localStorage.getItem(FLAG_STORAGE_KEY), {})

export const setFeatureFlags = (flags: FeatureFlags): void => {
  localStorage.setItem(FLAG_STORAGE_KEY, JSON.stringify(flags))
}

export const isFeatureEnabled = (flag: string): boolean => !!getFeatureFlags()[flag]

export const getEnabledFlagList = (): string[] =>
  Object.entries(getFeatureFlags())
    .filter(([, enabled]) => Boolean(enabled))
    .map(([key]) => key)

export const getFeatureFlagsHeader = (): string | undefined => {
  const enabled = getEnabledFlagList()
  return enabled.length ? enabled.join(',') : undefined
}

export const getCohort = (): string | null => localStorage.getItem(COHORT_STORAGE_KEY)

export const setCohort = (cohort: string | null): void => {
  if (cohort) {
    localStorage.setItem(COHORT_STORAGE_KEY, cohort)
  } else {
    localStorage.removeItem(COHORT_STORAGE_KEY)
  }
}

export const getReleaseChannel = (): string =>
  localStorage.getItem(RELEASE_STORAGE_KEY) ||
  import.meta.env.VITE_RELEASE_CHANNEL ||
  'stable'

export const setReleaseChannel = (channel: string | null): void => {
  if (channel) {
    localStorage.setItem(RELEASE_STORAGE_KEY, channel)
  } else {
    localStorage.removeItem(RELEASE_STORAGE_KEY)
  }
}
