"""Domain models for ScoutSwap's player recommendation data."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

from scoutswap.models import Player as SourcePlayer
from scoutswap.models import Team as SourceTeam
from scoutswap.positions import NormalizedPosition, normalize_position
from scoutswap.temporal import calculate_age, parse_contract_until


@dataclass(frozen=True)
class ClubReference:
    """Club identity captured with a player observation."""

    club_id: int
    club_name: str


@dataclass(frozen=True)
class DomainPlayer:
    """ScoutSwap player record independent of upstream API payload shape."""

    player_id: int
    name: str
    club: ClubReference
    source_position: Optional[str]
    normalized_position: NormalizedPosition
    observed_at: datetime
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    nationality: Optional[str] = None
    shirt_number: Optional[int] = None
    market_value: Optional[int] = None
    contract_until: Optional[str] = None

    def age_on(self, as_of: date) -> Optional[int]:
        """Return age in complete years on an explicit date."""

        return calculate_age(self.date_of_birth, as_of=as_of)

    def contract_end_date(self) -> Optional[date]:
        """Return the parsed contract end date when the source value is usable."""

        return parse_contract_until(self.contract_until)

    @classmethod
    def from_source(
        cls,
        player: SourcePlayer,
        *,
        club: SourceTeam,
        observed_at: datetime,
    ) -> "DomainPlayer":
        """Create a domain player from a football-data.org squad record."""

        contract_until = player.contract.until if player.contract is not None else None
        return cls(
            player_id=player.id,
            name=player.name,
            first_name=player.first_name,
            last_name=player.last_name,
            club=ClubReference(club_id=club.id, club_name=club.name),
            source_position=player.position,
            normalized_position=normalize_position(player.position),
            date_of_birth=player.date_of_birth,
            nationality=player.nationality,
            shirt_number=player.shirt_number,
            market_value=player.market_value,
            contract_until=contract_until,
            observed_at=observed_at,
        )
