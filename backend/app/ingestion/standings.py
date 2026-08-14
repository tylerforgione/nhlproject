from nhlpy import NHLClient
from app.db.base import SessionLocal
from app.models.standing import Standing
from app.models.team import Team
from app.models.season import Season

ABBREV_OVERRIDES = {
    "CBN": "CLE",
}


def ingest_standings(season: str = None):
    client = NHLClient()
    db = SessionLocal()

    try:
        if season:
            data = client.standings.league_standings(season=season)
        else:
            data = client.standings.league_standings()

        standings = data["standings"]
        season_id = standings[0]["seasonId"]

        for s in standings:
            abbrev = s["teamAbbrev"]["default"]
            abbrev = ABBREV_OVERRIDES.get(abbrev, abbrev)
            season_year = str(season_id)[:4]

            team = (
                db.query(Team)
                .filter(
                    Team.abbrev == abbrev,
                    Team.first_season <= season_year + "9999",
                    Team.last_season >= season_year + "0000",
                )
                .first()
            )

            if not team:
                print(f"Team not found for abbrev {abbrev}, skipping")
                continue

            standing = Standing(
                team_id=team.id,
                season_id=season_id,
                clinch_indicator=s.get("clinchIndicator"),
                conference_name=s.get("conferenceName"),
                conference_abbrev=s.get("conferenceAbbrev"),
                division_name=s.get("divisionName"),
                division_abbrev=s.get("divisionAbbrev"),
                games_played=s.get("gamesPlayed"),
                wins=s.get("wins"),
                losses=s.get("losses"),
                ot_losses=s.get("otLosses"),
                ties=s.get("ties"),
                points=s.get("points"),
                point_pctg=s.get("pointPctg"),
                goal_for=s.get("goalFor"),
                goal_against=s.get("goalAgainst"),
                goal_differential=s.get("goalDifferential"),
                home_wins=s.get("homeWins"),
                home_losses=s.get("homeLosses"),
                home_ot_losses=s.get("homeOtLosses"),
                road_wins=s.get("roadWins"),
                road_losses=s.get("roadLosses"),
                road_ot_losses=s.get("roadOtLosses"),
                regulation_wins=s.get("regulationWins"),
                regulation_plus_ot_wins=s.get("regulationPlusOtWins"),
                shootout_wins=s.get("shootoutWins"),
                shootout_losses=s.get("shootoutLosses"),
                streak_code=s.get("streakCode"),
                streak_count=s.get("streakCount"),
                wildcard_sequence=s.get("wildcardSequence"),
                league_sequence=s.get("leagueSequence"),
                conference_sequence=s.get("conferenceSequence"),
                division_sequence=s.get("divisionSequence"),
                l10_wins=s.get("l10Wins"),
                l10_losses=s.get("l10Losses"),
                l10_ot_losses=s.get("l10OtLosses"),
                l10_points=s.get("l10Points"),
                l10_goal_for=s.get("l10GoalsFor"),
                l10_goal_against=s.get("l10GoalsAgainst"),
                l10_goal_differential=s.get("l10GoalDifferential"),
                home_points=s.get("homePoints"),
                road_points=s.get("roadPoints"),
                home_games_played=s.get("homeGamesPlayed"),
                road_games_played=s.get("roadGamesPlayed"),
                home_goal_for=s.get("homeGoalsFor"),
                home_goal_against=s.get("homeGoalsAgainst"),
                road_goal_for=s.get("roadGoalsFor"),
                road_goal_against=s.get("roadGoalsAgainst"),
                home_regulation_wins=s.get("homeRegulationWins"),
                road_regulation_wins=s.get("roadRegulationWins"),
                home_regulation_plus_ot_wins=s.get("homeRegulationPlusOtWins"),
                road_regulation_plus_ot_wins=s.get("roadRegulationPlusOtWins"),
            )
            db.merge(standing)

        db.commit()
        print(f"Ingested standings for season {season_id}")
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    from nhlpy import NHLClient

    client = NHLClient()
    seasons = client.standings.season_standing_manifest()

    for season in seasons:
        season_id = str(season["id"])
        print(f"Ingesting standings for {season_id}...")
        try:
            ingest_standings(season=season_id)
        except Exception as e:
            print(f"Failed for season {season_id}: {e}")
            continue
