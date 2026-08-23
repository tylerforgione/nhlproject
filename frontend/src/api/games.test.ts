import { afterEach, describe, expect, it, vi } from 'vitest'

import { getGamesByOfficialDate } from './games'

describe('games API', () => {
  afterEach(() => vi.unstubAllGlobals())

  it('loads games using the NHL official game date', async () => {
    const payload = {
      official_date: '2026-01-15',
      capability: { state: 'available', explanation: null },
      games: [],
    }
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: vi.fn().mockResolvedValue(payload),
    })
    vi.stubGlobal('fetch', fetchMock)

    const result = await getGamesByOfficialDate('2026-01-15')

    expect(fetchMock).toHaveBeenCalledWith(
      '/api/v1/games?official_date=2026-01-15',
      { headers: { Accept: 'application/json' } },
    )
    expect(result).toEqual(payload)
  })
})
