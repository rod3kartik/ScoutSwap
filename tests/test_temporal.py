from datetime import date
from typing import Optional

import pytest

from scoutswap.temporal import calculate_age, parse_contract_until


def test_calculate_age_uses_explicit_as_of_date() -> None:
    assert calculate_age(date(2000, 9, 12), as_of=date(2026, 9, 11)) == 25
    assert calculate_age(date(2000, 9, 12), as_of=date(2026, 9, 12)) == 26
    assert calculate_age(date(2000, 9, 12), as_of=date(2026, 9, 13)) == 26


@pytest.mark.parametrize("date_of_birth", [None, date(2027, 1, 1)])
def test_calculate_age_returns_none_for_missing_or_future_birth_dates(
    date_of_birth: Optional[date],
) -> None:
    assert calculate_age(date_of_birth, as_of=date(2026, 9, 12)) is None


@pytest.mark.parametrize(
    ("contract_until", "expected"),
    [
        ("2028-06-15", date(2028, 6, 15)),
        ("2028-06", date(2028, 6, 30)),
        ("2028-02", date(2028, 2, 29)),
        (" 2028-06 ", date(2028, 6, 30)),
    ],
)
def test_parse_contract_until_parses_supported_source_values(
    contract_until: str, expected: date
) -> None:
    assert parse_contract_until(contract_until) == expected


@pytest.mark.parametrize(
    "contract_until",
    [None, "", "   ", "2028", "2028-13", "2028-02-31", "June 2028"],
)
def test_parse_contract_until_returns_none_for_missing_or_invalid_values(
    contract_until: Optional[str],
) -> None:
    assert parse_contract_until(contract_until) is None
