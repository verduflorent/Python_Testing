from server import app, clubs


def test_login_with_unknown_email():
    client = app.test_client()

    response = client.post(
        "/showSummary",
        data={"email": "inconnu@test.fr"},
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Adresse email inconnue" in response.data


def test_login_with_valid_email():
    client = app.test_client()

    valid_email = clubs[0]["email"]

    response = client.post(
        "/showSummary",
        data={"email": valid_email}
    )

    assert response.status_code == 200
    assert b"Welcome" in response.data
