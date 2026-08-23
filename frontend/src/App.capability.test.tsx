import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { expect, it, vi } from 'vitest'

import App from './App'
import { getGamesByOfficialDate } from './api/games'
import { getCurrentContext } from './api/home'

vi.mock('./api/home', () => ({ getCurrentContext: vi.fn() }))
vi.mock('./api/games', () => ({ getGamesByOfficialDate: vi.fn() }))

it('shows the API explanation when game coverage is partial', async () => {
  vi.mocked(getCurrentContext).mockResolvedValue({
    official_date: '1920-01-15',
    active_season_phase: 'regular-season',
    schedule_season_id: 19191920,
    latest_completed_season_id: 19181919,
    games_capability: {
      state: 'partial',
      explanation: 'Some historical schedules are incomplete.',
    },
  })
  vi.mocked(getGamesByOfficialDate).mockResolvedValue({
    official_date: '1920-01-15',
    capability: {
      state: 'partial',
      explanation: 'Some historical schedules are incomplete.',
    },
    games: [],
  })

  render(
    <MemoryRouter>
      <App />
    </MemoryRouter>,
  )

  expect(
    await screen.findByText('Some historical schedules are incomplete.'),
  ).toBeInTheDocument()
})
