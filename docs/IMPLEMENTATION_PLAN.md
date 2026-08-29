# ScoutSwap implementation plan

## Purpose of this document

This is the shared implementation handoff for ScoutSwap. An agent starting on
another laptop should read this file and the repository-root `AGENTS.md` before
changing code. Treat the checked-in repository as the source of truth and do
not assume uncommitted work exists on another machine.

## Product goal

ScoutSwap helps a user select a Premier League player and find affordable,
explainable replacement candidates. It uses football-data.org as its initial
data source and clearly separates source-provided market values from
ScoutSwap-calculated similarity scores.

An example result should eventually look like:

```text
Replacement: Example Player
Similarity: 86%
Estimated saving: EUR 24m
Why: Same position, three years younger, and 42% cheaper.
```

ScoutSwap is not an official transfer valuation service. It must not describe
its similarity score as a transfer fee prediction.

## Decisions already made

- Language: Python 3.9 or newer.
- Initial competition: English Premier League (`PL`).
- Source API: football-data.org v4.
- Cloud provider: AWS.
- Operational database: Amazon DynamoDB, not a local database.
- Intended runtime: AWS Lambda behind API Gateway.
- Scheduled imports: Amazon EventBridge Scheduler invoking Lambda.
- Frontend hosting: Amazon S3 behind CloudFront.
- Secrets: AWS Systems Manager Parameter Store or Secrets Manager.
- Monitoring: Amazon CloudWatch.
- Infrastructure should be reproducible and checked in, preferably with AWS
  CDK for Python.
- Keep domain and ranking logic independent from AWS so another repository
  implementation can be introduced later.

## Current repository state

The repository currently contains an installable Python package with:

- Configuration loaded through `pydantic-settings`.
- A synchronous `httpx` client for football-data.org.
- Typed Pydantic models for competitions, teams, contracts, and players.
- Mocked API tests that do not consume football-data.org quota.
- A repository-level `AGENTS.md` containing contributor rules.

Current verification command:

```bash
cd /Users/kartikrode/scoutswap
source .venv/bin/activate
python -m pytest
```

At the time this document was created, the suite had two passing tests. The
project has not yet made a live football-data.org request, provisioned AWS
resources, implemented persistence, or implemented the ranking engine.

## Security boundaries

- Never print, log, commit, or paste the football-data.org token.
- `.env` is ignored and currently uses `FOOTBALL_DATA_API_TOKEN`.
- Do not commit AWS access keys or session credentials.
- Prefer AWS IAM Identity Center/SSO profiles on each laptop.
- Lambda should receive only least-privilege permissions for its tables,
  secret, and logs.
- Do not make AWS resources publicly writable.
- The browser must never receive the football-data.org token or AWS database
  credentials.
- Avoid live API calls in unit tests.

## DynamoDB access patterns

Design keys and indexes from these access patterns before provisioning tables:

1. Get one player by football-data.org player ID.
2. Find replacement candidates by normalized position and maximum market value.
3. List players belonging to a club.
4. Retrieve a player's market-value observations in chronological order.
5. Upsert a synchronized Premier League squad without creating duplicates.
6. Record synchronization status and prevent overlapping synchronization runs.

Do not add a scan-based endpoint without explicitly documenting why its bounded
data volume makes the scan acceptable.

## Initial DynamoDB table design

Use a simple multiple-table design for the MVP. Do not introduce single-table
design unless measured access patterns justify the extra complexity.

### Players table

Suggested logical name: `scoutswap-players-{environment}`

```text
Partition key: player_id (Number)

Attributes:
player_id
name
first_name
last_name
club_id
club_name
position
normalized_position
date_of_birth
age
nationality
shirt_number
market_value
contract_until
data_completeness
source_updated_at
synced_at
```

Candidate index:

```text
GSI1 partition key: normalized_position
GSI1 sort key: market_value
```

Club index:

```text
GSI2 partition key: club_id
GSI2 sort key: name
```

Exact physical index names should be configuration values rather than repeated
string literals.

### Market-value history table

Suggested logical name: `scoutswap-value-history-{environment}`

```text
Partition key: player_id (Number)
Sort key: observed_at (ISO-8601 String)

Attributes:
player_id
observed_at
market_value
club_id
source
```

