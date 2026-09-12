# ScoutSwap data completeness

Data completeness is a ScoutSwap-calculated source coverage score. It is not an
official player quality score, transfer value, or recommendation score.

The result contains a bounded total from `0.0` to `1.0` and boolean component
flags so callers can explain why a record is complete or sparse.

## Default weights

| Component | Weight |
| --- | ---: |
| Club association | 0.20 |
| Known normalized position | 0.25 |
| Date of birth | 0.25 |
| Nationality | 0.10 |
| Contract end source value | 0.10 |
| Market value source value | 0.10 |

The current football-data.org Premier League audit found no contract-end or
market-value coverage. These fields remain part of completeness because the
domain model can carry them when a source provides them, but ranking and UI must
still label missing values honestly.

## Component behavior

- Club is present when a player has club context.
- Position is present when the normalized position is not `UNKNOWN`.
- Date of birth is present when the source date parsed successfully.
- Nationality is present when the source value contains non-whitespace text.
- Contract end is present when the preserved source value contains non-whitespace
  text.
- Market value is present when the source value is not `None`.

Weights are normalized by their total, so custom test weights can still produce
a bounded `0.0` to `1.0` score.
