"""Functional tests for the public points board."""
import server


def test_points_board_is_public(monkeypatch):
    """The points board works without a login or session."""
    clubs = [
        {"name": "Alpha Lift", "email": "alpha@example.com", "points": "13"},
        {"name": "Beta Lift", "email": "beta@example.com", "points": "4"},
    ]
    monkeypatch.setattr(server, "clubs", clubs)

    response = server.app.test_client().get("/points")

    assert response.status_code == 200
    assert b"Alpha Lift" in response.data
    assert b"Beta Lift" in response.data
    assert b"<td>13</td>" in response.data
    assert b"<td>4</td>" in response.data


def test_points_board_reflects_booking(monkeypatch):
    """The board reflects points deducted after a valid reservation."""
    from datetime import datetime, timedelta

    club = {"name": "Alpha Lift", "email": "alpha@example.com", "points": "10"}
    competition = {
        "name": "Future Competition",
        "numberOfPlaces": "20",
        "date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S"),
    }
    monkeypatch.setattr(server, "clubs", [club])
    monkeypatch.setattr(server, "competitions", [competition])
    client = server.app.test_client()

    purchase = client.post(
        "/purchasePlaces",
        data={"club": club["name"], "competition": competition["name"], "places": "3"},
    )
    response = client.get("/points")

    assert purchase.status_code == 200
    assert response.status_code == 200
    assert b"Alpha Lift" in response.data
    assert b"<td>7</td>" in response.data
    assert b"<td>10</td>" not in response.data


def test_home_links_to_public_points_board():
    """The public board is discoverable from the home page."""
    response = server.app.test_client().get("/")

    assert response.status_code == 200
    assert b'href="/points"' in response.data
