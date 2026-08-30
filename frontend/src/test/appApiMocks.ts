import { vi } from 'vitest'

import type { GameSummary, GamesByDateResponse } from '../api/game-types'
import type { GamesByOfficialDateFilters } from '../api/games'
import type { CurrentContext } from '../api/types'

const hoistedAppApiMocks = vi.hoisted(() => ({
  getCurrentContext: vi.fn<() => Promise<CurrentContext>>(),
  getGamesByOfficialDate:
    vi.fn<
      (
        officialDate: string,
        filters?: GamesByOfficialDateFilters,
      ) => Promise<GamesByDateResponse>
    >(),
}))

export const appApiMocks = hoistedAppApiMocks

vi.mock('../api/home', () => ({
  getCurrentContext: appApiMocks.getCurrentContext,
}))

vi.mock('../api/games', () => ({
  getGamesByOfficialDate: appApiMocks.getGamesByOfficialDate,
}))

export function resetAppApiMocks() {
  appApiMocks.getCurrentContext.mockReset()
  appApiMocks.getGamesByOfficialDate.mockReset()
}

export function currentContextFixture(
  overrides: Partial<CurrentContext> = {},
): CurrentContext {
  return {
    official_date: '2026-01-15',
    active_season_phase: 'regular-season',
    schedule_season_id: 20252026,
    latest_completed_season_id: 20242025,
    games_capability: { state: 'available', explanation: null },
    ...overrides,
  }
}

export function gamesResponseFixture(
  overrides: Partial<GamesByDateResponse> = {},
): GamesByDateResponse {
  return {
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
    ...overrides,
  }
}

export function gameSummaryFixture(
  overrides: Partial<GameSummary> = {},
): GameSummary {
  return {
    id: 2025020710,
    season_id: 20252026,
    game_type: 'regular-season',
    state: 'scheduled',
    official_date: '2026-01-15',
    start_time_utc: '2026-01-16T00:30:00Z',
    away_team: {
      id: 1,
      name: 'Boston Bruins',
      abbreviation: 'BOS',
      logo_url: null,
      dark_logo_url: null,
    },
    home_team: {
      id: 2,
      name: 'New York Rangers',
      abbreviation: 'NYR',
      logo_url: null,
      dark_logo_url: null,
    },
    away_score: null,
    home_score: null,
    venue: 'Madison Square Garden',
    venue_timezone: 'America/New_York',
    neutral_site: false,
    ...overrides,
  }
}
