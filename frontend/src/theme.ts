import { useEffect, useState } from 'react'

type ThemePreference = 'system' | 'light' | 'dark'

const storageKey = 'hockey-stat-pack-theme'

function savedPreference(): ThemePreference {
  const saved = localStorage.getItem(storageKey)
  return saved === 'light' || saved === 'dark' ? saved : 'system'
}

export function useTheme() {
  const [preference, setPreference] = useState<ThemePreference>(savedPreference)
  const resolvedTheme =
    preference === 'system'
      ? matchMedia('(prefers-color-scheme: dark)').matches
        ? 'dark'
        : 'light'
      : preference

  useEffect(() => {
    document.documentElement.dataset.theme = resolvedTheme
  }, [resolvedTheme])

  function cycleTheme() {
    const next =
      preference === 'system'
        ? 'light'
        : preference === 'light'
          ? 'dark'
          : 'system'

    setPreference(next)

    if (next === 'system') localStorage.removeItem(storageKey)
    else localStorage.setItem(storageKey, next)
  }

  return { preference, cycleTheme }
}
