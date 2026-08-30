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

it('shows games with malformed reference data without a Games link', async () => {
  appApiMocks.getCurrentContext.mockResolvedValue(currentContext)
  appApiMocks.getGamesByOfficialDate.mockResolvedValue(
    gamesResponseFixture({
      games: [gameSummaryFixture({ official_date: 'not-a-date' })],
    }),
  )

  render(
    <MemoryRouter initialEntries={['/']}>
      <App />
    </MemoryRouter>,
  )

  expect(await screen.findByText('Boston Bruins')).toBeInTheDocument()
  expect(
    screen.queryByRole('link', {
      name: 'View Boston Bruins at New York Rangers in Games',
    }),
  ).not.toBeInTheDocument()
})

it('shows game cards in API order with the current presentation details', async () => {
  appApiMocks.getCurrentContext.mockResolvedValue(currentContext)
  appApiMocks.getGamesByOfficialDate.mockResolvedValue(
    gamesResponseFixture({
      games: [
        gameSummaryFixture({
          away_score: 0,
          home_score: 2,
          state: 'final',
        }),
        gameSummaryFixture({
          id: 2025020711,
          away_team: {
            id: 3,
            name: 'Montreal Canadiens',
            abbreviation: 'MTL',
            logo_url: null,
            dark_logo_url: null,
          },
          home_team: {
            id: 4,
            name: 'Toronto Maple Leafs',
            abbreviation: 'TOR',
            logo_url: null,
            dark_logo_url: null,
          },
          venue: 'Scotiabank Arena',
        }),
      ],
    }),
  )

  render(
    <MemoryRouter initialEntries={['/']}>
      <App />
    </MemoryRouter>,
  )

  const scores = await screen.findByRole('region', {
    name: "Today's NHL games",
  })
  expect(screen.getByText('regular-season')).toBeInTheDocument()
  expect(screen.getByText('January 15, 2026')).toBeInTheDocument()
  expect(within(scores).getAllByRole('article')).toHaveLength(2)
  expect(
    within(scores).getAllByRole('link').map((link) => link.textContent),
  ).toEqual([
    expect.stringContaining('Boston Bruins'),
    expect.stringContaining('Montreal Canadiens'),
  ])
  expect(within(scores).getByText('0')).toBeInTheDocument()
  expect(within(scores).getByText('2')).toBeInTheDocument()
  expect(within(scores).getByText('Final')).toBeInTheDocument()
  expect(within(scores).getByText('Madison Square Garden')).toBeInTheDocument()
  expect(within(scores).getByText('Scotiabank Arena')).toBeInTheDocument()
})

it('links an unknown game type with a partial Games Reference', async () => {
  appApiMocks.getCurrentContext.mockResolvedValue(currentContext)
  appApiMocks.getGamesByOfficialDate.mockResolvedValue(
    gamesResponseFixture({
      games: [gameSummaryFixture({ game_type: 'unknown' })],
    }),
  )

  render(
    <MemoryRouter initialEntries={['/']}>
      <App />
    </MemoryRouter>,
  )

  expect(
    await screen.findByRole('link', {
      name: 'View Boston Bruins at New York Rangers in Games',
    }),
  ).toHaveAttribute('href', '/games?date=2026-01-15&season=20252026')
})
