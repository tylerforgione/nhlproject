import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { expect, it } from 'vitest'

import {
  appApiMocks,
  currentContextFixture,
  gameSummaryFixture,
  gamesResponseFixture,
} from './test/appApiMocks'
import App from './App'

it('distinguishes unavailable scheduled scores from a recorded zero', async () => {
  appApiMocks.getCurrentContext.mockResolvedValue(
    currentContextFixture(),
  )
  appApiMocks.getGamesByOfficialDate.mockResolvedValue(
    gamesResponseFixture({
      games: [
        gameSummaryFixture({
          start_time_utc: null,
          venue: null,
          venue_timezone: null,
        }),
      ],
    }),
  )

  render(
    <MemoryRouter>
      <App />
    </MemoryRouter>,
  )

  expect(await screen.findByText('Time unavailable')).toBeInTheDocument()
  expect(screen.getAllByLabelText('Score unavailable')).toHaveLength(2)
  expect(screen.queryByText('0')).not.toBeInTheDocument()
})
