# GÜDLFT — Competition Booking (Flask)

Proof-of-concept competition booking application for sports clubs. Clubs use
points to reserve places in competitions; a public page shows current club
balances.

## Requirements

- Python **3.10.11** (the legacy Flask 1.1.2 stack is not compatible with
  every newer Python release).
- PowerShell commands below are for Windows; other platforms can use their
  equivalent virtual environment activation commands.

## Install and run

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:FLASK_APP = "server.py"
python -m flask run
```

Open http://127.0.0.1:5000/ . The club login addresses are defined in
`clubs.json`. The public club points board is available at
http://127.0.0.1:5000/points .

**Note:** The sample competitions in `competitions.json` are dated 2020
and therefore cannot be booked today. To test booking manually, create a
future-dated competition in a local copy of the fixture.

## Features and booking rules

- Unknown club email shows an error instead of crashing.
- Booking deducts club points and competition capacity.
- A club may book at most **12 places per competition in total**.
- Booking cannot exceed the club's points or remaining competition places.
- Invalid quantities and unknown clubs/competitions are rejected.
- Past competitions remain visible but cannot be booked.
- The booking form reflects the most restrictive allowed quantity.
- The public `/points` page lists clubs and their current point balances.

## Automated tests

```powershell
python -m pip install -r requirements-test.txt
python -m pytest -v
python -m pytest --cov=server --cov-report=term-missing
```

Tests live in `tests/unit`, `tests/integration` and `tests/functional`.
The latest locally verified run (29 October 2026) completed **46 tests**
with **97% line coverage** for `server.py` before the performance-only
branch was merged. Run the commands above to verify your own environment.

## Performance test (Locust)

See [PERFORMANCE.md](PERFORMANCE.md) for the isolated test server,
dependencies, run instructions and measured results.

The recorded local run used six users for 60 seconds, with 231 requests,
zero failures, and p95 response times of 50 ms (competition list) and
35 ms (booking/points update). This is a local development-server
measurement, **not** a production performance guarantee.

## Architecture and limitations

- `server.py` contains Flask routes and the booking logic.
- `clubs.json` and `competitions.json` provide the initial fixture data.
- `templates/` contains Jinja2 views; `tests/` contains pytest tests.
- Changes to points, capacity and cumulative bookings occur **in memory**,
  not persistently in the JSON files. Restarting the application resets
  this state. The proof of concept does not provide transactional guarantees
  for concurrent bookings.
- The performance test uses isolated in-memory fixtures, and does not
  modify the original JSON files.

## Git workflow

Work on a dedicated branch for each bug or feature, run the tests,
then merge via pull request. The `master` branch holds validated changes.
A separate `QA` delivery branch will be prepared after final checks.
