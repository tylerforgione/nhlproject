import { useEffect, useState } from 'react'

import type { GameSummary, GamesByDateResponse } from '../api/game-types'
import { getGamesByOfficialDate } from '../api/games'
import { getCurrentContext } from '../api/home'
import type { CurrentContext } from '../api/types'
import { ScoresModule } from '../components/ScoresModule'
import {
  gamesReferenceFromGame,
  gamesReferenceHref,
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

function getHomeGameLink(game: GameSummary) {
  const reference = gamesReferenceFromGame(game)
  if (!reference) return null

  return {
    to: gamesReferenceHref(reference),
    ariaLabel: `View ${game.away_team.name} at ${game.home_team.name} in Games`,
  }
}

export function CurrentGamesPage() {
  const [data, setData] = useState<HomeData | null>(null)
  const [loadState, setLoadState] = useState<LoadState>('loading')
  const [retryGeneration, setRetryGeneration] = useState(0)

  useEffect(() => {
    let active = true

    async function loadGames() {
      try {
        const currentContext = await getCurrentContext()
        if (!active) return
        const schedule = await getGamesByOfficialDate(
          currentContext.official_date,
        )
        if (!active) return

        setData({
          context: {
            active_season_phase: currentContext.active_season_phase,
          },
          schedule,
        })
        setLoadState('success')
      } catch {
        if (active) setLoadState('error')
      }
    }

    void loadGames()

    return () => {
      active = false
    }
  }, [retryGeneration])

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
                setRetryGeneration((value) => value + 1)
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

  const coverageExplanation =
    data.schedule.capability.state !== 'available'
      ? data.schedule.capability.explanation
      : null

  return (
    <main className="page-content home-page">
      <div
        className={`scores-module-frame${coverageExplanation ? ' has-scores-notice' : ''}`}
      >
        <ScoresModule
          games={data.schedule.games}
          eyebrow={data.context.active_season_phase}
          heading="Today's games"
          headingLevel={1}
          officialDate={data.schedule.official_date}
          scoresRegionLabel="Today's NHL games"
          getGameLink={getHomeGameLink}
        />
        {coverageExplanation && (
          <div className="scores-page-notice">
            <p className="coverage-notice">{coverageExplanation}</p>
          </div>
        )}
        {data.schedule.games.length === 0 && (
          <div className="scores-state scores-page-state">
            <p role="status">
              No NHL games are scheduled for this official date.
            </p>
          </div>
        )}
      </div>
    </main>
  )
}
