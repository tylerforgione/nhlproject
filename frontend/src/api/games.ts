import { requestJson } from './client'
import type { GamesByDateResponse, GameType } from './game-types'

export interface GamesByOfficialDateFilters {
  seasonId?: number
  gameType?: GameType
}

export async function getGamesByOfficialDate(
  officialDate: string,
  filters: GamesByOfficialDateFilters = {},
): Promise<GamesByDateResponse> {
  const query = new URLSearchParams({ official_date: officialDate })

  if (filters.seasonId !== undefined) {
    query.set('season_id', String(filters.seasonId))
  }

  if (filters.gameType !== undefined) {
    query.set('game_type', filters.gameType)
  }

  return requestJson<GamesByDateResponse>(`/api/v1/games?${query}`)
}
