import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { expect, it } from 'vitest'

import { gameSummaryFixture } from '../test/appApiMocks'
import { ScoresModule } from './ScoresModule'

it('renders caller-supplied scores presentation text and semantics', () => {
  render(
    <MemoryRouter>
      <ScoresModule
        games={[gameSummaryFixture()]}
        eyebrow="Regular season"
        heading="Games for January 15"
        headingLevel={2}
        officialDate="2026-01-15"
        gamesLabel="January 15 NHL games"
      />
    </MemoryRouter>,
  )

  expect(screen.getByText('Regular season')).toBeInTheDocument()
  expect(
    screen.getByRole('heading', {
      level: 2,
      name: 'Games for January 15',
    }),
  ).toBeInTheDocument()
  expect(screen.getByText('January 15, 2026')).toHaveAttribute(
    'datetime',
    '2026-01-15',
  )
  expect(
    screen.getByRole('region', { name: 'Games for January 15' }),
  ).toBeInTheDocument()
  expect(
    screen.getByRole('region', { name: 'January 15 NHL games' }),
  ).toHaveAttribute('tabindex', '0')
})

it('uses the caller link resolver for linked and unlinked Game Cards', () => {
  const linkedGame = gameSummaryFixture()
  const unlinkedGame = gameSummaryFixture({
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
  })

  render(
    <MemoryRouter>
      <ScoresModule
        games={[linkedGame, unlinkedGame]}
        eyebrow="Regular season"
        heading="Games for January 15"
        headingLevel={2}
        officialDate="2026-01-15"
        gamesLabel="January 15 NHL games"
        getGameLink={(game) =>
          game.id === linkedGame.id
            ? {
                to: '/games?date=2026-01-15',
                ariaLabel: 'Open Bruins at Rangers',
              }
            : null
        }
      />
    </MemoryRouter>,
  )

  expect(
    screen.getByRole('link', { name: 'Open Bruins at Rangers' }),
  ).toHaveAttribute('href', '/games?date=2026-01-15')
  expect(screen.getByText('Montreal Canadiens')).toBeInTheDocument()
  expect(
    screen.queryByRole('link', { name: /Canadiens/ }),
  ).not.toBeInTheDocument()
  expect(screen.getAllByRole('article')).toHaveLength(2)
})

it('associates each Scores Module with its own heading', () => {
  render(
    <MemoryRouter>
      <ScoresModule
        games={[gameSummaryFixture()]}
        eyebrow="Regular season"
        heading="January 15 games"
        headingLevel={2}
        officialDate="2026-01-15"
        gamesLabel="January 15 NHL games"
      />
      <ScoresModule
        games={[gameSummaryFixture({ id: 2025020711 })]}
        eyebrow="Regular season"
        heading="January 16 games"
        headingLevel={2}
        officialDate="2026-01-16"
        gamesLabel="January 16 NHL games"
      />
    </MemoryRouter>,
  )

  const firstModule = screen.getByRole('region', { name: 'January 15 games' })
  const secondModule = screen.getByRole('region', { name: 'January 16 games' })
  const firstHeading = screen.getByRole('heading', {
    name: 'January 15 games',
  })
  const secondHeading = screen.getByRole('heading', {
    name: 'January 16 games',
  })

  expect(firstModule).toHaveAttribute('aria-labelledby', firstHeading.id)
  expect(secondModule).toHaveAttribute('aria-labelledby', secondHeading.id)
  expect(firstHeading.id).not.toBe(secondHeading.id)
})

it('renders empty games without adding empty-state policy', () => {
  render(
    <MemoryRouter>
      <ScoresModule
        games={[]}
        eyebrow="Regular season"
        heading="Games for January 15"
        headingLevel={2}
        officialDate="2026-01-15"
        gamesLabel="January 15 NHL games"
      />
    </MemoryRouter>,
  )

  expect(
    screen.getByRole('region', { name: 'Games for January 15' }),
  ).toBeInTheDocument()
  expect(screen.queryByRole('article')).not.toBeInTheDocument()
  expect(
    screen.queryByText('No NHL games are scheduled for this official date.'),
  ).not.toBeInTheDocument()
})