Only create a new snapshot when a value is available. Decide during
implementation whether unchanged values should be stored on every scheduled
observation or only when changed; record that decision here before release.

### Synchronization table

Suggested logical name: `scoutswap-sync-runs-{environment}`

```text
Partition key: competition_code (String)
Sort key: started_at (ISO-8601 String)

Attributes:
competition_code
started_at
completed_at
status
players_received
players_saved
error_summary
lock_expires_at
```

Use a conditional write or a dedicated lock item to prevent two laptops or two
Lambda invocations from synchronizing the same competition simultaneously.

## Repository boundary

The ranking engine and service layer must depend on protocols, not directly on
Boto3. The intended boundary is conceptually:

```python
class PlayerRepository(Protocol):
    def get_player(self, player_id: int): ...
    def find_candidates(self, position: str, max_value: int, limit: int): ...
    def save_players(self, players): ...


class ValueHistoryRepository(Protocol):
    def save_snapshot(self, snapshot): ...
    def get_history(self, player_id: int): ...
```

Provide DynamoDB implementations and in-memory fakes for unit testing. Do not
make the domain layer import Boto3.

## Replacement score v1

The first score must be deterministic and explainable. Start with source fields
that football-data.org is expected to expose:

```text
Position similarity:       40%
Age similarity:            25%
Value/budget fit:           20%
Contract opportunity:      10%
Data completeness:          5%
```

These are initial product weights, not validated sporting science. Keep weights
in one explicit configuration object and test boundary behavior.

Initial filters:

- Maximum market value.
- Maximum age, when age is available.
- Exclude the selected player.
- Optionally exclude the selected player's club.
- Require an exact normalized position by default.
- Exclude candidates below a configurable data-completeness threshold.

Every result should include structured explanation fields rather than only a
preformatted sentence.

## Phased delivery plan

### Target 1: Audit the live source data

Tasks:

- Add a safe command or script that fetches Premier League teams once.
- Inspect whether competition-team responses include complete squads.
- Calculate counts and percentages for market value, position, birth date, and
  contract coverage.
- Write only aggregate coverage results to output; never dump the token.
- If a single competition request lacks squads, document the minimum safe call
  strategy that respects the API rate limit.

Acceptance criteria:

- One authenticated synchronization request succeeds.
- A data-coverage report identifies which ranking fields are usable.
- Tests remain fully mocked.
- The report contains no secrets or unnecessary personal data dumps.

### Target 2: Normalize domain records

Tasks:

- Introduce persisted/domain player and value snapshot models separate from raw
  API payload models.
- Associate squad members with their club.
- Normalize football-data.org position strings into a documented vocabulary.
- Calculate age using an explicit `as_of` date for deterministic tests.
- Parse contract expiration and calculate data completeness.

Acceptance criteria:

- Complete and incomplete API payloads normalize without crashing.
- Age and completeness tests use fixed dates.
- Unknown positions map to an explicit fallback rather than disappearing.

### Target 3: Add the DynamoDB storage boundary

Tasks:

- Add Boto3 as a dependency.
- Add DynamoDB and AWS region settings without adding access-key settings.
- Define repository protocols.
- Implement player upsert, player lookup, candidate query, club query, snapshot
  insertion, and history query.
- Use batch writers for squad imports and conditional writes where idempotency
  matters.
- Use integer minor/whole currency units consistently; do not use floating-point
  values for money.

Acceptance criteria:

- Unit tests run without AWS credentials.
- Repository tests use stubs, fakes, or a deliberately selected local emulator.
- Candidate lookup uses the position/value GSI rather than a full scan.
- Missing optional attributes round-trip safely.

### Target 4: Implement replacement ranking

Tasks:

- Implement candidate filters and score components.
- Return total score, component scores, savings, and explanation facts.
- Keep ranking code free of HTTP, Boto3, and FastAPI imports.
- Define deterministic tie-breaking.

Acceptance criteria:

- Tests cover equal players, cheaper players, missing values, age boundaries,
  same-club exclusion, and ties.
- Scores remain within the documented range.
- A recommendation can explain why it ranked above another candidate.

### Target 5: Build synchronization service

Tasks:

