import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { expect, it, vi } from 'vitest'

import App from './App'
import { getGamesByOfficialDate } from './api/games'
import { getCurrentContext } from './api/home'

vi.mock('./api/home', () => ({ getCurrentContext: vi.fn() }))
vi.mock('./api/games', () => ({ getGamesByOfficialDate: vi.fn() }))

it('lets a visitor retry a recoverable games error', async () => {
  const user = userEvent.setup()
  vi.mocked(getCurrentContext)
    .mockRejectedValueOnce(new Error('Unavailable'))
    .mockResolvedValueOnce({
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

  const alert = await screen.findByRole('alert')
  expect(alert).toHaveTextContent("We couldn't load today's games")
  await user.click(screen.getByRole('button', { name: 'Try again' }))
  expect(
    await screen.findByText('No NHL games are scheduled for this official date.'),
  ).toBeInTheDocument()
  expect(getCurrentContext).toHaveBeenCalledTimes(2)
})
