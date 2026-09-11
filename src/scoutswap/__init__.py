"""Public package interface for ScoutSwap."""

from scoutswap.client import FootballDataClient
from scoutswap.config import Settings
from scoutswap.domain import ClubReference, DomainPlayer
from scoutswap.models import CompetitionTeams, Contract, Player, Team
from scoutswap.positions import NormalizedPosition, normalize_position

__all__ = [
    "ClubReference",
    "CompetitionTeams",
    "Contract",
    "DomainPlayer",
    "FootballDataClient",
    "NormalizedPosition",
    "Player",
    "Settings",
    "Team",
    "normalize_position",
]
