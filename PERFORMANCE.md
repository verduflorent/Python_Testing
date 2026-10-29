# GÜDLFT performance testing

The load test runs against an **isolated in-memory dataset**, not the project's
`clubs.json` or `competitions.json`. The Flask development server is used
for local, comparative measurements only; it is not a production benchmark.

## Setup (Python 3.10 virtual environment)

```powershell
python -m pip install -r requirements-performance.txt
```

## Run in two PowerShell terminals

Terminal 1 (from repository root):

```powershell
python performance_server.py
```

Terminal 2 (same virtual environment, from repository root):

```powershell
New-Item -ItemType Directory -Force reports | Out-Null
python -m locust -f locustfile.py --headless -u 6 -r 1 -t 60s --host http://127.0.0.1:5001 --csv reports/locust
```

- 6 users, spawned at 1 per second, 60 seconds of load.
- Each user has its own club and reserves one place in a different future
  competition for each successful booking attempt.
- 3/4 of tasks request the competition list via `POST /showSummary`;
  1/4 perform a valid booking and update club points via `POST /purchasePlaces`.
- The first route is labeled as a list read in Locust but uses HTTP POST.
- Check the generated `reports/locust_stats.csv` for response times,
  failure rate and request count, including p95.
- Compare the list against 5000 ms and the points update against 2000 ms.
  Report **which statistic** (median, p95, max) is being compared.
- Do not claim performance targets have been met until the run completes.
- The fixture is bounded (500 bookings per user). Restart the server before
  a new load-test run to restore its initial state.
- Avoid publishing generated CSV files until results have been reviewed.

The isolated test environment is intentionally separate from the production
data. The Flask development server's throughput is not representative of a
production WSGI deployment.
