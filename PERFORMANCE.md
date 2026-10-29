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


## Measured results — 29 October 2026

A 60-second local run with six simulated users (ramp-up 1 user/second)
produced the following values from `reports/locust_stats.csv`:

| Metric | Competition list (POST /showSummary) | Booking / points update (POST /purchasePlaces) |
| --- | ---: | ---: |
| Requests | 194 | 37 |
| Failures | 0 | 0 |
| Average latency | 24.56 ms | 20.51 ms |
| Median latency | 19 ms | 18 ms |
| 95th percentile (p95) | 50 ms | 35 ms |
| Maximum latency | 157.10 ms | 43.36 ms |
| Required threshold | 5000 ms | 2000 ms |

**Combined:** 231 requests, zero recorded failures, 23.91 ms average
response time, 19 ms median, 48 ms p95, 157.10 ms maximum, and
3.87 requests/second reported by Locust.

**Result:** Both measured operations remained below their respective
response-time thresholds, including the slowest observed requests, in this
specific local test run.

### Interpretation and limitations

- These results were supplied from a completed Locust CSV export; the raw
  CSV remains local to the test machine.
- The `/showSummary` measurement includes rendering a competition list
  from a 500-competition in-memory fixture. It is an HTTP POST, not GET.
- The booking measurement includes the successful reservation and point
  deduction, not an isolated database write.
- Six simulated users and a 60-second local run are not evidence of
  production scalability, long-term stability, or multi-process consistency.
- All data changes occur in memory. The test does not verify persistence
  across server restarts.
- These timings reflect the Flask development server, local hardware and
  the isolated fixture; they must not be presented as production benchmarks.
