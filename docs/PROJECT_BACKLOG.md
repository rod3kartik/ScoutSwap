# ScoutSwap project backlog

## How to use this backlog

This file defines stable story scope, delivery order, and milestone acceptance.
Use GitHub Issues and pull requests for assignment and current status. Do not
maintain day-to-day status in both places.

Point scale:

- 1: trivial.
- 2: small.
- 3: approximately one focused developer day.
- 5: multi-day or integration-heavy.
- 8: too large; split before implementation.

Priorities:

- P0: required for the MVP or an immediate delivery gate.
- P1: important but not on the minimum critical path.
- P2: defer until evidence justifies the work.

## Release 0.1 — Validated player domain

### Epic 0: Source feasibility

#### SS-001 — Safe Premier League data audit

- Priority: P0
- Points: 3
- Depends on: existing football-data.org client

As the product team, we want an aggregate audit of Premier League squad data so
that we know whether our subscription can support a useful replacement finder.

Acceptance criteria:

- An explicit command fetches `/competitions/PL/teams` once.
- If squads are absent, the fallback fetches teams sequentially with a
  rate-limit-aware strategy.
- Output contains request counts and aggregate field coverage only.
- The API token and full upstream payloads are never printed.
- Mocked tests cover both squad-included and per-team fallback paths.
- Unit tests make no live requests.

#### SS-002 — Source coverage report

- Priority: P0
- Points: 2
- Depends on: SS-001

Acceptance criteria:

- Report player count and coverage percentages for position, birth date,
  contract expiration, market value, and club association.
- Record the minimum API-call strategy required by the current plan.
- Keep the report free of secrets and unnecessary player-level data.

#### SS-003 — Product feasibility gate

- Priority: P0
- Points: 1
- Depends on: SS-002

Acceptance criteria:

- Record whether market-value coverage supports the MVP.
- Record any required scope reduction or scoring-field changes.
- Do not finalize DynamoDB indexes or ranking weights before this decision.

Milestone exit: the repository contains a documented go/no-go decision for the
initial value-based replacement experience.

### Epic 1: Trusted player domain

#### SS-101 — Domain player model

- Priority: P0
- Points: 3
- Depends on: SS-003

Acceptance criteria:

- Domain player model is separate from raw API models.
- Player records include club, source position, observation time, and optional
  market and contract fields.
- Missing source fields do not cause validation failures.

#### SS-102 — Position normalization

- Priority: P0
- Points: 3
- Depends on: SS-101

Acceptance criteria:

- A documented canonical position vocabulary exists.
- Known source positions map deterministically.
- Unknown values map to an explicit `UNKNOWN` fallback.
- Source position is preserved.

#### SS-103 — Deterministic age and contract parsing

- Priority: P0
- Points: 2
- Depends on: SS-101

Acceptance criteria:

- Age uses an explicit `as_of` date.
- Partial contract dates such as `2028-06` parse safely.
- Missing and invalid values have documented behavior.
- Fixed-date boundary tests pass.

#### SS-104 — Data-completeness calculation

- Priority: P0
- Points: 2
- Depends on: SS-101, SS-102, SS-103

Acceptance criteria:

- Completeness rules and weights are explicit.
- Result includes component flags and a bounded total score.
- Complete, partial, and sparse records are tested.

Milestone exit: raw squad data consistently normalizes without crashes or
silent data loss.

## Release 0.2 — Local replacement engine and shared storage contract

### Epic 2: Storage boundary

#### SS-201 — Repository protocols and in-memory fakes

- Priority: P0
- Points: 3
- Depends on: SS-101

Acceptance criteria:

- Typed player, value-history, and sync repository protocols exist.
- In-memory implementations support service tests.
- Domain and ranking modules do not import Boto3.

#### SS-202 — AWS and DynamoDB configuration

- Priority: P0
- Points: 2
- Depends on: SS-201

Acceptance criteria:

