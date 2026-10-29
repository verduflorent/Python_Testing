import json
from datetime import datetime
from flask import Flask,render_template,request,redirect,flash,url_for,abort


def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


def competition_is_future(competition):
    """Return True only for a competition with a valid future date."""
    try:
        competition_date = datetime.strptime(competition['date'], '%Y-%m-%d %H:%M:%S')
    except (KeyError, TypeError, ValueError):
        return False
    return competition_date > datetime.now()


app = Flask(__name__)
app.secret_key = 'something_special'
app.jinja_env.globals['competition_is_future'] = competition_is_future

competitions = loadCompetitions()
clubs = loadClubs()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary',methods=['POST'])
def showSummary():
    matching_clubs = [
        club for club in clubs
        if club['email'] == request.form['email']
    ]

    if not matching_clubs:
        flash("Adresse email inconnue. Veuillez réessayer.")
        return redirect(url_for('index'))

    club = matching_clubs[0]
    return render_template('welcome.html',club=club,competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClub = next((c for c in clubs if c['name'] == club), None)
    foundCompetition = next((c for c in competitions if c['name'] == competition), None)
    if foundClub is None or foundCompetition is None:
        abort(404)
    if not competition_is_future(foundCompetition):
        abort(403, description='Booking is closed for past competitions.')
    already_booked = foundClub.get('bookings', {}).get(foundCompetition['name'], 0)
    max_places = max(0, min(
        int(foundClub['points']),
        int(foundCompetition['numberOfPlaces']),
        12 - already_booked
    ))
    return render_template(
        'booking.html', club=foundClub, competition=foundCompetition,
        max_places=max_places
    )


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition_name = request.form.get('competition')
    club_name = request.form.get('club')
    competition = next((c for c in competitions if c['name'] == competition_name), None)
    club = next((c for c in clubs if c['name'] == club_name), None)
    if club is None or competition is None:
        abort(400, description="Unknown club or competition.")

    if not competition_is_future(competition):
        flash("Booking is closed for past competitions.")
        return render_template('welcome.html', club=club, competitions=competitions)

    # Vérifie le champ avant de convertir et de modifier les données.
    raw_places = request.form.get('places', '')
    try:
        placesRequired = int(raw_places)
    except (TypeError, ValueError):
        flash("Please enter a valid positive number of places.")
        return render_template('welcome.html', club=club, competitions=competitions)

    if placesRequired <= 0:
        flash("Please enter a valid positive number of places.")
        return render_template('welcome.html', club=club, competitions=competitions)

    # Les réservations sont suivies par club et par compétition.
    alreadyBooked = club.get('bookings', {}).get(competition['name'], 0)

    # Le plafond de 12 s'applique au cumul, pas à chaque demande isolée.
    if alreadyBooked + placesRequired > 12:
        flash("You cannot book more than 12 places.")
        return render_template(
            'welcome.html',
            club=club,
            competitions=competitions
        )

    # Refuse une réservation supérieure aux places restantes.
    if placesRequired > int(competition['numberOfPlaces']):
        flash("Not enough places available for this competition.")
        return render_template(
            'welcome.html',
            club=club,
            competitions=competitions
        )

    # Vérifie que le club possède suffisamment de points.
    if placesRequired > int(club['points']):
        flash("Not enough points to complete this booking.")
        return render_template(
            'welcome.html',
            club=club,
            competitions=competitions
        )

    # La réservation est autorisée : on met à jour les données.
    competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - placesRequired
    club['points'] = int(club['points']) - placesRequired
    club.setdefault('bookings', {})[competition['name']] = alreadyBooked + placesRequired

    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))
