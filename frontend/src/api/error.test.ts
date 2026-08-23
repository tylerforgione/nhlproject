import { afterEach, expect, it, vi } from 'vitest'

import { getGamesByOfficialDate } from './games'

afterEach(() => vi.unstubAllGlobals())

it('normalizes a structured backend error', async () => {
  vi.stubGlobal(
    'fetch',
    vi.fn().mockResolvedValue({
      ok: false,
      status: 503,
      json: vi.fn().mockResolvedValue({
        error: {
          code: 'games_unavailable',
          message: 'Games are temporarily unavailable',
          details: [],
        },
      }),
    }),
  )

  await expect(getGamesByOfficialDate('2026-01-15')).rejects.toMatchObject({
    name: 'ApiError',
    status: 503,
    code: 'games_unavailable',
    message: 'Games are temporarily unavailable',
  })
})
