from copy import deepcopy

import pytest

import server


@pytest.fixture
def booking_data(monkeypatch):
    """Prépare des données isolées pour chaque test."""

    clubs = [
        {
            "name": "Test Club",
            "email": "test@club.com",
            "points": "10"
        }
    ]

    competitions = [
        {
            "name": "Test Competition",
            "numberOfPlaces": "20"
        }
    ]

    monkeypatch.setattr(server, "clubs", clubs)
    monkeypatch.setattr(server, "competitions", competitions)

    return clubs[0], competitions[0]


def test_purchase_deducts_club_points(booking_data):
    """Une réservation doit déduire les points du club."""

    club, competition = booking_data

    client = server.app.test_client()

    response = client.post(
        "/purchasePlaces",
        data={
            "club": club["name"],
            "competition": competition["name"],
            "places": "3"
        }
    )

    assert response.status_code == 200
    assert int(club["points"]) == 7
    assert int(competition["numberOfPlaces"]) == 17
