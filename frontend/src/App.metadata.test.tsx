import { render } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, expect, it, vi } from 'vitest'

import App from './App'
import { getCurrentContext } from './api/home'
import { getGamesByOfficialDate } from './api/games'

vi.mock('./api/home', () => ({ getCurrentContext: vi.fn() }))
vi.mock('./api/games', () => ({ getGamesByOfficialDate: vi.fn() }))

beforeEach(() => {
  vi.mocked(getCurrentContext).mockReset()
  vi.mocked(getGamesByOfficialDate).mockReset()
})

it('publishes meaningful metadata for the canonical Home route', () => {
  vi.mocked(getCurrentContext).mockReturnValue(new Promise(() => undefined))

  render(
    <MemoryRouter initialEntries={['/']}>
      <App />
    </MemoryRouter>,
  )

  expect(document.title).toBe("Today's NHL Games | Hockey Stat Pack")
  expect(document.querySelector('meta[name="description"]')).toHaveAttribute(
    'content',
    "See today's NHL schedule, local start times, and game status.",
  )
  expect(document.querySelector('link[rel="canonical"]')).toHaveAttribute(
    'href',
    new URL('/', window.location.origin).href,
  )
})

it('keeps Games reference state in canonical metadata', () => {
  vi.mocked(getGamesByOfficialDate).mockReturnValue(new Promise(() => undefined))

  render(
    <MemoryRouter
      initialEntries={[
        '/games?date=2026-01-14&season=20252026&gameType=regular-season',
      ]}
    >
      <App />
    </MemoryRouter>,
  )

  expect(document.title).toBe('NHL Games | Hockey Stat Pack')
  expect(document.querySelector('link[rel="canonical"]')).toHaveAttribute(
    'href',
    new URL(
      '/games?date=2026-01-14&season=20252026&gameType=regular-season',
      window.location.origin,
    ).href,
  )
  expect(getCurrentContext).not.toHaveBeenCalled()
})
