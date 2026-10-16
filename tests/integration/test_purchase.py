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

def test_purchase_with_insufficient_points(booking_data):
    """Une réservation doit être refusée si le club manque de points."""

    club, competition = booking_data

    # Le club ne possède que 3 points.
    club["points"] = "3"

    client = server.app.test_client()

    response = client.post(
        "/purchasePlaces",
        data={
            "club": club["name"],
            "competition": competition["name"],
            "places": "5"
        }
    )

    # La réservation ne doit modifier aucune donnée.
    assert int(club["points"]) == 3
    assert int(competition["numberOfPlaces"]) == 20
    assert b"Not enough points" in response.data


def test_purchase_cannot_exceed_twelve_places(booking_data):
    """Une demande de 13 places est refusée sans modifier les données."""
    club, competition = booking_data
    club["points"] = "20"
    competition["numberOfPlaces"] = "25"

    response = server.app.test_client().post(
        "/purchasePlaces",
        data={"club": club["name"], "competition": competition["name"], "places": "13"}
    )

    assert response.status_code == 200
    assert int(club["points"]) == 20
    assert int(competition["numberOfPlaces"]) == 25
    assert b"You cannot book more than 12 places." in response.data


def test_purchase_exactly_twelve_places(booking_data):
    """Une demande de 12 places reste autorisée si le solde et les places suffisent."""
    club, competition = booking_data
    club["points"] = "20"
    competition["numberOfPlaces"] = "25"

    response = server.app.test_client().post(
        "/purchasePlaces",
        data={"club": club["name"], "competition": competition["name"], "places": "12"}
    )

    assert response.status_code == 200
    assert int(club["points"]) == 8
    assert int(competition["numberOfPlaces"]) == 13
    assert b"Great-booking complete!" in response.data
