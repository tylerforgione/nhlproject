import { useEffect, useState } from 'react'

type ThemePreference = 'system' | 'light' | 'dark'
type Theme = Exclude<ThemePreference, 'system'>

const storageKey = 'hockey-stat-pack-theme'

function savedPreference(): ThemePreference {
  const saved = localStorage.getItem(storageKey)
  return saved === 'light' || saved === 'dark' ? saved : 'system'
}

export function useTheme() {
  const [preference, setPreference] = useState<ThemePreference>(savedPreference)
  const [systemTheme, setSystemTheme] = useState<Theme>(() =>
    matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light',
  )
  const resolvedTheme = preference === 'system' ? systemTheme : preference

  useEffect(() => {
    const media = matchMedia('(prefers-color-scheme: dark)')
    const updateSystemTheme = (event: MediaQueryListEvent) => {
      setSystemTheme(event.matches ? 'dark' : 'light')
    }

    media.addEventListener('change', updateSystemTheme)
    return () => media.removeEventListener('change', updateSystemTheme)
  }, [])

  useEffect(() => {
    document.documentElement.dataset.theme = resolvedTheme
  }, [resolvedTheme])

  function toggleTheme() {
    const next = resolvedTheme === 'dark' ? 'light' : 'dark'

    setPreference(next)
    localStorage.setItem(storageKey, next)
  }

  return { resolvedTheme, toggleTheme }
}
