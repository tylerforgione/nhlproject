import { render } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { expect, it, vi } from 'vitest'

import App from './App'
import { getCurrentContext } from './api/home'

vi.mock('./api/home', () => ({ getCurrentContext: vi.fn() }))
vi.mock('./api/games', () => ({ getGamesByOfficialDate: vi.fn() }))

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
