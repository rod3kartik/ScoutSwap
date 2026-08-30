# ScoutSwap

ScoutSwap is a Python package for finding value-conscious replacement football
players using data from football-data.org.

## Setup

Create a `.env` file in the project root:

```dotenv
FOOTBALL_DATA_API_TOKEN=your_token
```

Install the package for development:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

## Example

```python
from scoutswap import FootballDataClient, Settings

client = FootballDataClient(Settings())
premier_league = client.get_competition_teams("PL")
print(premier_league.teams[0].name)
```

## Safe source-data audit

Run the aggregate Premier League coverage audit with:

```bash
scoutswap-audit
```

The command reports field availability and request counts only. If the
competition response omits squads, team fallback requests are paced to respect
the football-data.org free-plan rate limit. It never prints the API token or
full player payloads.
