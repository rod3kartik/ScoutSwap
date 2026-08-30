import json

import httpx

from scoutswap.audit import audit_competition
from scoutswap.client import FootballDataClient
from scoutswap.config import Settings


def _player(player_id: int, *, complete: bool = True) -> dict:
    player = {
        "id": player_id,
        "name": f"Player {player_id}",
        "position": "Centre-Forward",
        "dateOfBirth": "2001-05-04",
        "marketValue": 20_000_000,
        "contract": {"until": "2028-06"},
    }
    if not complete:
        player.update(
            position=None,
            dateOfBirth=None,
            marketValue=None,
            contract=None,
        )
    return player


def test_audit_uses_squads_from_competition_response_without_fallback() -> None:
    paths = []

    def handler(request: httpx.Request) -> httpx.Response:
        paths.append(request.url.path)
        return httpx.Response(
            200,
            json={
                "count": 1,
                "competition": {"id": 2021, "name": "Premier League", "code": "PL"},
                "teams": [
                    {
                        "id": 1,
                        "name": "Example FC",
                        "squad": [_player(10), _player(11, complete=False)],
                    }
                ],
            },
        )

    settings = Settings(football_data_api_token="test-token")
    with FootballDataClient(
        settings, transport=httpx.MockTransport(handler)
    ) as client:
        report = audit_competition(client, sleep=lambda _: None)

    assert paths == ["/v4/competitions/PL/teams"]
    assert report.requests == 1
    assert report.fallback_team_requests == 0
    assert report.players == 2
    assert report.coverage["market_value"].present == 1
    assert report.coverage["market_value"].percentage == 50.0
    assert "Player 10" not in json.dumps(report.to_dict())


def test_audit_paces_team_fallback_requests_when_squads_are_absent() -> None:
    paths = []
    sleeps = []

    def handler(request: httpx.Request) -> httpx.Response:
        paths.append(request.url.path)
        if request.url.path == "/v4/competitions/PL/teams":
            return httpx.Response(
                200,
                json={
                    "count": 2,
                    "competition": {
                        "id": 2021,
                        "name": "Premier League",
                        "code": "PL",
                    },
                    "teams": [
                        {"id": 1, "name": "One FC"},
                        {"id": 2, "name": "Two FC"},
                    ],
                },
            )
        team_id = int(request.url.path.rsplit("/", 1)[1])
        return httpx.Response(
            200,
            json={
                "id": team_id,
                "name": f"Team {team_id}",
                "squad": [_player(team_id * 10)],
            },
        )

    settings = Settings(football_data_api_token="test-token")
    with FootballDataClient(
        settings, transport=httpx.MockTransport(handler)
    ) as client:
        report = audit_competition(
            client,
            fallback_interval_seconds=6.1,
            sleep=sleeps.append,
        )

    assert paths == [
        "/v4/competitions/PL/teams",
        "/v4/teams/1",
        "/v4/teams/2",
    ]
    assert sleeps == [6.1, 6.1]
    assert report.requests == 3
    assert report.fallback_team_requests == 2
    assert report.players == 2
    assert report.coverage["club_association"].percentage == 100.0


def test_audit_handles_zero_players_without_dividing_by_zero() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v4/competitions/PL/teams":
            return httpx.Response(
                200,
                json={
                    "count": 1,
                    "competition": {
                        "id": 2021,
                        "name": "Premier League",
                        "code": "PL",
                    },
                    "teams": [{"id": 1, "name": "Example FC"}],
                },
            )
        return httpx.Response(200, json={"id": 1, "name": "Example FC", "squad": []})

    settings = Settings(football_data_api_token="test-token")
    with FootballDataClient(
        settings, transport=httpx.MockTransport(handler)
    ) as client:
        report = audit_competition(
            client,
            fallback_interval_seconds=0,
            sleep=lambda _: None,
        )

    assert report.players == 0
    assert report.coverage["market_value"].percentage == 0.0

