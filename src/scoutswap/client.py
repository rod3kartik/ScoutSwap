"""Client for the subset of football-data.org used by ScoutSwap."""

from __future__ import annotations

from typing import Any

import httpx

from scoutswap.config import Settings
from scoutswap.exceptions import FootballDataError
from scoutswap.models import CompetitionTeams, Team


class FootballDataClient:
    """Small synchronous v4 API client with typed responses."""

    def __init__(
        self,
        settings: Settings,
        *,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._client = httpx.Client(
            base_url=settings.football_data_base_url.rstrip("/"),
            headers={
                "X-Auth-Token": settings.football_data_api_token.get_secret_value(),
                "Accept": "application/json",
                "User-Agent": "ScoutSwap/0.1",
            },
            timeout=settings.request_timeout_seconds,
            transport=transport,
        )

    def __enter__(self) -> "FootballDataClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    def get_competition_teams(
        self, competition: str = "PL", *, season: int | None = None
    ) -> CompetitionTeams:
        params = {"season": season} if season is not None else None
        payload = self._get(f"/competitions/{competition}/teams", params=params)
        return CompetitionTeams.model_validate(payload)

    def get_team(self, team_id: int) -> Team:
        return Team.model_validate(self._get(f"/teams/{team_id}"))

    def _get(
        self, path: str, *, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        try:
            response = self._client.get(path, params=params)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            detail = _safe_error_detail(exc.response)
            raise FootballDataError(
                f"football-data.org returned {exc.response.status_code}: {detail}"
            ) from exc
        except httpx.HTTPError as exc:
            raise FootballDataError(f"Could not reach football-data.org: {exc}") from exc

        payload = response.json()
        if not isinstance(payload, dict):
            raise FootballDataError("football-data.org returned an unexpected response")
        return payload


def _safe_error_detail(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        return response.reason_phrase
    if isinstance(payload, dict):
        return str(payload.get("message") or payload.get("error") or response.reason_phrase)
    return response.reason_phrase
