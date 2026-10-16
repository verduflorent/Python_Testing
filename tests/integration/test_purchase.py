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


def test_purchase_cumulative_limit_rejects_second_booking(booking_data):
    """8 places puis 6 autres dépassent le plafond de 12 pour le même club."""
    club, competition = booking_data
    club["points"] = "30"
    competition["numberOfPlaces"] = "30"
    client = server.app.test_client()
    data = {"club": club["name"], "competition": competition["name"]}

    first = client.post("/purchasePlaces", data={**data, "places": "8"})
    second = client.post("/purchasePlaces", data={**data, "places": "6"})

    assert first.status_code == 200
    assert second.status_code == 200
    assert b"You cannot book more than 12 places." in second.data
    assert int(club["points"]) == 22
    assert int(competition["numberOfPlaces"]) == 22
    assert club["bookings"][competition["name"]] == 8


def test_purchase_cumulative_limit_accepts_exactly_twelve(booking_data):
    """8 places puis 4 atteignent exactement le plafond autorisé."""
    club, competition = booking_data
    club["points"] = "20"
    competition["numberOfPlaces"] = "25"
    client = server.app.test_client()
    data = {"club": club["name"], "competition": competition["name"]}

    client.post("/purchasePlaces", data={**data, "places": "8"})
    response = client.post("/purchasePlaces", data={**data, "places": "4"})

    assert response.status_code == 200
    assert int(club["points"]) == 8
    assert int(competition["numberOfPlaces"]) == 13
    assert club["bookings"][competition["name"]] == 12


def test_purchase_limit_is_per_competition(booking_data):
    """Les places réservées dans une autre compétition ne comptent pas."""
    club, competition = booking_data
    club["points"] = "30"
    competition["numberOfPlaces"] = "25"
    other = {"name": "Second Competition", "numberOfPlaces": "25"}
    server.competitions.append(other)
    client = server.app.test_client()

    for comp in (competition, other):
        response = client.post(
            "/purchasePlaces",
            data={"club": club["name"], "competition": comp["name"], "places": "8"}
        )
        assert response.status_code == 200

    assert club["bookings"] == {"Test Competition": 8, "Second Competition": 8}
    assert int(club["points"]) == 14
    assert int(competition["numberOfPlaces"]) == 17
    assert int(other["numberOfPlaces"]) == 17


def test_purchase_rejects_more_than_available_places(booking_data):
    """Une demande supérieure au stock est refusée sans aucune déduction."""
    club, competition = booking_data
    club["points"] = "20"
    competition["numberOfPlaces"] = "5"

    response = server.app.test_client().post(
        "/purchasePlaces",
        data={"club": club["name"], "competition": competition["name"], "places": "6"}
    )

    assert response.status_code == 200
    assert b"Not enough places available" in response.data
    assert int(club["points"]) == 20
    assert int(competition["numberOfPlaces"]) == 5
    assert club.get("bookings", {}) == {}


def test_purchase_accepts_exact_available_places(booking_data):
    """Réserver exactement les dernières places est autorisé."""
    club, competition = booking_data
    club["points"] = "20"
    competition["numberOfPlaces"] = "5"

    response = server.app.test_client().post(
        "/purchasePlaces",
        data={"club": club["name"], "competition": competition["name"], "places": "5"}
    )

    assert response.status_code == 200
    assert b"Great-booking complete!" in response.data
    assert int(club["points"]) == 15
    assert int(competition["numberOfPlaces"]) == 0
    assert club["bookings"][competition["name"]] == 5


def test_purchase_rejects_booking_when_competition_is_full(booking_data):
    """Une compétition sans places disponibles refuse toute réservation."""
    club, competition = booking_data
    competition["numberOfPlaces"] = "0"

    response = server.app.test_client().post(
        "/purchasePlaces",
        data={"club": club["name"], "competition": competition["name"], "places": "1"}
    )

    assert response.status_code == 200
    assert b"Not enough places available" in response.data
    assert int(club["points"]) == 10
    assert int(competition["numberOfPlaces"]) == 0
    assert club.get("bookings", {}) == {}


@pytest.mark.parametrize("invalid_places", ["0", "-3", "abc", "1.5", "", None])
def test_purchase_rejects_invalid_quantity(booking_data, invalid_places):
    """Les quantités invalides sont refusées sans effet sur les données."""
    club, competition = booking_data
    data = {"club": club["name"], "competition": competition["name"]}
    if invalid_places is not None:
        data["places"] = invalid_places

    response = server.app.test_client().post("/purchasePlaces", data=data)

    assert response.status_code == 200
    assert b"Please enter a valid positive number of places." in response.data
    assert int(club["points"]) == 10
    assert int(competition["numberOfPlaces"]) == 20
    assert club.get("bookings", {}) == {}


@pytest.mark.parametrize("missing_field", ["club", "competition"])
def test_purchase_unknown_entity_is_rejected(booking_data, missing_field):
    """Un club ou une compétition inconnue ne modifie aucune donnée."""
    club, competition = booking_data
    data = {"club": club["name"], "competition": competition["name"], "places": "2"}
    data[missing_field] = "Unknown"

    response = server.app.test_client().post("/purchasePlaces", data=data)

    assert response.status_code == 400
    assert int(club["points"]) == 10
    assert int(competition["numberOfPlaces"]) == 20
    assert club.get("bookings", {}) == {}


@pytest.mark.parametrize("missing_field", ["club", "competition"])
def test_purchase_missing_entity_field_is_rejected(booking_data, missing_field):
    """Un formulaire incomplet est refusé sans mutation."""
    club, competition = booking_data
    data = {"club": club["name"], "competition": competition["name"], "places": "2"}
    del data[missing_field]

    response = server.app.test_client().post("/purchasePlaces", data=data)

    assert response.status_code == 400
    assert int(club["points"]) == 10
    assert int(competition["numberOfPlaces"]) == 20
    assert club.get("bookings", {}) == {}


@pytest.mark.parametrize("invalid_segment", ["club", "competition"])
def test_book_unknown_entity_returns_404(booking_data, invalid_segment):
    """La page de réservation n'existe pas pour un club ou concours inconnu."""
    club, competition = booking_data
    club_name = "Unknown" if invalid_segment == "club" else club["name"]
    competition_name = "Unknown" if invalid_segment == "competition" else competition["name"]

    response = server.app.test_client().get(
        f"/book/{competition_name}/{club_name}"
    )

    assert response.status_code == 404
    assert int(club["points"]) == 10
    assert int(competition["numberOfPlaces"]) == 20
