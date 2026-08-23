import { afterEach, describe, expect, it, vi } from 'vitest'

import { getCurrentContext } from './home'

describe('home API', () => {
  afterEach(() => vi.unstubAllGlobals())

  it('loads the public current context contract', async () => {
    const payload = {
      official_date: '2026-01-15',
      active_season_phase: 'regular-season',
      schedule_season_id: 20252026,
      latest_completed_season_id: 20242025,
      games_capability: { state: 'available', explanation: null },
    }
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: vi.fn().mockResolvedValue(payload),
    })
    vi.stubGlobal('fetch', fetchMock)

    const result = await getCurrentContext()

    expect(fetchMock).toHaveBeenCalledWith('/api/v1/current-context', {
      headers: { Accept: 'application/json' },
    })
    expect(result).toEqual(payload)
  })
})
