import pytest

from scoutswap.positions import NormalizedPosition, normalize_position


@pytest.mark.parametrize(
    ("source_position", "expected"),
    [
        ("Goalkeeper", NormalizedPosition.GOALKEEPER),
        ("Defence", NormalizedPosition.DEFENDER),
        ("Centre-Back", NormalizedPosition.DEFENDER),
        ("Left-Back", NormalizedPosition.DEFENDER),
        ("Right-Back", NormalizedPosition.DEFENDER),
        ("Midfield", NormalizedPosition.MIDFIELDER),
        ("Defensive Midfield", NormalizedPosition.MIDFIELDER),
        ("Central Midfield", NormalizedPosition.MIDFIELDER),
        ("Attacking Midfield", NormalizedPosition.MIDFIELDER),
        ("Offence", NormalizedPosition.FORWARD),
        ("Centre-Forward", NormalizedPosition.FORWARD),
        ("Left-Winger", NormalizedPosition.FORWARD),
        ("Right-Winger", NormalizedPosition.FORWARD),
    ],
)
def test_normalize_position_maps_known_source_positions(
    source_position: str, expected: NormalizedPosition
) -> None:
    assert normalize_position(source_position) == expected


def test_normalize_position_ignores_case_and_extra_whitespace() -> None:
    assert normalize_position("  central   midfield  ") == NormalizedPosition.MIDFIELDER


@pytest.mark.parametrize("source_position", [None, "", "   ", "Sweeper"])
def test_normalize_position_uses_unknown_for_missing_or_unmapped_values(
    source_position: str
) -> None:
    assert normalize_position(source_position) == NormalizedPosition.UNKNOWN
