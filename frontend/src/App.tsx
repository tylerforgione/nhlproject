import { useEffect, useState } from 'react'
import { NavLink, Route, Routes } from 'react-router-dom'

import './product.css'
import './coverage.css'
import './states.css'
import './theme.css'
import { getGamesByOfficialDate } from './api/games'
import type { GameSummary, GamesByDateResponse } from './api/game-types'
import { getCurrentContext } from './api/home'
import type { CurrentContext } from './api/types'
import { RouteMetadata } from './RouteMetadata'
import { useTheme } from './theme'

interface HomeData {
  context: CurrentContext
  schedule: GamesByDateResponse
}

type LoadState = 'loading' | 'success' | 'error'

function formatStartTime(startTimeUtc: string | null): string {
  if (!startTimeUtc) return 'Time unavailable'

  return new Intl.DateTimeFormat(undefined, {
    hour: 'numeric',
    minute: '2-digit',
    timeZoneName: 'short',
  }).format(new Date(startTimeUtc))
}

function formatStatus(game: GameSummary): string {
  if (game.state === 'scheduled') return 'Scheduled'
  if (game.state === 'live') return 'Live'
  if (game.state === 'final') return 'Final'
  return 'Status unavailable'
}

function Team({ game, side }: { game: GameSummary; side: 'away' | 'home' }) {
  const team = side === 'away' ? game.away_team : game.home_team
  const score = side === 'away' ? game.away_score : game.home_score

  return (
    <div className="team-row">
      <span className="team-abbreviation" aria-hidden="true">
        {team.abbreviation}
      </span>
      <span className="team-name">{team.name}</span>
      {score === null ? (
        <span className="team-score" aria-label="Score unavailable">
          —
        </span>
      ) : (
        <strong className="team-score">{score}</strong>
      )}
    </div>
  )
}

function ScoresModule({
  data,
  headingLevel = 1,
}: {
  data: HomeData
  headingLevel?: 1 | 2
}) {
  return (
    <section className="scores-section" aria-labelledby="todays-games-heading">
      <div className="section-heading">
        <div>
          <p className="eyebrow">{data.context.active_season_phase}</p>
          {headingLevel === 1 ? (
            <h1 id="todays-games-heading">Today's games</h1>
          ) : (
            <h2 id="todays-games-heading">Today's games</h2>
          )}
        </div>
        <time dateTime={data.schedule.official_date}>
          {new Intl.DateTimeFormat(undefined, {
            month: 'long',
            day: 'numeric',
            year: 'numeric',
            timeZone: 'UTC',
          }).format(new Date(`${data.schedule.official_date}T12:00:00Z`))}
        </time>
      </div>
      {data.schedule.capability.state !== 'available' &&
        data.schedule.capability.explanation && (
          <p className="coverage-notice">
            {data.schedule.capability.explanation}
          </p>
        )}
      {data.schedule.games.length === 0 ? (
        <div className="scores-state">
          <p role="status">
            No NHL games are scheduled for this official date.
          </p>
        </div>
      ) : (
        <div className="scores-scroll" tabIndex={0} aria-label="Today's NHL games">
          {data.schedule.games.map((game) => (
            <article className="game-card" key={game.id}>
              <div className="game-meta">
                <span>{formatStartTime(game.start_time_utc)}</span>
                <span className={`game-state game-state-${game.state}`}>
                  {formatStatus(game)}
                </span>
              </div>
              <Team game={game} side="away" />
              <Team game={game} side="home" />
              {game.venue && <p className="venue">{game.venue}</p>}
            </article>
          ))}
        </div>
      )}
    </section>
  )
}

function CurrentGamesPage({ isGamesPage = false }: { isGamesPage?: boolean }) {
  const [data, setData] = useState<HomeData | null>(null)
  const [loadState, setLoadState] = useState<LoadState>('loading')
  const [attempt, setAttempt] = useState(0)

  useEffect(() => {
    let active = true
    async function loadGames() {
      try {
        const context = await getCurrentContext()
        const schedule = await getGamesByOfficialDate(context.official_date)

        if (active) {
          setData({ context, schedule })
          setLoadState('success')
        }
      } catch {
        if (active) setLoadState('error')
      }
    }

    void loadGames()

    return () => {
      active = false
    }
  }, [attempt])

  if (loadState === 'error') {
    return (
      <main className="page-content">
        <section className="scores-state" role="alert">
          <div>
            <h1>We couldn't load today's games</h1>
            <p>This looks temporary. Check your connection and try again.</p>
            <button
              type="button"
              onClick={() => {
                setLoadState('loading')
                setAttempt((value) => value + 1)
              }}
            >
              Try again
            </button>
          </div>
        </section>
      </main>
    )
  }

  if (loadState === 'loading' || !data) {
    return (
      <main className="page-content" aria-busy="true">
        <section className="scores-state" data-testid="scores-state">
          <p role="status">Loading today's games…</p>
        </section>
      </main>
    )
  }

  return (
    <main className="page-content">
      {isGamesPage && <h1 className="page-title">Games</h1>}
      <ScoresModule data={data} headingLevel={isGamesPage ? 2 : 1} />
    </main>
  )
}

function App() {
  const { preference, cycleTheme } = useTheme()

  return (
    <div className="app-shell">
      <RouteMetadata />
      <header className="site-header" aria-label="Hockey Stat Pack">
        <NavLink className="wordmark" to="/" aria-label="Hockey Stat Pack Home">
          Hockey Stat Pack
        </NavLink>
        <div className="header-actions">
          <nav aria-label="Primary">
            <NavLink to="/">Home</NavLink>
            <NavLink to="/games">Games</NavLink>
          </nav>
          <button
            className="theme-toggle"
            type="button"
            aria-label={"Theme: " + preference}
            onClick={cycleTheme}
          >
            Theme
          </button>
        </div>
      </header>
      <Routes>
        <Route path="/" element={<CurrentGamesPage />} />
        <Route path="/games" element={<CurrentGamesPage isGamesPage />} />
      </Routes>
    </div>
  )
}

export default App
