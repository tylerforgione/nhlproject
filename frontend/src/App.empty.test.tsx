import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { expect, it, vi } from 'vitest'

import App from './App'
import { getGamesByOfficialDate } from './api/games'
import { getCurrentContext } from './api/home'

vi.mock('./api/home', () => ({ getCurrentContext: vi.fn() }))
vi.mock('./api/games', () => ({ getGamesByOfficialDate: vi.fn() }))

it('shows a deliberate empty state for an official date with no games', async () => {
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
    <MemoryRouter initialEntries={['/']}>
      <App />
    </MemoryRouter>,
  )

  expect(
    await screen.findByText('No NHL games are scheduled for this official date.'),
  ).toBeInTheDocument()
  expect(screen.getByText('January 15, 2026')).toBeInTheDocument()
})
