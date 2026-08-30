import type { GameSummary, GameType } from '../api/game-types'

export interface GamesReferenceState {
  officialDate: string
  seasonId: number
  gameType: GameType
}

const gameTypes = new Set<GameType>([
  'preseason',
  'regular-season',
  'playoffs',
  'unknown',
])

function isOfficialDate(value: string | null): value is string {
  if (!value || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return false

  const parsed = new Date(`${value}T12:00:00Z`)
  return !Number.isNaN(parsed.valueOf()) && parsed.toISOString().startsWith(value)
}

export function parseGamesReference(search: string): GamesReferenceState | null {
  const parameters = new URLSearchParams(search)
  const officialDate = parameters.get('date')
  const season = parameters.get('season')
  const gameType = parameters.get('gameType') as GameType | null

  if (
    !isOfficialDate(officialDate) ||
    !season ||
    !/^\d{8}$/.test(season) ||
    !gameType ||
    !gameTypes.has(gameType)
  ) {
    return null
  }

  return { officialDate, seasonId: Number(season), gameType }
}

export function gamesReferenceHref(game: GameSummary): string {
  const parameters = new URLSearchParams({
    date: game.official_date,
    season: String(game.season_id),
    gameType: game.game_type,
  })

  return `/games?${parameters}`
}
