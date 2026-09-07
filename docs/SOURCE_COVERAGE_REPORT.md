# ScoutSwap source coverage report

## Report context

- Story: SS-002
- Source: football-data.org v4
- Competition: Premier League (`PL`)
- Observation date: 2026-09-07
- Audit command: `scoutswap-audit --competition PL`

This report records aggregate field availability only. It must not include the
API token, raw upstream payloads, or player-level records.

## Request strategy

The `/competitions/PL/teams` response included squads for all Premier League
teams during this audit.

Minimum API-call strategy observed:

- Competition team request: 1
- Fallback team requests: 0
- Total requests: 1

The per-team fallback path remains available for cases where the competition
teams response omits squad data, but it was not required for this observation.

## Aggregate coverage

| Field | Present | Total | Coverage |
| --- | ---: | ---: | ---: |
| Club association | 548 | 548 | 100.0% |
| Position | 548 | 548 | 100.0% |
| Date of birth | 548 | 548 | 100.0% |
| Contract expiration | 0 | 548 | 0.0% |
| Market value | 0 | 548 | 0.0% |

## Notes

- The current subscription and endpoint combination provides enough aggregate
  player identity, club, position, and birth-date coverage to normalize Premier
  League squad records.
- The current audit returned no market values and no contract-expiration dates.
- The value-based replacement MVP must not assume source market-value coverage
  is available until SS-003 records the product feasibility decision.
