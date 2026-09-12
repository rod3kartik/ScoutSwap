from datetime import date, datetime, timezone
from typing import Optional

import pytest

from scoutswap.completeness import (
    CompletenessWeights,
    calculate_data_completeness,
)
from scoutswap.domain import ClubReference, DomainPlayer
from scoutswap.positions import NormalizedPosition


def _domain_player(
    *,
    normalized_position: NormalizedPosition = NormalizedPosition.FORWARD,
    date_of_birth: Optional[date] = date(2001, 5, 4),
    nationality: Optional[str] = "England",
    contract_until: Optional[str] = "2028-06",
    market_value: Optional[int] = 20_000_000,
) -> DomainPlayer:
    return DomainPlayer(
        player_id=10,
        name="Ada Striker",
        club=ClubReference(club_id=1, club_name="Example FC"),
        source_position="Centre-Forward",
        normalized_position=normalized_position,
        observed_at=datetime(2026, 9, 12, tzinfo=timezone.utc),
        date_of_birth=date_of_birth,
        nationality=nationality,
        contract_until=contract_until,
        market_value=market_value,
    )


def test_complete_record_gets_full_completeness_score() -> None:
    score = calculate_data_completeness(_domain_player())

    assert score.total == 1.0
    assert score.components.has_club is True
    assert score.components.has_known_position is True
    assert score.components.has_date_of_birth is True
    assert score.components.has_nationality is True
    assert score.components.has_contract_until is True
    assert score.components.has_market_value is True


def test_partial_record_reports_component_flags_and_bounded_score() -> None:
    player = _domain_player(
        normalized_position=NormalizedPosition.UNKNOWN,
        nationality=" ",
        contract_until="",
        market_value=None,
    )

    score = player.data_completeness()

    assert score.total == 0.45
    assert score.components.has_club is True
    assert score.components.has_known_position is False
    assert score.components.has_date_of_birth is True
    assert score.components.has_nationality is False
    assert score.components.has_contract_until is False
    assert score.components.has_market_value is False


def test_sparse_record_keeps_only_available_component_credit() -> None:
    player = _domain_player(
        normalized_position=NormalizedPosition.UNKNOWN,
        date_of_birth=None,
        nationality=None,
        contract_until=None,
        market_value=None,
    )

    score = player.data_completeness()

    assert score.total == 0.2
    assert score.components.has_club is True
    assert score.components.has_known_position is False
    assert score.components.has_date_of_birth is False
    assert score.components.has_nationality is False
    assert score.components.has_contract_until is False
    assert score.components.has_market_value is False


def test_custom_weights_are_normalized_to_a_bounded_score() -> None:
    score = calculate_data_completeness(
        _domain_player(market_value=None),
        weights=CompletenessWeights(
            club=2,
            position=2,
            date_of_birth=2,
            nationality=2,
            contract_until=2,
            market_value=10,
        ),
    )

    assert score.total == 0.5


def test_zero_total_weights_are_rejected() -> None:
    with pytest.raises(ValueError, match="positive total"):
        calculate_data_completeness(
            _domain_player(),
            weights=CompletenessWeights(
                club=0,
                position=0,
                date_of_birth=0,
                nationality=0,
                contract_until=0,
                market_value=0,
            ),
        )
