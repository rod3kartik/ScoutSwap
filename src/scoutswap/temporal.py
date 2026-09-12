"""Deterministic date helpers for ScoutSwap domain records."""

from __future__ import annotations

import calendar
import re
from datetime import date
from typing import Optional


_YEAR_MONTH_PATTERN = re.compile(r"^(?P<year>\d{4})-(?P<month>\d{2})$")


def calculate_age(
    date_of_birth: Optional[date], *, as_of: date
) -> Optional[int]:
    """Return age in complete years as of an explicit date."""

    if date_of_birth is None or date_of_birth > as_of:
        return None

    age = as_of.year - date_of_birth.year
    birthday = (as_of.month, as_of.day)
    birth_month_day = (date_of_birth.month, date_of_birth.day)
    if birthday < birth_month_day:
        age -= 1
    return age


def parse_contract_until(contract_until: Optional[str]) -> Optional[date]:
    """Parse a source contract end value, returning None for missing or invalid input."""

    if contract_until is None:
        return None

    value = contract_until.strip()
    if not value:
        return None

    try:
        return date.fromisoformat(value)
    except ValueError:
        pass

    match = _YEAR_MONTH_PATTERN.fullmatch(value)
    if match is None:
        return None

    year = int(match.group("year"))
    month = int(match.group("month"))
    if month < 1 or month > 12:
        return None

    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, last_day)
