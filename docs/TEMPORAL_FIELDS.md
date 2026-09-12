# ScoutSwap temporal field behavior

ScoutSwap keeps source dates and calculated values separate. Source fields such
as `date_of_birth` and `contract_until` are stored as received after basic API
model parsing. Derived values are calculated with explicit helper functions.

## Age

Age must always be calculated with an explicit `as_of` date. This keeps ranking
and tests deterministic.

Behavior:

- Missing date of birth returns `None`.
- A future date of birth relative to `as_of` returns `None`.
- Age is measured in complete years.
- The birthday boundary is inclusive: a player has the new age on their
  birthday.

## Contract end date

football-data.org may return complete contract dates or partial month values.
ScoutSwap parses only values with documented behavior.

Behavior:

- `YYYY-MM-DD` parses as that exact date.
- `YYYY-MM` parses to the last calendar day of that month.
- Missing, blank, malformed, or impossible values return `None`.

The source `contract_until` string is still preserved on the domain player.
