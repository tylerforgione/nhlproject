import { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

import { getGamesByOfficialDate } from '../api/games'
import type { GameSummary, GamesByDateResponse } from '../api/game-types'
import { getCurrentContext } from '../api/home'
import type { CurrentContext } from '../api/types'
import { ScoresModule } from '../components/ScoresModule'
import {
  type GamesReference,
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

type LoadState = 'loading' | 'success' | 'invalid' | 'error'

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

function formatGamesDateLabel(officialDate: string): string {
  return new Intl.DateTimeFormat(undefined, {
    month: 'long',
    day: 'numeric',
    year: 'numeric',
    timeZone: 'UTC',
  }).format(new Date(`${officialDate}T12:00:00Z`))
}

interface ScheduleGroup {
  key: string
  label: string
  eyebrow: string
  games: GameSummary[]
}

function formatScheduleSeason(seasonId: number): string {
  const value = String(seasonId).padStart(8, '0')
  return `${value.slice(0, 4)}–${value.slice(-2)}`
}

function formatGameType(gameType: GameSummary['game_type']): string {
  if (gameType === 'preseason') return 'Preseason'
  if (gameType === 'regular-season') return 'Regular Season'
  if (gameType === 'playoffs') return 'Playoffs'
  return 'Other games'
}

function deriveScheduleGroups(games: readonly GameSummary[]): ScheduleGroup[] {
  const namedGroups = new Map<string, ScheduleGroup>()
  const otherGroups = new Map<string, ScheduleGroup>()

  for (const game of games) {
    const isOther = game.game_type === 'unknown'
    const key = isOther
      ? `${game.season_id}:other`
      : `${game.season_id}:${game.game_type}`
    const groups = isOther ? otherGroups : namedGroups
    const existing = groups.get(key)
    if (existing) {
      existing.games.push(game)
      continue
    }

    const typeLabel = formatGameType(game.game_type)
    groups.set(key, {
      key,
      label: `${formatScheduleSeason(game.season_id)} ${typeLabel}`,
      eyebrow: isOther ? 'Other games' : typeLabel,
      games: [game],
    })
  }

  return [...namedGroups.values(), ...otherGroups.values()]
}

function getEmptyGamesMessage(
  reference: GamesReference,
  officialDateLabel: string,
): string {
  const subject = reference.gameType
    ? `No ${formatGameType(reference.gameType)} games`
    : 'No NHL games'
  const season = reference.seasonId
    ? ` in the ${formatScheduleSeason(reference.seasonId)} season`
    : ''
  return `${subject} are scheduled for ${officialDateLabel}${season}.`
}

export function CurrentGamesPage({
  isGamesPage = false,
}: CurrentGamesPageProps) {
  const [data, setData] = useState<HomeData | null>(null)
  const location = useLocation()
  const navigate = useNavigate()
  const [loadState, setLoadState] = useState<LoadState>('loading')
  const [attempt, setAttempt] = useState(0)
  const [recoverInvalid, setRecoverInvalid] = useState(false)
  const requestKey = `${location.pathname}${location.search}:${attempt}:${recoverInvalid}`
  const [settledRequestKey, setSettledRequestKey] = useState<string | null>(
    null,
  )

  useEffect(() => {
    let active = true

    async function loadGames() {
      try {
        const parseResult = isGamesPage
          ? parseGamesReference(location.search)
          : { status: 'absent' as const }
        if (
          isGamesPage &&
          parseResult.status === 'invalid' &&
          !recoverInvalid
        ) {
          if (active) {
            setData(null)
            setLoadState('invalid')
            setSettledRequestKey(requestKey)
          }
          return
        }
        const reference =
          parseResult.status === 'valid' ? parseResult.reference : null
        if (
          isGamesPage &&
          reference &&
          `${location.pathname}${location.search}` !==
            gamesReferenceHref(reference)
        ) {
          navigate(gamesReferenceHref(reference), { replace: true })
          return
        }
        let context: ScoresContext
        let officialDate: string

        if (reference) {
          context = { active_season_phase: reference.gameType ?? 'unknown' }
          officialDate = reference.officialDate
        } else {
          const currentContext = await getCurrentContext()
          if (!active) return
          if (isGamesPage) {
            const gameType =
              currentContext.active_season_phase === 'offseason'
                ? undefined
                : currentContext.active_season_phase
            setRecoverInvalid(false)
            navigate(
              gamesReferenceHref({
                officialDate: currentContext.official_date,
                seasonId: currentContext.schedule_season_id,
                gameType,
              }),
              { replace: true },
            )
            return
          }
          context = {
            active_season_phase: currentContext.active_season_phase,
          }
          officialDate = currentContext.official_date
        }

        const schedule = await getGamesByOfficialDate(
          officialDate,
          reference
            ? {
                ...(reference.seasonId === undefined
                  ? {}
                  : { seasonId: reference.seasonId }),
                ...(reference.gameType === undefined
                  ? {}
                  : { gameType: reference.gameType }),
              }
            : undefined,
        )
        if (!active) return

        if (isGamesPage && reference) {
          const namedGames = schedule.games.filter(
            (game): game is GameSummary & {
              game_type: Exclude<GameSummary['game_type'], 'unknown'>
            } => game.game_type !== 'unknown',
          )
          const contexts = new Map(
            namedGames.map((game) => [
              `${game.season_id}:${game.game_type}`,
              { seasonId: game.season_id, gameType: game.game_type },
            ]),
          )
          if (
            namedGames.length === schedule.games.length &&
            contexts.size === 1
          ) {
            const [resolvedContext] = contexts.values()
            const resolvedReference = {
              officialDate: reference.officialDate,
              seasonId: reference.seasonId ?? resolvedContext.seasonId,
              gameType: reference.gameType ?? resolvedContext.gameType,
            }
            if (
              gamesReferenceHref(resolvedReference) !==
              gamesReferenceHref(reference)
            ) {
              navigate(gamesReferenceHref(resolvedReference), { replace: true })
              return
            }
          }
        }

        if (active) {
          setData({ context, schedule })
          setLoadState('success')
          setSettledRequestKey(requestKey)
        }
      } catch {
        if (active) {
          setLoadState('error')
          setSettledRequestKey(requestKey)
        }
      }
    }

    void loadGames()

    return () => {
      active = false
    }
  }, [
    isGamesPage,
    location.pathname,
    location.search,
    navigate,
    recoverInvalid,
    requestKey,
  ])

  if (settledRequestKey === requestKey && loadState === 'invalid') {
    return (
      <main className="page-content">
        <section className="scores-state" role="alert">
          <div>
            <h1>This Games link is invalid</h1>
            <p>Use Today to load the current NHL schedule.</p>
            <button
              type="button"
              onClick={() => {
                setRecoverInvalid(true)
              }}
            >
              Go to Today
            </button>
          </div>
        </section>
      </main>
    )
  }

  if (settledRequestKey === requestKey && loadState === 'error') {
    const referenceResult = isGamesPage
      ? parseGamesReference(location.search)
      : { status: 'absent' as const }
    const errorHeading =
      isGamesPage && referenceResult.status === 'valid'
        ? `We couldn't load games for ${formatGamesDateLabel(referenceResult.reference.officialDate)}`
        : isGamesPage
          ? "We couldn't load Games"
          : "We couldn't load today's games"

    return (
      <main className="page-content">
        <section className="scores-state" role="alert">
          <div>
            <h1>{errorHeading}</h1>
            <p>This looks temporary. Check your connection and try again.</p>
            <button
              type="button"
              onClick={() => {
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

  if (settledRequestKey !== requestKey || loadState === 'loading' || !data) {
    const referenceResult = isGamesPage
      ? parseGamesReference(location.search)
      : { status: 'absent' as const }
    const loadingMessage =
      isGamesPage && referenceResult.status === 'valid'
        ? `Loading games for ${formatGamesDateLabel(referenceResult.reference.officialDate)}…`
        : isGamesPage
          ? 'Loading games…'
          : "Loading today's games…"

    return (
      <main className="page-content" aria-busy="true">
        <section className="scores-state" data-testid="scores-state">
          <p role="status">{loadingMessage}</p>
        </section>
      </main>
    )
  }

  const officialDateLabel = formatGamesDateLabel(data.schedule.official_date)

  if (isGamesPage) {
    const groups = deriveScheduleGroups(data.schedule.games)
    const referenceResult = parseGamesReference(location.search)
    const reference =
      referenceResult.status === 'valid'
        ? referenceResult.reference
        : { officialDate: data.schedule.official_date }
    const notices = [
      data.schedule.capability.state === 'available'
        ? null
        : data.schedule.capability.explanation,
      data.schedule.freshness.state === 'fresh'
        ? null
        : data.schedule.freshness.explanation,
    ].filter(
      (notice, index, values): notice is string =>
        Boolean(notice) && values.indexOf(notice) === index,
    )

    return (
      <main className="page-content games-page">
        <h1 className="page-title">Games for {officialDateLabel}</h1>
        {notices.length > 0 && (
          <div className="scores-page-notices" aria-label="Schedule notices">
            {notices.map((notice) => (
              <p className="coverage-notice" key={notice}>
                {notice}
              </p>
            ))}
          </div>
        )}
        <div className="scores-groups">
          {groups.map((group) => (
            <ScoresModule
              games={group.games}
              eyebrow={group.eyebrow}
              heading={group.label}
              headingLevel={2}
              officialDate={data.schedule.official_date}
              scoresRegionLabel={`${group.label} games for ${officialDateLabel}`}
              key={group.key}
            />
          ))}
          {groups.length === 0 && (
            <div className="scores-state scores-page-state">
              <p role="status">
                {getEmptyGamesMessage(reference, officialDateLabel)}
              </p>
            </div>
          )}
        </div>
      </main>
    )
  }

  const scoresPresentation = {
    heading: "Today's games",
    headingLevel: 1 as const,
    regionLabel: "Today's NHL games",
    getGameLink: getHomeGameLink,
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
          heading={scoresPresentation.heading}
          headingLevel={scoresPresentation.headingLevel}
          officialDate={data.schedule.official_date}
          scoresRegionLabel={scoresPresentation.regionLabel}
          getGameLink={scoresPresentation.getGameLink}
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
