import { requestJson } from './client'
import type { GamesByDateResponse } from './game-types'

export async function getGamesByOfficialDate(
  officialDate: string,
): Promise<GamesByDateResponse> {
  const query = new URLSearchParams({ official_date: officialDate })
  return requestJson<GamesByDateResponse>(`/api/v1/games?${query}`)
}
