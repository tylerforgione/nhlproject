import { render, screen, within } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, expect, it, vi } from 'vitest'

import App from './App'
import { getGamesByOfficialDate } from './api/games'
import { getCurrentContext } from './api/home'

vi.stubEnv('TZ', 'America/New_York')

vi.mock('./api/home', () => ({ getCurrentContext: vi.fn() }))
vi.mock('./api/games', () => ({ getGamesByOfficialDate: vi.fn() }))

const currentContext = {
  official_date: '2026-01-15',
  active_season_phase: 'regular-season' as const,
  schedule_season_id: 20252026,
  latest_completed_season_id: 20242025,
  games_capability: { state: 'available' as const, explanation: null },
}

beforeEach(() => {
  vi.mocked(getCurrentContext).mockReset()
  vi.mocked(getGamesByOfficialDate).mockReset()
})

it('shows todays scheduled games through the Home route', async () => {
  vi.mocked(getCurrentContext).mockResolvedValue(currentContext)
  vi.mocked(getGamesByOfficialDate).mockResolvedValue({
    official_date: '2026-01-15',
    capability: { state: 'available', explanation: null },
    games: [
      {
        id: 2025020710,
        season_id: 20252026,
        game_type: 'regular-season',
        state: 'scheduled',
        official_date: '2026-01-15',
        start_time_utc: '2026-01-16T00:30:00Z',
        away_team: {
          id: 1,
          name: 'Boston Bruins',
          abbreviation: 'BOS',
          logo_url: null,
          dark_logo_url: null,
        },
        home_team: {
          id: 2,
          name: 'New York Rangers',
          abbreviation: 'NYR',
          logo_url: null,
          dark_logo_url: null,
        },
        away_score: null,
        home_score: null,
        venue: 'Madison Square Garden',
        venue_timezone: 'America/New_York',
        neutral_site: false,
      },
    ],
  })

  render(
    <MemoryRouter initialEntries={['/']}>
      <App />
    </MemoryRouter>,
  )

  expect(
    screen.getByRole('banner', { name: 'Hockey Stat Pack' }),
  ).toBeInTheDocument()
  const navigation = screen.getByRole('navigation', { name: 'Primary' })
  expect(
    within(navigation).getAllByRole('link').map((link) => link.textContent),
  ).toEqual(['Home', 'Games'])
  expect(
    await screen.findByRole('heading', { name: "Today's games" }),
  ).toBeInTheDocument()
  expect(screen.getByText('Boston Bruins')).toBeInTheDocument()
  expect(screen.getByText('New York Rangers')).toBeInTheDocument()
  expect(screen.getByText('7:30 PM EST')).toBeInTheDocument()
  expect(screen.getByText('Scheduled')).toBeInTheDocument()
})
