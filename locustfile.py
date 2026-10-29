"""Locust scenarios for the isolated performance_server.py only.

Run: python -m locust -f locustfile.py --headless -u 6 -r 1 -t 60s
     --host http://127.0.0.1:5001 --csv reports/locust
"""
from itertools import count

from locust import HttpUser, between, task

_next_user = count(1)


class GudlftUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        self.user_number = next(_next_user)
        if self.user_number > 6:
            raise RuntimeError("This scenario supports exactly six simulated users at most.")
        self.club_name = f"Load Club {self.user_number}"
        self.email = f"load{self.user_number}@example.test"
        self.next_competition = 1

    @task(3)
    def view_competitions(self):
        with self.client.post(
            "/showSummary",
            data={"email": self.email},
            name="GET competition list (POST /showSummary)",
            catch_response=True,
        ) as response:
            if response.status_code != 200 or b"Load Competition 1" not in response.content:
                response.failure("Competition list not displayed")

    @task(1)
    def update_points_by_booking(self):
        if self.next_competition > 500:
            return  # Avoid exhausting the isolated fixture.
        competition = f"Load Competition {self.next_competition}"
        self.next_competition += 1
        with self.client.post(
            "/purchasePlaces",
            data={"club": self.club_name, "competition": competition, "places": "1"},
            name="POST booking / points update",
            catch_response=True,
        ) as response:
            if response.status_code != 200 or b"Great-booking complete!" not in response.content:
                response.failure("Booking did not update points successfully")
