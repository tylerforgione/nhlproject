import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'

const homeDescription =
  "See today's NHL schedule, local start times, and game status."

export function RouteMetadata() {
  const location = useLocation()

  useEffect(() => {
    const isGamesRoute = location.pathname === '/games'
    document.title = isGamesRoute
      ? 'NHL Games | Hockey Stat Pack'
      : "Today's NHL Games | Hockey Stat Pack"

    let description = document.querySelector<HTMLMetaElement>(
      'meta[name="description"]',
    )

    if (!description) {
      description = document.createElement('meta')
      description.name = 'description'
      document.head.append(description)
    }

    description.content = homeDescription

    let canonical = document.querySelector<HTMLLinkElement>(
      'link[rel="canonical"]',
    )

    if (!canonical) {
      canonical = document.createElement('link')
      canonical.rel = 'canonical'
      document.head.append(canonical)
    }

    canonical.href = new URL(location.pathname, window.location.origin).href
  }, [location.pathname])

  return null
}
