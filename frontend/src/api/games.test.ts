import { afterEach, describe, expect, it, vi } from 'vitest'

import type { GamesByDateResponse } from './game-types'
import { getGamesByOfficialDate } from './games'

const payload = {
  official_date: '2026-01-15',
  capability: { state: 'available', explanation: null },
  season_id: 20252026,
  game_type: 'regular-season',
  freshness: {
    state: 'unknown',
    updated_at: null,
    explanation: 'Schedule freshness has not been verified.',
  },
  games: [],
} satisfies GamesByDateResponse

function stubSuccessfulFetch() {
  const fetchMock = vi.fn().mockResolvedValue({
    ok: true,
    json: vi.fn().mockResolvedValue(payload),
  })
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

describe('games API', () => {
  afterEach(() => vi.unstubAllGlobals())

  it('loads games using the NHL official game date', async () => {
    const fetchMock = stubSuccessfulFetch()

    const result = await getGamesByOfficialDate('2026-01-15')

    expect(fetchMock).toHaveBeenCalledWith(
      '/api/v1/games?official_date=2026-01-15',
      { headers: { Accept: 'application/json' } },
    )
    expect(result).toEqual(payload)
  })

  it('includes stable season and game-type reference filters', async () => {
    const fetchMock = stubSuccessfulFetch()

    await getGamesByOfficialDate('2026-01-15', {
      seasonId: 20252026,
      gameType: 'regular-season',
    })

    expect(fetchMock).toHaveBeenCalledWith(
      '/api/v1/games?official_date=2026-01-15&season_id=20252026&game_type=regular-season',
      { headers: { Accept: 'application/json' } },
    )
  })
})
