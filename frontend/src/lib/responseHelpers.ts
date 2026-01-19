const readArray = <T>(value: unknown): T[] | null => (Array.isArray(value) ? (value as T[]) : null)

export const extractArray = <T>(data: unknown, keys: string[] = []): T[] => {
  const direct = readArray<T>(data)
  if (direct) return direct

  if (data && typeof data === 'object') {
    const record = data as Record<string, unknown>

    for (const key of keys) {
      const value = record[key]
      const byKey = readArray<T>(value)
      if (byKey) return byKey

      if (value && typeof value === 'object') {
        const nested = value as Record<string, unknown>
        const nestedItems = readArray<T>(nested.items) || readArray<T>(nested.data)
        if (nestedItems) return nestedItems
      }
    }

    const fallback = readArray<T>(record.items) || readArray<T>(record.data)
    if (fallback) return fallback
  }

  return []
}