- Region, environment, table names, and index names are validated settings.
- No AWS access-key settings are introduced.
- Development and production resource names are isolated.

#### SS-203 — DynamoDB player repository

- Priority: P0
- Points: 5
- Depends on: SS-102, SS-104, SS-201, SS-202

Acceptance criteria:

- Player get, batch upsert, club query, and candidate query are implemented.
- Candidate lookup uses the position/value GSI rather than a full scan.
- Optional attributes round-trip safely.
- Money uses integers or `Decimal`, never floats.
- Tests require no live AWS credentials.

#### SS-204 — Market-value history repository

- Priority: P1
- Points: 3
- Depends on: SS-202

Acceptance criteria:

- Snapshot insertion and chronological history retrieval work.
- Snapshot policy is recorded in `DECISIONS.md`.
- Duplicate behavior is deterministic and tested.

#### SS-205 — Synchronization lock and run repository

- Priority: P1
- Points: 5
- Depends on: SS-202

Acceptance criteria:

- Conditional acquisition prevents overlapping synchronization.
- Locks have owners and expiry times.
- One owner cannot release another owner's lock.
- Expired locks are recoverable without relying on immediate TTL deletion.

### Epic 3: Replacement engine

#### SS-301 — Candidate filters

- Priority: P0
- Points: 3
- Depends on: SS-104, SS-201

Acceptance criteria:

- Filters support maximum value, optional maximum age, exact normalized
  position, same-player exclusion, optional same-club exclusion, and minimum
  completeness.
- Missing selected-player market value has explicit behavior.

#### SS-302 — Explainable similarity scoring

- Priority: P0
- Points: 5
- Depends on: SS-301

Acceptance criteria:

- Position, age, budget, contract, and completeness components exist.
- Weights live in one immutable configuration object.
- Component and total scores are bounded.
- Results contain raw explanation facts, not only prose.

#### SS-303 — Savings and deterministic ranking

- Priority: P0
- Points: 2
- Depends on: SS-302

Acceptance criteria:

- Savings are returned only when both source values exist.
- Ties resolve by total score, lower value, younger age, then player ID.
- Tests cover equal profiles, missing values, age boundaries, unknown position,
  completeness thresholds, same-club exclusion, and ties.

Milestone exit: a package-level use case returns ranked replacements from an
in-memory repository with structured explanations.

## Release 0.3 — Synchronized AWS API

### Epic 4: Source synchronization

#### SS-401 — Premier League squad collector

- Priority: P0
- Points: 3
- Depends on: SS-001, SS-101 through SS-104

Acceptance criteria:

- Collector uses bounded requests and avoids one request per player.
- Safe transient failures and HTTP 429 responses have documented handling.
- Metrics expose request counts without exposing secrets.

#### SS-402 — Idempotent synchronization service

- Priority: P0
- Points: 5
- Depends on: SS-203, SS-204, SS-205, SS-401

Acceptance criteria:

- Service acquires a lock, fetches, normalizes, upserts, snapshots, and records
  results.
- Replaying the same payload does not duplicate players or corrupt history.
- Partial failures produce sanitized, observable run records.

#### SS-403 — Synchronization contract tests

- Priority: P0
- Points: 3
- Depends on: SS-402

Acceptance criteria:

- Tests cover success, rerun, partial team failure, lock contention, upstream
  timeout, and missing fields.
- Tests use mocked HTTP and fake repositories.

### Epic 5: AWS infrastructure

#### SS-501 — CDK foundation and DynamoDB resources

- Priority: P0
- Points: 5
- Depends on: SS-202 through SS-205

Acceptance criteria:

- Python CDK project defines environment-specific tables, GSIs, encryption,
  lock TTL, and recovery policy.
- `cdk synth` succeeds without live application secrets.
- Key-schema changes receive explicit destructive-change review.

#### SS-502 — Lambda packaging and least-privilege IAM

- Priority: P0
- Points: 5
- Depends on: SS-501

Acceptance criteria:

