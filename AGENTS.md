# ScoutSwap contributor guidance

Read `docs/IMPLEMENTATION_PLAN.md` before beginning a new implementation target
or handing work between laptops.

## Project goal

ScoutSwap finds affordable replacement candidates for football players using
football-data.org. Recommendations must be explainable and must distinguish
source data from ScoutSwap's calculated scores.

## Development setup

- Use Python 3.9 or newer.
- Create and activate the project virtual environment at `.venv`.
- Install development dependencies with `pip install -e '.[dev]'`.
- Run the test suite with `python -m pytest`.

## Architecture

- Keep reusable package code under `src/scoutswap`.
- Keep football-data.org transport logic in `client.py`.
- Represent external API payloads with typed Pydantic models in `models.py`.
- Keep replacement scoring independent of HTTP and persistence code.
- Prefer small, testable modules over framework-specific coupling.

## Data and API rules

- Read the API token from `FOOTBALL_DATA_API_TOKEN`; never hard-code, print,
  log, or commit it.
- Treat missing and `null` API fields as expected input.
- Respect football-data.org rate limits and avoid one-request-per-player loops.
- Cache or persist fetched squad data before adding repeated API calls.
- Label market values with their source and observation date when displayed.
- Do not describe ScoutSwap similarity scores as official transfer valuations.

## Implementation conventions

- Maintain compatibility with the Python version declared in `pyproject.toml`.
- Add type hints to public functions and models.
- Raise domain-specific exceptions for upstream API failures.
- Keep ranking weights explicit and explainable.
- Add or update tests for every behavior change.

## Verification

Before considering a change complete:

1. Run `python -m pytest`.
2. Confirm `.env`, virtual environments, IDE metadata, databases, and generated
   package metadata remain untracked.
3. Avoid live API calls in unit tests; use `httpx.MockTransport` or fixtures.
