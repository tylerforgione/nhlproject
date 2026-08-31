import { act, render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import {
  MemoryRouter,
  useLocation,
  useNavigate,
  useNavigationType,
} from 'react-router-dom'
import { beforeEach, expect, it } from 'vitest'

import {
  appApiMocks,
  currentContextFixture,
  gameSummaryFixture,
  gamesResponseFixture,
  resetAppApiMocks,
} from './test/appApiMocks'
import App from './App'

beforeEach(resetAppApiMocks)

function RouteStateProbe() {
  const location = useLocation()
  const navigationType = useNavigationType()
  return <output>{`${location.pathname}${location.search}|${navigationType}`}</output>
}

function LoadJanuaryFourteenth() {
  const navigate = useNavigate()
  return (
    <button
      type="button"
      onClick={() =>
        navigate(
          '/games?date=2026-01-14&season=20252026&gameType=regular-season',
        )
      }
    >
      Load January 14
    </button>
  )
}

it('supports direct loading of the working Games destination', async () => {
  appApiMocks.getCurrentContext.mockResolvedValue(currentContextFixture())
  appApiMocks.getGamesByOfficialDate.mockResolvedValue(
    gamesResponseFixture({
      games: [gameSummaryFixture()],
    }),
  )

  render(
    <MemoryRouter initialEntries={['/games']}>
      <App />
    </MemoryRouter>,
  )

  expect(
    await screen.findByRole('heading', {
      level: 1,
      name: 'Games for January 15, 2026',
    }),
  ).toBeInTheDocument()
  expect(
    screen.getByRole('heading', {
      level: 2,
      name: '2025–26 Regular Season',
    }),
  ).toBeInTheDocument()
  expect(
    screen.getByRole('region', {
      name: '2025–26 Regular Season games for January 15, 2026',
    }),
  ).toHaveAttribute('tabindex', '0')
  expect(screen.queryByRole('link', { name: /in Games/ })).not.toBeInTheDocument()
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

  expect(
    await screen.findByRole('heading', {
      level: 1,
      name: 'Games for January 14, 2026',
    }),
  ).toBeInTheDocument()
  expect(appApiMocks.getGamesByOfficialDate).toHaveBeenCalledWith(
    '2026-01-14',
    {
      seasonId: 20252026,
      gameType: 'regular-season',
    },
  )
  expect(appApiMocks.getCurrentContext).not.toHaveBeenCalled()
})

it('loads a date-only Games Reference without resolving current context', async () => {
  appApiMocks.getGamesByOfficialDate.mockResolvedValue(
    gamesResponseFixture({
      official_date: '2026-01-14',
      season_id: null,
      game_type: null,
    }),
  )

  render(
    <MemoryRouter initialEntries={['/games?date=2026-01-14']}>
      <App />
    </MemoryRouter>,
  )

  expect(
    await screen.findByRole('heading', {
      level: 1,
      name: 'Games for January 14, 2026',
    }),
  ).toBeInTheDocument()
  expect(appApiMocks.getGamesByOfficialDate).toHaveBeenCalledWith(
    '2026-01-14',
    {},
  )
  expect(appApiMocks.getCurrentContext).not.toHaveBeenCalled()
})

it('replaces bare Games with the canonical current Schedule Context', async () => {
  appApiMocks.getCurrentContext.mockResolvedValue(currentContextFixture())
  appApiMocks.getGamesByOfficialDate.mockResolvedValue(
    gamesResponseFixture({ games: [gameSummaryFixture()] }),
  )

  render(
    <MemoryRouter initialEntries={['/games']}>
      <App />
      <RouteStateProbe />
    </MemoryRouter>,
  )

  expect(
    await screen.findByText(
      '/games?date=2026-01-15&season=20252026&gameType=regular-season|REPLACE',
    ),
  ).toBeInTheDocument()
  expect(appApiMocks.getCurrentContext).toHaveBeenCalledTimes(1)
  expect(appApiMocks.getGamesByOfficialDate).toHaveBeenCalledWith(
    '2026-01-15',
    { seasonId: 20252026, gameType: 'regular-season' },
  )
})

it('cleans and orders a valid Games Reference with history replacement', async () => {
  appApiMocks.getGamesByOfficialDate.mockResolvedValue(
    gamesResponseFixture({
      official_date: '2026-01-14',
      games: [],
    }),
  )

  render(
    <MemoryRouter
      initialEntries={[
        '/games?gameType=regular-season&utm=score&date=2026-01-14&season=20252026',
      ]}
    >
      <App />
      <RouteStateProbe />
    </MemoryRouter>,
  )

  expect(
    await screen.findByText(
      '/games?date=2026-01-14&season=20252026&gameType=regular-season|REPLACE',
    ),
  ).toBeInTheDocument()
  expect(appApiMocks.getGamesByOfficialDate).toHaveBeenCalledTimes(1)
})

it('completes a date-only reference from one returned Schedule Context', async () => {
  appApiMocks.getGamesByOfficialDate.mockResolvedValue(
    gamesResponseFixture({ games: [gameSummaryFixture()] }),
  )

  render(
    <MemoryRouter initialEntries={['/games?date=2026-01-15']}>
      <App />
      <RouteStateProbe />
    </MemoryRouter>,
  )

  expect(
    await screen.findByText(
      '/games?date=2026-01-15&season=20252026&gameType=regular-season|REPLACE',
    ),
  ).toBeInTheDocument()
  expect(appApiMocks.getGamesByOfficialDate).toHaveBeenNthCalledWith(
    1,
    '2026-01-15',
    {},
  )
  expect(appApiMocks.getGamesByOfficialDate).toHaveBeenLastCalledWith(
    '2026-01-15',
    { seasonId: 20252026, gameType: 'regular-season' },
  )
})

it('renders named and Other games as distinct ordered Schedule Groups', async () => {
  const playoffGame = gameSummaryFixture({
    id: 2024020711,
    season_id: 20242025,
    game_type: 'playoffs',
    away_team: {
      id: 3,
      name: 'Montreal Canadiens',
      abbreviation: 'MTL',
      logo_url: null,
      dark_logo_url: null,
    },
  })
  const unknown2025 = gameSummaryFixture({
    id: 2025020712,
    game_type: 'unknown',
    away_team: {
      id: 4,
      name: 'Ottawa Senators',
      abbreviation: 'OTT',
      logo_url: null,
      dark_logo_url: null,
    },
  })
  const unknown2024 = gameSummaryFixture({
    id: 2024020713,
    season_id: 20242025,
    game_type: 'unknown',
    away_team: {
      id: 5,
      name: 'Buffalo Sabres',
      abbreviation: 'BUF',
      logo_url: null,
      dark_logo_url: null,
    },
  })
  appApiMocks.getGamesByOfficialDate.mockResolvedValue(
    gamesResponseFixture({
      season_id: null,
      game_type: null,
      games: [gameSummaryFixture(), unknown2025, playoffGame, unknown2024],
    }),
  )

  render(
    <MemoryRouter initialEntries={['/games?date=2026-01-15']}>
      <App />
    </MemoryRouter>,
  )

  expect(
    await screen.findByRole('heading', {
      level: 1,
      name: 'Games for January 15, 2026',
    }),
  ).toBeInTheDocument()
  expect(
    screen.getAllByRole('heading', { level: 2 }).map((heading) => heading.textContent),
  ).toEqual([
    '2025–26 Regular Season',
    '2024–25 Playoffs',
    '2025–26 Other games',
    '2024–25 Other games',
  ])
  expect(
    within(
      screen.getByRole('region', { name: '2025–26 Other games' }),
    ).getByText('Ottawa Senators'),
  ).toBeInTheDocument()
})

it.each([
  [
    '/games?date=2026-01-14',
    'No NHL games are scheduled for January 14, 2026.',
    {},
  ],
  [
    '/games?date=2026-01-14&season=20252026',
    'No NHL games are scheduled for January 14, 2026 in the 2025–26 season.',
    { seasonId: 20252026 },
  ],
  [
    '/games?date=2026-01-14&gameType=regular-season',
    'No Regular Season games are scheduled for January 14, 2026.',
    { gameType: 'regular-season' },
  ],
  [
    '/games?date=2026-01-14&season=20252026&gameType=regular-season',
    'No Regular Season games are scheduled for January 14, 2026 in the 2025–26 season.',
    { seasonId: 20252026, gameType: 'regular-season' },
  ],
])('renders explicit empty scope for %s', async (url, message, filters) => {
  appApiMocks.getGamesByOfficialDate.mockResolvedValue(
    gamesResponseFixture({
      official_date: '2026-01-14',
      season_id: null,
      game_type: null,
    }),
  )

  render(
    <MemoryRouter initialEntries={[url]}>
      <App />
    </MemoryRouter>,
  )

  expect(await screen.findByText(message)).toBeInTheDocument()
  expect(appApiMocks.getGamesByOfficialDate).toHaveBeenCalledWith(
    '2026-01-14',
    filters,
  )
})

it('recovers an invalid Games link through explicit current-context replacement', async () => {
  const user = userEvent.setup()
  appApiMocks.getCurrentContext.mockResolvedValue(currentContextFixture())
  appApiMocks.getGamesByOfficialDate.mockResolvedValue(gamesResponseFixture())

  render(
    <MemoryRouter initialEntries={['/games?date=not-a-date']}>
      <App />
      <RouteStateProbe />
    </MemoryRouter>,
  )

  expect(
    await screen.findByRole('heading', { name: 'This Games link is invalid' }),
  ).toBeInTheDocument()
  expect(appApiMocks.getCurrentContext).not.toHaveBeenCalled()
  expect(appApiMocks.getGamesByOfficialDate).not.toHaveBeenCalled()

  await user.click(screen.getByRole('button', { name: 'Go to Today' }))

  expect(
    await screen.findByText(
      '/games?date=2026-01-15&season=20252026&gameType=regular-season|REPLACE',
    ),
  ).toBeInTheDocument()
})

it('retries a dated request without changing its Games Reference', async () => {
  const user = userEvent.setup()
  appApiMocks.getGamesByOfficialDate
    .mockRejectedValueOnce(new Error('Unavailable'))
    .mockResolvedValueOnce(
      gamesResponseFixture({ official_date: '2026-01-14' }),
    )

  render(
    <MemoryRouter
      initialEntries={[
        '/games?date=2026-01-14&season=20252026&gameType=regular-season',
      ]}
    >
      <App />
      <RouteStateProbe />
    </MemoryRouter>,
  )

  expect(
    await screen.findByRole('heading', {
      name: "We couldn't load games for January 14, 2026",
    }),
  ).toBeInTheDocument()
  expect(screen.getByText(/\/games\?date=2026-01-14.*\|POP/)).toBeInTheDocument()

  await user.click(screen.getByRole('button', { name: 'Try again' }))

  expect(
    await screen.findByText(
      'No Regular Season games are scheduled for January 14, 2026 in the 2025–26 season.',
    ),
  ).toBeInTheDocument()
  expect(appApiMocks.getGamesByOfficialDate).toHaveBeenCalledTimes(2)
  expect(appApiMocks.getGamesByOfficialDate).toHaveBeenLastCalledWith(
    '2026-01-14',
    { seasonId: 20252026, gameType: 'regular-season' },
  )
})

it('clears previous Schedule Groups while a different reference loads', async () => {
  const user = userEvent.setup()
  appApiMocks.getGamesByOfficialDate
    .mockResolvedValueOnce(
      gamesResponseFixture({ games: [gameSummaryFixture()] }),
    )
    .mockReturnValueOnce(new Promise(() => undefined))

  render(
    <MemoryRouter
      initialEntries={[
        '/games?date=2026-01-15&season=20252026&gameType=regular-season',
      ]}
    >
      <App />
      <LoadJanuaryFourteenth />
    </MemoryRouter>,
  )

  expect(await screen.findByText('Boston Bruins')).toBeInTheDocument()

  await user.click(screen.getByRole('button', { name: 'Load January 14' }))

  expect(
    await screen.findByText('Loading games for January 14, 2026…'),
  ).toHaveAttribute('role', 'status')
  expect(screen.queryByText('Boston Bruins')).not.toBeInTheDocument()
})

it('ignores an obsolete partial-reference response after location changes', async () => {
  const user = userEvent.setup()
  let resolveObsolete: (response: ReturnType<typeof gamesResponseFixture>) => void
  const obsoleteResponse = new Promise<ReturnType<typeof gamesResponseFixture>>(
    (resolve) => {
      resolveObsolete = resolve
    },
  )
  appApiMocks.getGamesByOfficialDate
    .mockReturnValueOnce(obsoleteResponse)
    .mockResolvedValueOnce(
      gamesResponseFixture({
        official_date: '2026-01-14',
        games: [
          gameSummaryFixture({
            official_date: '2026-01-14',
            away_team: {
              id: 4,
              name: 'Ottawa Senators',
              abbreviation: 'OTT',
              logo_url: null,
              dark_logo_url: null,
            },
          }),
        ],
      }),
    )

  render(
    <MemoryRouter initialEntries={['/games?date=2026-01-15']}>
      <App />
      <LoadJanuaryFourteenth />
      <RouteStateProbe />
    </MemoryRouter>,
  )

  await user.click(screen.getByRole('button', { name: 'Load January 14' }))
  expect(await screen.findByText('Ottawa Senators')).toBeInTheDocument()

  await act(async () => {
    resolveObsolete(
      gamesResponseFixture({ games: [gameSummaryFixture()] }),
    )
  })

  expect(screen.getByText(/\/games\?date=2026-01-14.*\|PUSH/)).toBeInTheDocument()
  expect(screen.queryByText('Boston Bruins')).not.toBeInTheDocument()
})

it('resolves bare Games to a season-only reference during offseason', async () => {
  appApiMocks.getCurrentContext.mockResolvedValue(
    currentContextFixture({ active_season_phase: 'offseason' }),
  )
  appApiMocks.getGamesByOfficialDate.mockResolvedValue(gamesResponseFixture())

  render(
    <MemoryRouter initialEntries={['/games']}>
      <App />
      <RouteStateProbe />
    </MemoryRouter>,
  )

  expect(
    await screen.findByText(
      '/games?date=2026-01-15&season=20252026|REPLACE',
    ),
  ).toBeInTheDocument()
  expect(appApiMocks.getGamesByOfficialDate).toHaveBeenCalledWith(
    '2026-01-15',
    { seasonId: 20252026 },
  )
})

it.each([
  [
    '/games?date=2026-01-15&season=20252026',
    '/games?date=2026-01-15&season=20252026&gameType=regular-season|REPLACE',
  ],
  [
    '/games?date=2026-01-15&gameType=regular-season',
    '/games?date=2026-01-15&season=20252026&gameType=regular-season|REPLACE',
  ],
])('completes one missing scope value for %s', async (url, canonicalState) => {
  appApiMocks.getGamesByOfficialDate.mockResolvedValue(
    gamesResponseFixture({ games: [gameSummaryFixture()] }),
  )

  render(
    <MemoryRouter initialEntries={[url]}>
      <App />
      <RouteStateProbe />
    </MemoryRouter>,
  )

  expect(await screen.findByText(canonicalState)).toBeInTheDocument()
  expect(appApiMocks.getGamesByOfficialDate).toHaveBeenCalledTimes(2)
})

it('preserves partial scope when named and unknown games are returned together', async () => {
  appApiMocks.getGamesByOfficialDate.mockResolvedValue(
    gamesResponseFixture({
      season_id: null,
      game_type: null,
      games: [
        gameSummaryFixture(),
        gameSummaryFixture({
          id: 2025020711,
          game_type: 'unknown',
          away_team: {
            id: 4,
            name: 'Ottawa Senators',
            abbreviation: 'OTT',
            logo_url: null,
            dark_logo_url: null,
          },
        }),
      ],
    }),
  )

  render(
    <MemoryRouter initialEntries={['/games?date=2026-01-15']}>
      <App />
      <RouteStateProbe />
    </MemoryRouter>,
  )

  expect(await screen.findByText('Boston Bruins')).toBeInTheDocument()
  expect(screen.getByText('Ottawa Senators')).toBeInTheDocument()
  expect(screen.getByText('/games?date=2026-01-15|POP')).toBeInTheDocument()
  expect(appApiMocks.getGamesByOfficialDate).toHaveBeenCalledTimes(1)
})

it('deduplicates response notices once above all Schedule Groups', async () => {
  const explanation = 'Schedule coverage may be stale.'
  appApiMocks.getGamesByOfficialDate.mockResolvedValue(
    gamesResponseFixture({
      capability: { state: 'partial', explanation },
      freshness: {
        state: 'stale',
        updated_at: '2026-01-15T12:00:00Z',
        explanation,
      },
      games: [gameSummaryFixture()],
    }),
  )

  render(
    <MemoryRouter
      initialEntries={[
        '/games?date=2026-01-15&season=20252026&gameType=regular-season',
      ]}
    >
      <App />
    </MemoryRouter>,
  )

  const notice = await screen.findByText(explanation)
  const groupHeading = screen.getByRole('heading', {
    level: 2,
    name: '2025–26 Regular Season',
  })
  expect(screen.getAllByText(explanation)).toHaveLength(1)
  expect(
    notice.compareDocumentPosition(groupHeading) & Node.DOCUMENT_POSITION_FOLLOWING,
  ).toBeTruthy()
})

it.each([
  '/games?date=2026-01-15&date=2026-01-16',
  '/games?date=2026-01-15&gameType=unknown',
  '/games?date=2026-01-15&season=20262025',
])('rejects malformed known route state in %s', async (url) => {
  render(
    <MemoryRouter initialEntries={[url]}>
      <App />
    </MemoryRouter>,
  )

  expect(
    await screen.findByRole('heading', { name: 'This Games link is invalid' }),
  ).toBeInTheDocument()
  expect(appApiMocks.getCurrentContext).not.toHaveBeenCalled()
  expect(appApiMocks.getGamesByOfficialDate).not.toHaveBeenCalled()
})

it('renders a retryable bare-resolution failure', async () => {
  appApiMocks.getCurrentContext.mockRejectedValue(new Error('Unavailable'))

  render(
    <MemoryRouter initialEntries={['/games']}>
      <App />
    </MemoryRouter>,
  )

  expect(
    await screen.findByRole('heading', { name: "We couldn't load Games" }),
  ).toBeInTheDocument()
  expect(screen.getByRole('button', { name: 'Try again' })).toBeInTheDocument()
  expect(appApiMocks.getGamesByOfficialDate).not.toHaveBeenCalled()
})