- API and synchronization Lambdas package successfully.
- Roles grant only required access to exact tables, indexes, parameters, and
  logs.
- API and sync roles are separate when permissions differ materially.

#### SS-503 — EventBridge and observability

- Priority: P1
- Points: 3
- Depends on: SS-402, SS-502

Acceptance criteria:

- Scheduled synchronization is configured.
- Logs are structured, retained for a bounded period, and secret-safe.
- Failure alarm and retry destination or dead-letter decision are documented.

### Epic 6: HTTP API

#### SS-601 — FastAPI Lambda foundation

- Priority: P0
- Points: 3
- Depends on: SS-502

Acceptance criteria:

- FastAPI application, health endpoint, dependency injection, structured errors,
  OpenAPI test, and Mangum adapter exist.

#### SS-602 — Player search and detail

- Priority: P0
- Points: 5
- Depends on: SS-203, SS-601

Acceptance criteria:

- Search strategy is recorded before implementation.
- Responses are paginated or explicitly bounded.
- Player details expose completeness and source observation date.
- Unbounded table scans are prohibited.

#### SS-603 — Replacement endpoint

- Priority: P0
- Points: 3
- Depends on: SS-303, SS-601

Acceptance criteria:

- Filters are validated.
- Response includes ranked candidates, component scores, savings, explanation
  facts, completeness, and source timestamps.
- Endpoint tests use fake repositories.

#### SS-604 — Protected administrative synchronization

- Priority: P1
- Points: 3
- Depends on: SS-402, SS-601

Acceptance criteria:

- Authentication mechanism is recorded before implementation.
- Public unauthenticated callers cannot start synchronization.

Milestone exit: the deployed API supports player selection and explainable
replacement results.

## Release 1.0 — User-facing MVP

### Epic 7: Frontend

#### SS-701 — Player selection interface

- Priority: P0
- Points: 3
- Depends on: SS-602

#### SS-702 — Replacement filters and results

- Priority: P0
- Points: 5
- Depends on: SS-603

Acceptance criteria for SS-701 and SS-702:

- Player search is keyboard and mobile usable.
- Budget, age, and club-exclusion filters are available.
- Results show score breakdown, savings, explanations, completeness, and source
  date.
- Missing fields are displayed honestly.

#### SS-703 — S3 and CloudFront deployment

- Priority: P0
- Points: 5
- Depends on: SS-701, SS-702

Acceptance criteria:

- CloudFront serves a private S3 origin over HTTPS.
- API URL is environment-configured.
- Deployment is reproducible.

### Epic 8: Delivery and operations

#### SS-801 — CI quality gate

- Priority: P1
- Points: 3

Acceptance criteria:

- Pull requests run package tests and `cdk synth` when infrastructure exists.
- Secrets and generated files remain excluded.

#### SS-802 — AWS and second-laptop operations guide

- Priority: P1
- Points: 3
- Depends on: SS-801

Acceptance criteria:

- AWS SSO, bootstrap, deploy, rollback, and clean-laptop setup are documented.

#### SS-803 — Production monitoring

- Priority: P1
- Points: 3
- Depends on: SS-503

Acceptance criteria:

- API and synchronization failure alarms exist.
- Logs contain no secrets.

Milestone exit: a browser user can select a Premier League player and receive
explainable replacement recommendations from the deployed AWS application.

## Critical path

```text
SS-001 → SS-002 → SS-003
→ SS-101 → SS-102/SS-103 → SS-104
→ SS-201 → SS-202 → SS-203
→ SS-301 → SS-302 → SS-303
→ SS-401 → SS-402
→ SS-501 → SS-502 → SS-601 → SS-603
→ SS-701 → SS-702 → SS-703
```

## First sprint

The first sprint contains:

1. SS-001 — Safe Premier League data audit.
2. SS-002 — Source coverage report.
3. SS-003 — Product feasibility gate.
4. SS-101 — Domain player model.
5. SS-102 — Position normalization.

The first implementation story is SS-001.

