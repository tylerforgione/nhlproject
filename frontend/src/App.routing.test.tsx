import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, expect, it, vi } from 'vitest'

import App from './App'
import { getGamesByOfficialDate } from './api/games'
import { getCurrentContext } from './api/home'

vi.mock('./api/home', () => ({ getCurrentContext: vi.fn() }))
vi.mock('./api/games', () => ({ getGamesByOfficialDate: vi.fn() }))

beforeEach(() => {
  vi.mocked(getCurrentContext).mockReset()
  vi.mocked(getGamesByOfficialDate).mockReset()
})

it('supports direct loading of the working Games destination', async () => {
  vi.mocked(getCurrentContext).mockResolvedValue({
    official_date: '2026-01-15',
    active_season_phase: 'regular-season',
    schedule_season_id: 20252026,
    latest_completed_season_id: 20242025,
    games_capability: { state: 'available', explanation: null },
  })
  vi.mocked(getGamesByOfficialDate).mockResolvedValue({
    official_date: '2026-01-15',
    capability: { state: 'available', explanation: null },
    games: [],
  })

  render(
    <MemoryRouter initialEntries={['/games']}>
      <App />
    </MemoryRouter>,
  )

  expect(
    await screen.findByRole('heading', { level: 1, name: 'Games' }),
  ).toBeInTheDocument()
  expect(
    screen.getByRole('heading', { level: 2, name: "Today's games" }),
  ).toBeInTheDocument()
  expect(screen.getByRole('link', { name: 'Games' })).toHaveAttribute(
    'aria-current',
    'page',
  )
})

it('restores official date state from a direct Games URL', async () => {
  vi.mocked(getGamesByOfficialDate).mockResolvedValue({
    official_date: '2026-01-14',
    capability: { state: 'unknown', explanation: 'Coverage is unverified.' },
    games: [],
  })

  render(
    <MemoryRouter
      initialEntries={[
        '/games?date=2026-01-14&season=20252026&gameType=regular-season',
      ]}
    >
      <App />
    </MemoryRouter>,
  )

  expect(await screen.findByText('January 14, 2026')).toBeInTheDocument()
  expect(getGamesByOfficialDate).toHaveBeenCalledWith('2026-01-14')
  expect(getCurrentContext).not.toHaveBeenCalled()
})
