import type { Capability, Freshness } from './types'

export type GameType =
  | 'preseason'
  | 'regular-season'
  | 'playoffs'
  | 'unknown'
export type GameState = 'scheduled' | 'live' | 'final' | 'unknown'

export interface TeamReference {
  id: number
  name: string
  abbreviation: string
  logo_url: string | null
  dark_logo_url: string | null
}

export interface GameSummary {
  id: number
  season_id: number
  game_type: GameType
  state: GameState
  official_date: string
  start_time_utc: string | null
  away_team: TeamReference
  home_team: TeamReference
  away_score: number | null
  home_score: number | null
  venue: string | null
  venue_timezone: string | null
  neutral_site: boolean
}

export interface GamesByDateResponse {
  official_date: string
  capability: Capability
  season_id: number | null
  game_type: GameType | null
  freshness: Freshness
  games: GameSummary[]
}
