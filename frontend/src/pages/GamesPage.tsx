import { useEffect, useMemo, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

import type { GameSummary, GamesByDateResponse } from '../api/game-types'
import { getGamesByOfficialDate } from '../api/games'
import { getCurrentContext } from '../api/home'
import { ScoresModule } from '../components/ScoresModule'
import {
  type GamesReference,
  gamesReferenceHref,
  parseGamesReference,
} from '../routing/gamesReference'

interface ScheduleGroup {
  key: string
  label: string
  eyebrow: string
  games: GameSummary[]
}

interface GamesRequestIdentity {
  pathname: string
  search: string
  retryGeneration: number
  recoverInvalid: boolean
}

type LoadState = 'loading' | 'success' | 'invalid' | 'error'

function formatGamesDateLabel(officialDate: string): string {
  return new Intl.DateTimeFormat(undefined, {
    month: 'long',
    day: 'numeric',
    year: 'numeric',
    timeZone: 'UTC',
  }).format(new Date(`${officialDate}T12:00:00Z`))
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

function getResponseNotices(schedule: GamesByDateResponse): string[] {
  return [
    schedule.capability.state === 'available'
      ? null
      : schedule.capability.explanation,
    schedule.freshness.state === 'fresh'
      ? null
      : schedule.freshness.explanation,
  ].filter(
    (notice, index, values): notice is string =>
      Boolean(notice) && values.indexOf(notice) === index,
  )
}

export function GamesPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const [schedule, setSchedule] = useState<GamesByDateResponse | null>(null)
  const [loadState, setLoadState] = useState<LoadState>('loading')
  const [retryGeneration, setRetryGeneration] = useState(0)
  const [recoverInvalid, setRecoverInvalid] = useState(false)
  const referenceResult = useMemo(
    () => parseGamesReference(location.search),
    [location.search],
  )
  const requestIdentity = useMemo<GamesRequestIdentity>(
    () => ({
      pathname: location.pathname,
      search: location.search,
      retryGeneration,
      recoverInvalid,
    }),
    [location.pathname, location.search, recoverInvalid, retryGeneration],
  )
  const [settledRequest, setSettledRequest] =
    useState<GamesRequestIdentity | null>(null)

  useEffect(() => {
    let active = true

    async function loadGames() {
      try {
        if (referenceResult.status === 'invalid' && !recoverInvalid) {
          if (active) {
            setSchedule(null)
            setLoadState('invalid')
            setSettledRequest(requestIdentity)
          }
          return
        }

        const reference =
          referenceResult.status === 'valid'
            ? referenceResult.reference
            : null
        if (
          reference &&
          `${requestIdentity.pathname}${requestIdentity.search}` !==
            gamesReferenceHref(reference)
        ) {
          navigate(gamesReferenceHref(reference), { replace: true })
          return
        }

        if (!reference) {
          const currentContext = await getCurrentContext()
          if (!active) return
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

        const response = await getGamesByOfficialDate(reference.officialDate, {
          ...(reference.seasonId === undefined
            ? {}
            : { seasonId: reference.seasonId }),
          ...(reference.gameType === undefined
            ? {}
            : { gameType: reference.gameType }),
        })
        if (!active) return

        const namedGames = response.games.filter(
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
        if (namedGames.length === response.games.length && contexts.size === 1) {
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

        setSchedule(response)
        setLoadState('success')
        setSettledRequest(requestIdentity)
      } catch {
        if (active) {
          setLoadState('error')
          setSettledRequest(requestIdentity)
        }
      }
    }

    void loadGames()

    return () => {
      active = false
    }
  }, [navigate, recoverInvalid, referenceResult, requestIdentity])

  if (settledRequest === requestIdentity && loadState === 'invalid') {
    return (
      <main className="page-content">
        <section className="scores-state" role="alert">
          <div>
            <h1>This Games link is invalid</h1>
            <p>Use Today to load the current NHL schedule.</p>
            <button type="button" onClick={() => setRecoverInvalid(true)}>
              Go to Today
            </button>
          </div>
        </section>
      </main>
    )
  }

  if (settledRequest === requestIdentity && loadState === 'error') {
    const errorHeading =
      referenceResult.status === 'valid'
        ? `We couldn't load games for ${formatGamesDateLabel(referenceResult.reference.officialDate)}`
        : "We couldn't load Games"

    return (
      <main className="page-content">
        <section className="scores-state" role="alert">
          <div>
            <h1>{errorHeading}</h1>
            <p>This looks temporary. Check your connection and try again.</p>
            <button
              type="button"
              onClick={() => setRetryGeneration((value) => value + 1)}
            >
              Try again
            </button>
          </div>
        </section>
      </main>
    )
  }

  if (
    settledRequest !== requestIdentity ||
    loadState === 'loading' ||
    !schedule
  ) {
    const loadingMessage =
      referenceResult.status === 'valid'
        ? `Loading games for ${formatGamesDateLabel(referenceResult.reference.officialDate)}…`
        : 'Loading games…'

    return (
      <main className="page-content" aria-busy="true">
        <section className="scores-state" data-testid="scores-state">
          <p role="status">{loadingMessage}</p>
        </section>
      </main>
    )
  }

  const officialDateLabel = formatGamesDateLabel(schedule.official_date)
  const groups = deriveScheduleGroups(schedule.games)
  const reference =
    referenceResult.status === 'valid'
      ? referenceResult.reference
      : { officialDate: schedule.official_date }
  const notices = getResponseNotices(schedule)

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
            officialDate={schedule.official_date}
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
