import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { expect, it, vi } from 'vitest'

import App from './App'
import { getGamesByOfficialDate } from './api/games'
import { getCurrentContext } from './api/home'

vi.mock('./api/home', () => ({ getCurrentContext: vi.fn() }))
vi.mock('./api/games', () => ({ getGamesByOfficialDate: vi.fn() }))

it('distinguishes unavailable scheduled scores from a recorded zero', async () => {
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
    games: [
      {
        id: 2025020710,
        season_id: 20252026,
        game_type: 'regular-season',
        state: 'scheduled',
        official_date: '2026-01-15',
        start_time_utc: null,
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
        venue: null,
        venue_timezone: null,
        neutral_site: false,
      },
    ],
  })

  render(
    <MemoryRouter>
      <App />
    </MemoryRouter>,
  )

  expect(await screen.findByText('Time unavailable')).toBeInTheDocument()
  expect(screen.getAllByLabelText('Score unavailable')).toHaveLength(2)
  expect(screen.queryByText('0')).not.toBeInTheDocument()
})
