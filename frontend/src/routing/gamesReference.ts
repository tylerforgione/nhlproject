import type { GameSummary, GameType } from '../api/game-types'

export type GamesReferenceGameType = Exclude<GameType, 'unknown'>

export interface GamesReference {
  officialDate: string
  seasonId?: number
  gameType?: GamesReferenceGameType
}

export type GamesReferenceParseResult =
  | { status: 'absent' }
  | { status: 'invalid' }
  | { status: 'valid'; reference: GamesReference }

const gameTypes = new Set<GamesReferenceGameType>([
  'preseason',
  'regular-season',
  'playoffs',
])

function isOfficialDate(value: string | null): value is string {
  if (!value || !/^\d{4}-\d{2}-\d{2}$/.test(value) || value.startsWith('0000')) {
    return false
  }

  const parsed = new Date(`${value}T12:00:00Z`)
  return !Number.isNaN(parsed.valueOf()) && parsed.toISOString().startsWith(value)
}

function isScheduleSeason(value: string): boolean {
  if (!/^\d{8}$/.test(value)) return false

  const startYear = Number(value.slice(0, 4))
  const endYear = Number(value.slice(4))
  return startYear >= 1 && startYear <= 9998 && endYear === startYear + 1
}

export function parseGamesReference(search: string): GamesReferenceParseResult {
  const parameters = new URLSearchParams(search)
  const knownNames = ['date', 'season', 'gameType']
  const knownValues = knownNames.flatMap((name) => parameters.getAll(name))
  if (knownValues.length === 0) return { status: 'absent' }
  if (knownNames.some((name) => parameters.getAll(name).length > 1)) {
    return { status: 'invalid' }
  }

  const officialDate = parameters.get('date')
  const season = parameters.get('season')
  const gameType = parameters.get('gameType')

  if (
    !isOfficialDate(officialDate) ||
    (season !== null && !isScheduleSeason(season)) ||
    (gameType !== null &&
      !gameTypes.has(gameType as GamesReferenceGameType))
  ) {
    return { status: 'invalid' }
  }

  const reference: GamesReference = { officialDate }
  if (season !== null) reference.seasonId = Number(season)
  if (gameType !== null) {
    reference.gameType = gameType as GamesReferenceGameType
  }

  return {
    status: 'valid',
    reference,
  }
}

export function serializeGamesReference(reference: GamesReference): string {
  const parameters = new URLSearchParams({ date: reference.officialDate })
  if (reference.seasonId !== undefined) {
    parameters.set('season', String(reference.seasonId).padStart(8, '0'))
  }
  if (reference.gameType !== undefined) {
    parameters.set('gameType', reference.gameType)
  }

  return parameters.toString()
}

export function gamesReferenceHref(reference: GamesReference): string {
  return `/games?${serializeGamesReference(reference)}`
}

export function gamesReferenceFromGame(game: GameSummary): GamesReference | null {
  const season = String(game.season_id).padStart(8, '0')
  if (
    !isOfficialDate(game.official_date) ||
    !Number.isInteger(game.season_id) ||
    !isScheduleSeason(season)
  ) {
    return null
  }

  const reference: GamesReference = {
    officialDate: game.official_date,
    seasonId: game.season_id,
  }
  if (game.game_type !== 'unknown') reference.gameType = game.game_type
  return reference
}

function moveOfficialDate(value: string, offset: -1 | 1): string | null {
  if (!isOfficialDate(value)) return null

  const [year, month, day] = value.split('-').map(Number)
  const moved = new Date(0)
  moved.setUTCHours(0, 0, 0, 0)
  moved.setUTCFullYear(year, month - 1, day)
  moved.setUTCDate(moved.getUTCDate() + offset)

  const movedYear = moved.getUTCFullYear()
  if (movedYear < 1 || movedYear > 9999) return null

  const movedMonth = String(moved.getUTCMonth() + 1).padStart(2, '0')
  const movedDay = String(moved.getUTCDate()).padStart(2, '0')
  return `${String(movedYear).padStart(4, '0')}-${movedMonth}-${movedDay}`
}

export function previousOfficialDate(value: string): string | null {
  return moveOfficialDate(value, -1)
}

export function nextOfficialDate(value: string): string | null {
  return moveOfficialDate(value, 1)
}
