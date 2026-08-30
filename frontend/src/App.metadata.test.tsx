import { render } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, expect, it } from 'vitest'

import { appApiMocks, resetAppApiMocks } from './test/appApiMocks'
import App from './App'

beforeEach(resetAppApiMocks)

it('publishes meaningful metadata for the canonical Home route', () => {
  appApiMocks.getCurrentContext.mockReturnValue(new Promise(() => undefined))

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
  appApiMocks.getGamesByOfficialDate.mockReturnValue(new Promise(() => undefined))

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
  expect(appApiMocks.getCurrentContext).not.toHaveBeenCalled()
})
