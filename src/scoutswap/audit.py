"""Safe aggregate coverage audit for football-data.org squad data."""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict, dataclass
from typing import Callable, Dict, List, Protocol

from scoutswap.client import FootballDataClient
from scoutswap.config import Settings
from scoutswap.models import CompetitionTeams, Player, Team


DEFAULT_FALLBACK_INTERVAL_SECONDS = 6.1


class AuditClient(Protocol):
    """Minimum client surface required by the audit."""

    def get_competition_teams(self, competition: str = "PL") -> CompetitionTeams:
        ...

    def get_team(self, team_id: int) -> Team:
        ...


@dataclass(frozen=True)
class FieldCoverage:
    """Aggregate availability for one source field."""

    present: int
    total: int
    percentage: float


@dataclass(frozen=True)
class AuditReport:
    """Secret-safe aggregate audit result."""

    competition: str
    teams: int
    players: int
    requests: int
    fallback_team_requests: int
    coverage: Dict[str, FieldCoverage]

    def to_dict(self) -> Dict[str, object]:
        """Return a JSON-serializable aggregate representation."""

        return asdict(self)


def audit_competition(
    client: AuditClient,
    competition: str = "PL",
    *,
    fallback_interval_seconds: float = DEFAULT_FALLBACK_INTERVAL_SECONDS,
    sleep: Callable[[float], None] = time.sleep,
) -> AuditReport:
    """Audit squad coverage without returning or printing player-level data."""

    if fallback_interval_seconds < 0:
        raise ValueError("fallback_interval_seconds must not be negative")

    competition_teams = client.get_competition_teams(competition)
    requests = 1
    fallback_requests = 0
    audited_teams: List[Team] = []

    for team in competition_teams.teams:
        if team.squad:
            audited_teams.append(team)
            continue

        sleep(fallback_interval_seconds)
        audited_teams.append(client.get_team(team.id))
        requests += 1
        fallback_requests += 1

    players = [player for team in audited_teams for player in team.squad]
    coverage = _calculate_coverage(audited_teams, players)

    return AuditReport(
        competition=competition_teams.competition.code,
        teams=len(audited_teams),
        players=len(players),
        requests=requests,
        fallback_team_requests=fallback_requests,
        coverage=coverage,
    )


def _calculate_coverage(
    teams: List[Team], players: List[Player]
) -> Dict[str, FieldCoverage]:
    total = len(players)
    players_with_club = sum(len(team.squad) for team in teams if team.id)
    counts = {
        "position": sum(player.position is not None for player in players),
        "date_of_birth": sum(player.date_of_birth is not None for player in players),
        "contract_until": sum(
            player.contract is not None and player.contract.until is not None
            for player in players
        ),
        "market_value": sum(player.market_value is not None for player in players),
        "club_association": players_with_club,
    }
    return {
        field: FieldCoverage(
            present=present,
            total=total,
            percentage=round((present / total * 100) if total else 0.0, 1),
        )
        for field, present in counts.items()
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit aggregate football-data.org squad field coverage."
    )
    parser.add_argument(
        "--competition",
        default="PL",
        help="football-data.org competition code (default: PL)",
    )
    parser.add_argument(
        "--fallback-interval-seconds",
        type=float,
        default=DEFAULT_FALLBACK_INTERVAL_SECONDS,
        help="delay between fallback team requests (default: 6.1)",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    with FootballDataClient(Settings()) as client:
        report = audit_competition(
            client,
            args.competition,
            fallback_interval_seconds=args.fallback_interval_seconds,
        )
    print(json.dumps(report.to_dict(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

