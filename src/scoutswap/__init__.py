"""Public package interface for ScoutSwap."""

from scoutswap.client import FootballDataClient
from scoutswap.config import Settings
from scoutswap.domain import ClubReference, DomainPlayer
from scoutswap.models import CompetitionTeams, Contract, Player, Team

__all__ = [
    "ClubReference",
    "CompetitionTeams",
    "Contract",
    "DomainPlayer",
    "FootballDataClient",
    "Player",
    "Settings",
    "Team",
]
