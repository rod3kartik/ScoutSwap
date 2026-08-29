from scoutswap.models import Team


def test_team_parses_camel_case_player_fields() -> None:
    team = Team.model_validate(
        {
            "id": 1,
            "name": "Example FC",
            "shortName": "Example",
            "marketValue": 50_000_000,
            "squad": [
                {
                    "id": 10,
                    "name": "Ada Striker",
                    "position": "Centre-Forward",
                    "dateOfBirth": "2001-05-04",
                    "marketValue": 20_000_000,
                    "contract": {"start": "2024-07", "until": "2028-06"},
                }
            ],
        }
    )

    assert team.short_name == "Example"
    assert team.squad[0].market_value == 20_000_000
    assert team.squad[0].date_of_birth.year == 2001

