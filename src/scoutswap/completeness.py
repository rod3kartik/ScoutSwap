"""Data-completeness scoring for ScoutSwap domain players."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol

from scoutswap.positions import NormalizedPosition


@dataclass(frozen=True)
class CompletenessWeights:
    """Explicit weights for source field coverage."""

    club: float = 0.20
    position: float = 0.25
    date_of_birth: float = 0.25
    nationality: float = 0.10
    contract_until: float = 0.10
    market_value: float = 0.10

    @property
    def total(self) -> float:
        return (
            self.club
            + self.position
            + self.date_of_birth
            + self.nationality
            + self.contract_until
            + self.market_value
        )


DEFAULT_COMPLETENESS_WEIGHTS = CompletenessWeights()


@dataclass(frozen=True)
class CompletenessComponents:
    """Boolean component coverage used to explain completeness."""

    has_club: bool
    has_known_position: bool
    has_date_of_birth: bool
    has_nationality: bool
    has_contract_until: bool
    has_market_value: bool


@dataclass(frozen=True)
class CompletenessScore:
    """Bounded completeness result with explainable components."""

    total: float
    components: CompletenessComponents


class CompletenessPlayer(Protocol):
    """Structural type for the player fields used by completeness scoring."""

    club: object
    normalized_position: NormalizedPosition
    date_of_birth: object
    nationality: Optional[str]
    contract_until: object
    market_value: object


def calculate_data_completeness(
    player: CompletenessPlayer,
    *,
    weights: CompletenessWeights = DEFAULT_COMPLETENESS_WEIGHTS,
) -> CompletenessScore:
    """Return a bounded data-completeness score for a domain player."""

    if weights.total <= 0:
        raise ValueError("Completeness weights must have a positive total")

    components = CompletenessComponents(
        has_club=player.club is not None,
        has_known_position=player.normalized_position != NormalizedPosition.UNKNOWN,
        has_date_of_birth=player.date_of_birth is not None,
        has_nationality=_has_text(player.nationality),
        has_contract_until=_has_text(player.contract_until),
        has_market_value=player.market_value is not None,
    )
    weighted_total = (
        (weights.club if components.has_club else 0.0)
        + (weights.position if components.has_known_position else 0.0)
        + (weights.date_of_birth if components.has_date_of_birth else 0.0)
        + (weights.nationality if components.has_nationality else 0.0)
        + (weights.contract_until if components.has_contract_until else 0.0)
        + (weights.market_value if components.has_market_value else 0.0)
    )
    return CompletenessScore(
        total=round(min(max(weighted_total / weights.total, 0.0), 1.0), 4),
        components=components,
    )


def _has_text(value: Optional[str]) -> bool:
    return value is not None and bool(value.strip())
