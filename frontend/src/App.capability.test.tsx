import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { expect, it } from 'vitest'

import {
  appApiMocks,
  currentContextFixture,
  gamesResponseFixture,
} from './test/appApiMocks'
import App from './App'

it('shows the API explanation when game coverage is partial', async () => {
  appApiMocks.getCurrentContext.mockResolvedValue(
    currentContextFixture({
      official_date: '1920-01-15',
      active_season_phase: 'regular-season',
      schedule_season_id: 19191920,
      latest_completed_season_id: 19181919,
      games_capability: {
        state: 'partial',
        explanation: 'Some historical schedules are incomplete.',
      },
    }),
  )
  appApiMocks.getGamesByOfficialDate.mockResolvedValue(
    gamesResponseFixture({
      official_date: '1920-01-15',
      capability: {
        state: 'partial',
        explanation: 'Some historical schedules are incomplete.',
      },
      games: [],
    }),
  )

  render(
    <MemoryRouter>
      <App />
    </MemoryRouter>,
  )

  const notice = await screen.findByText(
    'Some historical schedules are incomplete.',
  )
  const scoresModule = screen.getByRole('region', { name: "Today's games" })

  expect(notice).toBeInTheDocument()
  expect(scoresModule.parentElement).toHaveClass('scores-module-frame')
  expect(scoresModule.parentElement).toContainElement(notice)
  expect(scoresModule).not.toContainElement(notice)
})
