import { render, screen, within } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, expect, it, vi } from 'vitest'

import {
  appApiMocks,
  currentContextFixture,
  gameSummaryFixture,
  gamesResponseFixture,
  resetAppApiMocks,
} from './test/appApiMocks'
import App from './App'

vi.stubEnv('TZ', 'America/New_York')

const currentContext = currentContextFixture()

beforeEach(resetAppApiMocks)

it('shows todays scheduled games through the Home route', async () => {
  appApiMocks.getCurrentContext.mockResolvedValue(currentContext)
  appApiMocks.getGamesByOfficialDate.mockResolvedValue(
    gamesResponseFixture({ games: [gameSummaryFixture()] }),
  )

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
  const scoresBanner = screen.getByRole('region', { name: "Today's games" })
  expect(screen.getByRole('main').firstElementChild).toBe(scoresBanner)
  expect(
    within(scoresBanner).getByRole('region', { name: "Today's NHL games" }),
  ).toHaveAttribute('tabindex', '0')
  expect(
    within(scoresBanner).getByRole('link', {
      name: 'View Boston Bruins at New York Rangers in Games',
    }),
  ).toHaveAttribute(
    'href',
    '/games?date=2026-01-15&season=20252026&gameType=regular-season',
  )
  expect(screen.getByText('Boston Bruins')).toBeInTheDocument()
  expect(screen.getByText('New York Rangers')).toBeInTheDocument()
  expect(screen.getByText('7:30 PM EST')).toBeInTheDocument()
  expect(screen.getByText('Scheduled')).toBeInTheDocument()
})
