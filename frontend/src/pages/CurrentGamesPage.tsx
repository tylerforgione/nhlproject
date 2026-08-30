import { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'

import { getGamesByOfficialDate } from '../api/games'
import type { GameSummary, GamesByDateResponse } from '../api/game-types'
import { getCurrentContext } from '../api/home'
import type { CurrentContext } from '../api/types'
import { ScoresModule } from '../components/ScoresModule'
import {
  gamesReferenceFromGame,
  gamesReferenceHref,
  parseGamesReference,
} from '../routing/gamesReference'

interface ScoresContext {
  active_season_phase:
    | CurrentContext['active_season_phase']
    | GameSummary['game_type']
}

interface HomeData {
  context: ScoresContext
  schedule: GamesByDateResponse
}

type LoadState = 'loading' | 'success' | 'error'

interface CurrentGamesPageProps {
  isGamesPage?: boolean
}

function getHomeGameLink(game: GameSummary) {
  const reference = gamesReferenceFromGame(game)
  if (!reference) return null

  return {
    to: gamesReferenceHref(reference),
    ariaLabel: `View ${game.away_team.name} at ${game.home_team.name} in Games`,
  }
}

function formatOfficialDate(officialDate: string): string {
  return new Intl.DateTimeFormat(undefined, {
    month: 'long',
    day: 'numeric',
    year: 'numeric',
    timeZone: 'UTC',
  }).format(new Date(`${officialDate}T12:00:00Z`))
}

export function CurrentGamesPage({ isGamesPage = false }: CurrentGamesPageProps) {
  const [data, setData] = useState<HomeData | null>(null)
  const location = useLocation()
  const [loadState, setLoadState] = useState<LoadState>('loading')
  const [attempt, setAttempt] = useState(0)

  useEffect(() => {
    let active = true
    async function loadGames() {
      try {
        const parseResult = isGamesPage
          ? parseGamesReference(location.search)
          : { status: 'absent' as const }
        const reference =
          parseResult.status === 'valid' &&
          parseResult.reference.seasonId !== undefined &&
          parseResult.reference.gameType !== undefined
            ? {
                officialDate: parseResult.reference.officialDate,
                seasonId: parseResult.reference.seasonId,
                gameType: parseResult.reference.gameType,
              }
            : null
        let context: ScoresContext
        let officialDate: string

        if (reference) {
          context = { active_season_phase: reference.gameType }
          officialDate = reference.officialDate
        } else {
          const currentContext = await getCurrentContext()
          context = {
            active_season_phase: currentContext.active_season_phase,
          }
          officialDate = currentContext.official_date
        }

        const schedule = await getGamesByOfficialDate(
          officialDate,
          reference
            ? {
                seasonId: reference.seasonId,
                gameType: reference.gameType,
              }
            : undefined,
        )

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
  }, [attempt, isGamesPage, location.search])

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

  const officialDateLabel = formatOfficialDate(data.schedule.official_date)
  const scoresHeading = isGamesPage
    ? `Games for ${officialDateLabel}`
    : "Today's games"
  const scoresRegionLabel = isGamesPage
    ? `NHL games for ${officialDateLabel}`
    : "Today's NHL games"

  return (
    <main className={`page-content ${isGamesPage ? 'games-page' : 'home-page'}`}>
      {isGamesPage && <h1 className="page-title">Games</h1>}
      {data.schedule.capability.state !== 'available' &&
        data.schedule.capability.explanation && (
          <div className="scores-page-notice">
            <p className="coverage-notice">
              {data.schedule.capability.explanation}
            </p>
          </div>
        )}
      <ScoresModule
        games={data.schedule.games}
        eyebrow={data.context.active_season_phase}
        heading={scoresHeading}
        headingLevel={isGamesPage ? 2 : 1}
        officialDate={data.schedule.official_date}
        scoresRegionLabel={scoresRegionLabel}
        getGameLink={isGamesPage ? undefined : getHomeGameLink}
      />
      {data.schedule.games.length === 0 && (
        <div className="scores-state scores-page-state">
          <p role="status">
            No NHL games are scheduled for this official date.
          </p>
        </div>
      )}
    </main>
  )
}