- Fetch Premier League squads through the existing client.
- Normalize and batch-upsert players.
- Create value snapshots according to the recorded snapshot policy.
- Record sync metrics and failures.
- Add overlap protection and retry-safe behavior.

Acceptance criteria:

- Re-running the same payload does not duplicate players or corrupt history.
- Partial failures are visible in the sync record.
- External requests use explicit timeouts and useful domain exceptions.

### Target 6: Provision AWS infrastructure

Tasks:

- Add a Python AWS CDK application under `infrastructure/`.
- Define DynamoDB tables, indexes, TTL where appropriate, encryption defaults,
  and point-in-time recovery based on environment needs.
- Define the sync Lambda, API Lambda, API Gateway, EventBridge schedule,
  CloudWatch logs/alarms, and secret/parameter references.
- Export non-secret resource names for application configuration.

Acceptance criteria:

- `cdk synth` succeeds.
- Infrastructure changes are reviewable in source control.
- IAM policies name exact resources and required actions.
- Development and production environments cannot accidentally share table
  names.

### Target 7: Add FastAPI endpoints

Initial endpoints:

```text
GET  /health
GET  /players
GET  /players/{player_id}
GET  /players/{player_id}/replacements
POST /admin/sync
```

Tasks:

- Add FastAPI and a Lambda adapter such as Mangum.
- Add request validation, pagination, and structured errors.
- Protect administrative synchronization.
- Ensure API responses expose source timestamps and data completeness.

Acceptance criteria:

- OpenAPI generation succeeds.
- Endpoint tests use fake repositories.
- Error responses never expose secrets or raw upstream responses.

### Target 8: Build and deploy the frontend

Tasks:

- Build player search, player detail, replacement filters, and ranked results.
- Display missing data honestly.
- Host static assets in S3 through CloudFront.
- Keep admin operations out of the public interface initially.

Acceptance criteria:

- A user can select a player and obtain replacement results end to end.
- Mobile and desktop layouts are usable.
- Recommendation explanations and source dates are visible.

### Target 9: Delivery automation and operations

Tasks:

- Add GitHub Actions for tests and infrastructure synthesis.
- Add formatting/linting only with an agreed tool configuration.
- Document AWS bootstrap, deployment, rollback, and second-laptop setup.
- Add CloudWatch alarms for synchronization and API failures.
- Consider DynamoDB export to S3/Athena only after operational needs exist.

Acceptance criteria:

- Every pull request runs package tests.
- A clean laptop can authenticate with AWS SSO, install the package, run tests,
  and deploy using documented commands.

## Collaboration workflow for two laptops

Before starting work:

```bash
git switch main
git pull --ff-only
git status --short
```

Create one branch per target or bounded subtask:

```bash
git switch -c feature/target-3-dynamodb-repository
```

Before handing work to the other laptop:

1. Run the relevant tests.
2. Review `git diff` and confirm secrets are absent.
3. Commit coherent changes.
4. Push the branch.
5. Update this document if a durable decision changed.
6. State the branch name, last commit, tests run, and remaining work.

Do not use a shared uncommitted working state as a handoff mechanism. Do not
force-push `main`. Prefer small pull requests or fast-forwardable branches.

## Required environment on each laptop

Local `.env` during package development:

```dotenv
FOOTBALL_DATA_API_TOKEN=not-committed
AWS_REGION=us-west-2
AWS_PROFILE=scoutswap
SCOUTSWAP_ENVIRONMENT=dev
```

Exact DynamoDB table and index environment-variable names should be added only
when Target 3 settles the configuration API. AWS credentials must remain in the
AWS CLI/SSO credential mechanism, not `.env`.

## Open decisions

Record answers here when decided:

- AWS region: proposed `us-west-2`, not yet confirmed.
- Infrastructure tool: proposed AWS CDK for Python, not yet confirmed.
- Snapshot policy: every observation versus value-change-only.
- Public API authentication: not needed for read-only MVP, but admin sync must
  be protected.
- Frontend technology: static HTML/JavaScript or a compiled framework.
- Whether football-data.org returns enough non-null market values on the current
  account plan. Target 1 must answer this before weights are finalized.

## Immediate next action

Do not provision AWS first. Complete Target 1 and document real source-data
coverage. Then complete Target 2 before implementing DynamoDB serialization.
This prevents the cloud schema from being based on assumed API fields.

