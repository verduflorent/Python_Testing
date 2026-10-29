"""Isolated load-test server: never uses or changes the project's JSON files.

Start with: python performance_server.py
Do not expose this development server to the internet.
"""
from datetime import datetime, timedelta

import server

FUTURE_DATE = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d %H:%M:%S")
server.clubs = [
    {"name": f"Load Club {i}", "email": f"load{i}@example.test", "points": "500"}
    for i in range(1, 7)
]
server.competitions = [
    {"name": f"Load Competition {i}", "date": FUTURE_DATE, "numberOfPlaces": "200"}
    for i in range(1, 501)
]

if __name__ == "__main__":
    server.app.run(host="127.0.0.1", port=5001, debug=False, threaded=True)
