"""Position normalization for ScoutSwap domain players."""

from __future__ import annotations

from enum import Enum
from typing import Optional


class NormalizedPosition(str, Enum):
    """Canonical position groups used by ScoutSwap scoring and storage."""

    GOALKEEPER = "GOALKEEPER"
    DEFENDER = "DEFENDER"
    MIDFIELDER = "MIDFIELDER"
    FORWARD = "FORWARD"
    UNKNOWN = "UNKNOWN"


_SOURCE_POSITION_MAP = {
    "attacking midfield": NormalizedPosition.MIDFIELDER,
    "central midfield": NormalizedPosition.MIDFIELDER,
    "centre-back": NormalizedPosition.DEFENDER,
    "centre-forward": NormalizedPosition.FORWARD,
    "defence": NormalizedPosition.DEFENDER,
    "defender": NormalizedPosition.DEFENDER,
    "defensive midfield": NormalizedPosition.MIDFIELDER,
    "forward": NormalizedPosition.FORWARD,
    "goalkeeper": NormalizedPosition.GOALKEEPER,
    "left midfield": NormalizedPosition.MIDFIELDER,
    "left-back": NormalizedPosition.DEFENDER,
    "left-winger": NormalizedPosition.FORWARD,
    "midfield": NormalizedPosition.MIDFIELDER,
    "midfielder": NormalizedPosition.MIDFIELDER,
    "offence": NormalizedPosition.FORWARD,
    "right midfield": NormalizedPosition.MIDFIELDER,
    "right-back": NormalizedPosition.DEFENDER,
    "right-winger": NormalizedPosition.FORWARD,
    "second striker": NormalizedPosition.FORWARD,
}


def normalize_position(source_position: Optional[str]) -> NormalizedPosition:
    """Map a source position label to ScoutSwap's canonical vocabulary."""

    if source_position is None:
        return NormalizedPosition.UNKNOWN

    normalized_key = " ".join(source_position.strip().lower().split())
    if not normalized_key:
        return NormalizedPosition.UNKNOWN
    return _SOURCE_POSITION_MAP.get(normalized_key, NormalizedPosition.UNKNOWN)
