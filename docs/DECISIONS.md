# ScoutSwap decision log

## How to use this log

Record durable product and architecture choices here. A decision entry should
state its status, context, decision, and consequences. Story status belongs in
GitHub Issues, not this file.

Statuses:

- Accepted: active project direction.
- Proposed: requires owner confirmation or implementation evidence.
- Superseded: retained for history but no longer active.

## D-001 — Python implementation

- Status: Accepted
- Decision: Use Python 3.9 or newer for the reusable package and backend.
- Consequence: New syntax and dependencies must remain compatible with the
  version declared in `pyproject.toml`.

## D-002 — Initial source and competition

- Status: Accepted
- Decision: Use football-data.org v4 and begin with Premier League code `PL`.
- Consequence: Source-data coverage must be audited before treating market value
  or contract fields as reliable.

## D-003 — AWS as cloud provider

- Status: Accepted
- Decision: Build the deployed product on AWS.
- Consequence: Local development remains cloud-independent where practical, and
  deployed resources are reproducible through infrastructure as code.

## D-004 — DynamoDB operational database

- Status: Accepted
- Decision: Use DynamoDB instead of a local or relational database for the MVP.
- Consequence: Access patterns and indexes must be decided before table schemas;
  flexible filtering occurs over bounded candidate pools in Python.

## D-005 — Multiple-table DynamoDB design

- Status: Accepted
- Decision: Start with separate player and synchronization tables rather than
  single-table design. Add a separate value-history table only after an accepted
  market-value source exists.
- Consequence: The first implementation favors clarity and avoids provisioning
  unused value-history infrastructure. Consolidate only when measured access
  patterns justify the complexity.

## D-006 — Storage abstraction

- Status: Accepted
- Decision: Domain and ranking services depend on repository protocols rather
  than Boto3.
- Consequence: Unit tests use in-memory repositories, and storage can be replaced
  without rewriting ranking behavior.

## D-007 — Explainable recommendations

- Status: Accepted
- Decision: Return component scores and raw explanation facts alongside the total
  score.
- Consequence: ScoutSwap does not present similarity as an official valuation or
  hide recommendation reasoning in opaque prose.

## D-008 — AWS region

- Status: Proposed
- Proposal: Use `us-west-2`.
- Decision needed by: SS-202 and SS-501.

## D-009 — Infrastructure tool

- Status: Proposed
- Proposal: Use AWS CDK for Python.
- Decision needed by: SS-501.

## D-010 — Market-value snapshot policy

- Status: Proposed
- Proposal: Store a new history item only when value changes, while updating the
  current player record's observation timestamp on every successful sync.
- Decision needed by: SS-204.

## D-011 — Player-name search

- Status: Proposed
- Options: bounded scan for Premier League MVP, normalized-name GSI, or a later
  search service.
- Constraint: unbounded DynamoDB scans are prohibited.
- Decision needed by: SS-602.

## D-012 — Administrative API authentication

- Status: Proposed
- Constraint: `POST /admin/sync` must not be publicly unauthenticated.
- Decision needed by: SS-604.

## D-013 — Frontend technology

- Status: Proposed
- Options: static HTML/JavaScript or a compiled frontend framework.
- Decision needed by: SS-701.

## D-014 — Source-data feasibility

- Status: Accepted
- Context: The SS-001/SS-002 Premier League audit run on 2026-09-07 returned
  548 players across 20 teams from one `/competitions/PL/teams` request. Club
  association, position, and date-of-birth coverage were 100.0%. Contract
  expiration and market-value coverage were both 0.0%.
- Decision: The current football-data.org subscription and endpoint combination
  does not support the original value-based replacement MVP without scope
  changes or another market-value source.
- Consequence: ScoutSwap will proceed with a position- and age-based
  recommendation MVP. Affordability, estimated savings, and value/budget
  scoring must be omitted or marked unavailable unless a new accepted data
  source is added before release. Do not present missing market values as
  zero-value players, and do not finalize value-based DynamoDB indexes or
  ranking weights until the replacement market-value source is decided.
