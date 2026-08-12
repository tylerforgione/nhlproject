import json
from app.db.base import SessionLocal
from app.models.team import Team


def seed_teams(json_path: str):
    db = SessionLocal()
    try:
        with open(json_path, "r") as f:
            data = json.load(f)

        for team_id, info in data.items:
            team = Team(
                id=int(team_id),
                name=info["name"],
                abbrev=info["abbrev"],
                logo=info["logo"],
                dark_logo=info["dark_logo"],
                first_season=info["first_season"],
                last_season=info["last_season"],
                is_active=info["last_season"] == "20252026",
            )
            db.merge(team)
        db.commit()
        print(f"Seeded {len(data)} teams")
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_teams("/workspace/backend/app/data/historical_teams.json")
