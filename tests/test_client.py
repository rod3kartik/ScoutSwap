import httpx

from scoutswap.client import FootballDataClient
from scoutswap.config import Settings


def test_get_competition_teams_sends_auth_header() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["X-Auth-Token"] == "test-token"
        assert request.url.path == "/v4/competitions/PL/teams"
        return httpx.Response(
            200,
            json={
                "count": 1,
                "competition": {"id": 2021, "name": "Premier League", "code": "PL"},
                "teams": [{"id": 1, "name": "Example FC", "squad": []}],
            },
        )

    settings = Settings(football_data_api_token="test-token")
    with FootballDataClient(
        settings, transport=httpx.MockTransport(handler)
    ) as client:
        result = client.get_competition_teams()

    assert result.competition.code == "PL"
    assert result.teams[0].name == "Example FC"

