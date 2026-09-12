"""Public package interface for ScoutSwap."""

from scoutswap.client import FootballDataClient
from scoutswap.completeness import (
    CompletenessComponents,
    CompletenessScore,
    CompletenessWeights,
    DEFAULT_COMPLETENESS_WEIGHTS,
)
from scoutswap.config import Settings
from scoutswap.domain import ClubReference, DomainPlayer
from scoutswap.models import CompetitionTeams, Contract, Player, Team
from scoutswap.positions import NormalizedPosition

__all__ = [
    "ClubReference",
    "CompletenessComponents",
    "CompletenessScore",
    "CompletenessWeights",
    "CompetitionTeams",
    "Contract",
    "DEFAULT_COMPLETENESS_WEIGHTS",
    "DomainPlayer",
    "FootballDataClient",
    "NormalizedPosition",
    "Player",
    "Settings",
    "Team",
]
