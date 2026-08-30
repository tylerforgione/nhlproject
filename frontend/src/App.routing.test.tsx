import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, expect, it } from 'vitest'

import {
  appApiMocks,
  currentContextFixture,
  gamesResponseFixture,
  resetAppApiMocks,
} from './test/appApiMocks'
import App from './App'

beforeEach(resetAppApiMocks)

it('supports direct loading of the working Games destination', async () => {
  appApiMocks.getCurrentContext.mockResolvedValue(currentContextFixture())
  appApiMocks.getGamesByOfficialDate.mockResolvedValue(gamesResponseFixture())

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
  appApiMocks.getGamesByOfficialDate.mockResolvedValue(
    gamesResponseFixture({
      official_date: '2026-01-14',
      capability: { state: 'unknown', explanation: 'Coverage is unverified.' },
      games: [],
    }),
  )

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
  expect(appApiMocks.getGamesByOfficialDate).toHaveBeenCalledWith(
    '2026-01-14',
    {
      seasonId: 20252026,
      gameType: 'regular-season',
    },
  )
  expect(appApiMocks.getCurrentContext).not.toHaveBeenCalled()
})
