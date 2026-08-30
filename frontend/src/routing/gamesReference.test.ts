import { describe, expect, it } from 'vitest'

import { gameSummaryFixture } from '../test/appApiMocks'
import {
  gamesReferenceFromGame,
  gamesReferenceHref,
  nextOfficialDate,
  parseGamesReference,
  previousOfficialDate,
  serializeGamesReference,
} from './gamesReference'

describe('parseGamesReference', () => {
  it('parses a complete Games Reference', () => {
    expect(
      parseGamesReference(
        '?date=2026-01-15&season=20252026&gameType=regular-season',
      ),
    ).toEqual({
      status: 'valid',
      reference: {
        officialDate: '2026-01-15',
        seasonId: 20252026,
        gameType: 'regular-season',
      },
    })
  })

  it.each([
    ['?date=2026-01-15', { officialDate: '2026-01-15' }],
    [
      '?season=20252026&date=2026-01-15',
      { officialDate: '2026-01-15', seasonId: 20252026 },
    ],
    [
      '?gameType=playoffs&date=2026-05-01',
      { officialDate: '2026-05-01', gameType: 'playoffs' },
    ],
  ])('parses independently optional fields from %s', (search, reference) => {
    expect(parseGamesReference(search)).toEqual({ status: 'valid', reference })
  })

  it.each(['', '?utm_source=home&utm_source=duplicate', '?Date=2026-01-15'])(
    'classifies search without known fields as absent for %s',
    (search) => {
      expect(parseGamesReference(search)).toEqual({ status: 'absent' })
    },
  )

  it.each([
    '?date=',
    '?date=2026-1-15',
    '?date=2026-13-01',
    '?date=2026-04-31',
    '?date=2025-02-29',
    '?date=0000-01-01',
    '?season=20252026',
    '?gameType=playoffs',
  ])('rejects an invalid or missing Official Game Date from %s', (search) => {
    expect(parseGamesReference(search)).toEqual({ status: 'invalid' })
  })

  it.each(['?date=0001-01-01', '?date=2024-02-29', '?date=9999-12-31'])(
    'accepts the supported Official Game Date %s',
    (search) => {
      expect(parseGamesReference(search).status).toBe('valid')
    },
  )

  it.each([
    '2025202',
    '202520260',
    '2025A026',
    '20252025',
    '20252027',
    '00000001',
    '99990000',
  ])('rejects the malformed Schedule Season %s', (season) => {
    expect(parseGamesReference(`?date=2026-01-15&season=${season}`)).toEqual({
      status: 'invalid',
    })
  })

  it.each([
    ['00010002', 10002],
    ['20252026', 20252026],
    ['99989999', 99989999],
  ])('accepts the Schedule Season %s', (season, seasonId) => {
    expect(
      parseGamesReference(`?date=2026-01-15&season=${season}`),
    ).toEqual({
      status: 'valid',
      reference: { officialDate: '2026-01-15', seasonId },
    })
  })

  it.each(['unknown', 'Regular-season', ' playoffs', 'other', ''])(
    'rejects unsupported explicit Game Type %j',
    (gameType) => {
      expect(
        parseGamesReference(`?date=2026-01-15&gameType=${gameType}`),
      ).toEqual({ status: 'invalid' })
    },
  )

  it.each([
    '?date=2026-01-15&date=2026-01-15',
    '?date=2026-01-15&date=2026-01-16',
    '?date=2026-01-15&season=20252026&season=20252026',
    '?date=2026-01-15&gameType=playoffs&gameType=playoffs',
  ])('rejects duplicate known parameters from %s', (search) => {
    expect(parseGamesReference(search)).toEqual({ status: 'invalid' })
  })
})

describe('Games Reference serialization', () => {
  it('serializes canonical names and ordering', () => {
    const reference = {
      officialDate: '2026-01-15',
      seasonId: 20252026,
      gameType: 'regular-season' as const,
    }

    expect(serializeGamesReference(reference)).toBe(
      'date=2026-01-15&season=20252026&gameType=regular-season',
    )
    expect(gamesReferenceHref(reference)).toBe(
      '/games?date=2026-01-15&season=20252026&gameType=regular-season',
    )
  })

  it.each([
    [{ officialDate: '2026-01-15' }, 'date=2026-01-15'],
    [
      { officialDate: '2026-01-15', seasonId: 10002 },
      'date=2026-01-15&season=00010002',
    ],
    [
      { officialDate: '2026-01-15', gameType: 'playoffs' as const },
      'date=2026-01-15&gameType=playoffs',
    ],
  ])('omits absent optional fields from %#', (reference, expected) => {
    expect(serializeGamesReference(reference)).toBe(expected)
  })

  it('discards unrelated parameters after parsing', () => {
    const result = parseGamesReference(
      '?utm_source=home&gameType=playoffs&date=2026-05-01&extra=value',
    )

    expect(result.status).toBe('valid')
    if (result.status !== 'valid') return
    expect(serializeGamesReference(result.reference)).toBe(
      'date=2026-05-01&gameType=playoffs',
    )
  })
})

describe('gamesReferenceFromGame', () => {
  it('converts a game with a named Game Type into a complete reference', () => {
    expect(gamesReferenceFromGame(gameSummaryFixture())).toEqual({
      officialDate: '2026-01-15',
      seasonId: 20252026,
      gameType: 'regular-season',
    })
  })

  it('omits an unknown upstream Game Type', () => {
    const reference = gamesReferenceFromGame(
      gameSummaryFixture({ game_type: 'unknown' }),
    )

    expect(reference).toEqual({
      officialDate: '2026-01-15',
      seasonId: 20252026,
    })
    expect(reference && gamesReferenceHref(reference)).toBe(
      '/games?date=2026-01-15&season=20252026',
    )
  })

  it.each([
    { official_date: '2026-02-30' },
    { season_id: 20252025 },
    { season_id: -1 },
  ])('rejects malformed API reference data from %#', (overrides) => {
    expect(gamesReferenceFromGame(gameSummaryFixture(overrides))).toBeNull()
  })
})

describe('Official Game Date arithmetic', () => {
  it.each([
    ['2026-01-15', '2026-01-14'],
    ['2026-03-01', '2026-02-28'],
    ['2025-01-01', '2024-12-31'],
    ['2024-03-01', '2024-02-29'],
    ['2024-02-29', '2024-02-28'],
    ['2024-03-10', '2024-03-09'],
    ['2024-11-03', '2024-11-02'],
  ])('moves from %s to the previous calendar day', (value, expected) => {
    expect(previousOfficialDate(value)).toBe(expected)
  })

  it.each([
    ['2026-01-15', '2026-01-16'],
    ['2026-01-31', '2026-02-01'],
    ['2024-12-31', '2025-01-01'],
    ['2024-02-28', '2024-02-29'],
    ['2024-02-29', '2024-03-01'],
    ['2024-03-10', '2024-03-11'],
    ['2024-11-03', '2024-11-04'],
  ])('moves from %s to the next calendar day', (value, expected) => {
    expect(nextOfficialDate(value)).toBe(expected)
  })

  it.each(['', '2026-02-30', '2026-1-15', '0000-12-31'])(
    'rejects invalid arithmetic input %j',
    (value) => {
      expect(previousOfficialDate(value)).toBeNull()
      expect(nextOfficialDate(value)).toBeNull()
    },
  )

  it('rejects movement outside the supported year range', () => {
    expect(previousOfficialDate('0001-01-01')).toBeNull()
    expect(nextOfficialDate('9999-12-31')).toBeNull()
  })
})
