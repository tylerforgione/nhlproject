export type CapabilityState =
  | 'available'
  | 'partial'
  | 'unavailable'
  | 'unknown'

export interface Capability {
  state: CapabilityState
  explanation: string | null
}

export type SeasonPhase =
  | 'preseason'
  | 'regular-season'
  | 'playoffs'
  | 'offseason'

export interface CurrentContext {
  official_date: string
  active_season_phase: SeasonPhase
  schedule_season_id: number
  latest_completed_season_id: number | null
  games_capability: Capability
}
