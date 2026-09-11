from datetime import datetime, timezone

from scoutswap.domain import ClubReference, DomainPlayer
from scoutswap.models import Player, Team
from scoutswap.positions import NormalizedPosition


def test_domain_player_preserves_source_and_club_context() -> None:
    observed_at = datetime(2026, 9, 10, 12, 30, tzinfo=timezone.utc)
    club = Team.model_validate({"id": 1, "name": "Example FC"})
    player = Player.model_validate(
        {
            "id": 10,
            "name": "Ada Striker",
            "firstName": "Ada",
            "lastName": "Striker",
            "position": "Centre-Forward",
            "dateOfBirth": "2001-05-04",
            "nationality": "England",
            "shirtNumber": 9,
            "marketValue": 20_000_000,
            "contract": {"until": "2028-06"},
        }
    )

    domain_player = DomainPlayer.from_source(
        player, club=club, observed_at=observed_at
    )

    assert domain_player.player_id == 10
    assert domain_player.name == "Ada Striker"
    assert domain_player.club == ClubReference(club_id=1, club_name="Example FC")
    assert domain_player.source_position == "Centre-Forward"
    assert domain_player.normalized_position == NormalizedPosition.FORWARD
    assert domain_player.observed_at == observed_at
    assert domain_player.first_name == "Ada"
    assert domain_player.last_name == "Striker"
    assert domain_player.date_of_birth is not None
    assert domain_player.date_of_birth.isoformat() == "2001-05-04"
    assert domain_player.nationality == "England"
    assert domain_player.shirt_number == 9
    assert domain_player.market_value == 20_000_000
    assert domain_player.contract_until == "2028-06"


def test_domain_player_allows_missing_optional_source_fields() -> None:
    observed_at = datetime(2026, 9, 10, tzinfo=timezone.utc)
    club = Team.model_validate({"id": 2, "name": "Sparse FC"})
    player = Player.model_validate(
        {
            "id": 11,
            "name": "Sparse Player",
            "position": None,
            "dateOfBirth": None,
            "marketValue": None,
            "contract": None,
        }
    )

    domain_player = DomainPlayer.from_source(
        player, club=club, observed_at=observed_at
    )

    assert domain_player.player_id == 11
    assert domain_player.club.club_id == 2
    assert domain_player.source_position is None
    assert domain_player.normalized_position == NormalizedPosition.UNKNOWN
    assert domain_player.date_of_birth is None
    assert domain_player.market_value is None
    assert domain_player.contract_until is None
