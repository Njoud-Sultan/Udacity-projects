# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

from sqlalchemy.types import ARRAY

import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import datetime

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://njoud:248384@localhost:5432/fyyur'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)


# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500),
                           default='https://venuetech.nz/wp-content/uploads/IMG_2493-e1514332857195.jpg')
    genres = db.Column(ARRAY(db.String), nullable=True)
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120), default='no details provided')
    shows = db.relationship('Shows', backref='venue', lazy=True)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    genres = db.Column(ARRAY(db.String(120)))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120), default='no details provided')
    shows = db.relationship('Shows', backref='artist', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Shows(db.Model):
    __tablename__ = 'Shows'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    data = []
    # query locations by city and state combined
    locations = db.session.query(Venue.city, Venue.state)

    # get the venue IDs and names existing for each location filtered by city and status
    # then add to the data set
    for location in locations:
        venue_list = db.session.query(Venue.id, Venue.name).filter(Venue.city == location[0]).filter(
            Venue.state == location[1])
        data.append({
            'city': location[0],
            'state': location[1],
            'venues': venue_list
        })

    # data = [{
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "venues": [{
    #         "id": 1,
    #         "name": "The Musical Hop",
    #         "num_upcoming_shows": 0,
    #     }, {
    #         "id": 3,
    #         "name": "Park Square Live Music & Coffee",
    #         "num_upcoming_shows": 1,
    #     }]
    # }, {
    #     "city": "New York",
    #     "state": "NY",
    #     "venues": [{
    #         "id": 2,
    #         "name": "The Dueling Pianos Bar",
    #         "num_upcoming_shows": 0,
    #     }]
    # }]
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # search for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    data = []
    count = 0
    search_term = request.form.get('search_term')
    # ilike is used for case insensitive search results
    found_venues = db.session.query(Venue.id, Venue.name).filter(Venue.name.ilike('%' + search_term + '%')).all()

    if found_venues is not None:
        for venue in found_venues:
            data.append({
                'id': venue[0],
                'name': venue[1]
            })
        count = len(found_venues)

    response = {
        'count': count,
        'data': data
    }

    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    current_date = datetime.datetime.now()
    # query details of the Venue filtered by passed venue_id
    venue_details = db.session.query(Venue).get(venue_id)
    venue_shows = db.session.query(Shows).filter(Shows.venue_id == venue_id)

    # variables to be populated with shows details
    past_shows = []
    upcoming_shows = []
    upcoming_shows_count = 0
    past_shows_count = 0

    # handling empty results
    if venue_shows is not None:
        for show in venue_shows:
            if show.start_time > current_date:
                upcoming_shows.append({
                    'artist_id': show.artist_id,
                    'artist_name': show.artist.name,
                    'artist_image_link': show.artist.image_link,
                    'start_time': str(show.start_time)
                })
            else:
                past_shows.append({
                    'artist_id': show.artist_id,
                    'artist_name': show.artist.name,
                    'artist_image_link': show.artist.image_link,
                    'start_time': str(show.start_time)
                })
        upcoming_shows_count = len(upcoming_shows)
        past_shows_count = len(past_shows)

    # handling empty results
    if venue_details is not None:
        data = {
            'id': venue_details.id,
            'name': venue_details.name,
            'genres': venue_details.genres,
            'city': venue_details.city,
            'state': venue_details.state,
            'address': venue_details.address,
            'phone': venue_details.phone,
            'website': venue_details.website,
            'facebook_link': venue_details.facebook_link,
            'image_link': venue_details.image_link,
            'seeking_talent': venue_details.seeking_talent,
            'seeking_description': venue_details.seeking_description,
            'past_shows': past_shows,
            'upcoming_shows': upcoming_shows,
            'past_shows_count': past_shows_count,
            'upcoming_shows_count': upcoming_shows_count
        }
    else:
        flash('Error! Details on Venue with ID: ' + str(venue_id) + ' is not found.')
        return redirect('/venues')
    # data1 = {
    #     "id": 1,
    #     "name": "The Musical Hop",
    #     "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    #     "address": "1015 Folsom Street",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "123-123-1234",
    #     "website": "https://www.themusicalhop.com",
    #     "facebook_link": "https://www.facebook.com/TheMusicalHop",
    #     "seeking_talent": True,
    #     "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    #     "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    #     "past_shows": [{
    #         "artist_id": 4,
    #         "artist_name": "Guns N Petals",
    #         "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #         "start_time": "2019-05-21T21:30:00.000Z"
    #     }],
    #     "upcoming_shows": [],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 0,
    # }
    # data2 = {
    #     "id": 2,
    #     "name": "The Dueling Pianos Bar",
    #     "genres": ["Classical", "R&B", "Hip-Hop"],
    #     "address": "335 Delancey Street",
    #     "city": "New York",
    #     "state": "NY",
    #     "phone": "914-003-1132",
    #     "website": "https://www.theduelingpianos.com",
    #     "facebook_link": "https://www.facebook.com/theduelingpianos",
    #     "seeking_talent": False,
    #     "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    #     "past_shows": [],
    #     "upcoming_shows": [],
    #     "past_shows_count": 0,
    #     "upcoming_shows_count": 0,
    # }
    # data3 = {
    #     "id": 3,
    #     "name": "Park Square Live Music & Coffee",
    #     "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    #     "address": "34 Whiskey Moore Ave",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "415-000-1234",
    #     "website": "https://www.parksquarelivemusicandcoffee.com",
    #     "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    #     "seeking_talent": False,
    #     "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #     "past_shows": [{
    #         "artist_id": 5,
    #         "artist_name": "Matt Quevedo",
    #         "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #         "start_time": "2019-06-15T23:00:00.000Z"
    #     }],
    #     "upcoming_shows": [{
    #         "artist_id": 6,
    #         "artist_name": "The Wild Sax Band",
    #         "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #         "start_time": "2035-04-01T20:00:00.000Z"
    #     }, {
    #         "artist_id": 6,
    #         "artist_name": "The Wild Sax Band",
    #         "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #         "start_time": "2035-04-08T20:00:00.000Z"
    #     }, {
    #         "artist_id": 6,
    #         "artist_name": "The Wild Sax Band",
    #         "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #         "start_time": "2035-04-15T20:00:00.000Z"
    #     }],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 1,
    # }
    # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    # print(request.form)
    # create a new Venue object and add to the db
    venue = Venue(name=request.form.get('name'),
                  city=request.form.get('city'),
                  state=request.form.get('state'),
                  address=request.form.get('address'),
                  phone=request.form.get('phone'),
                  genres=request.form.getlist('genres'),
                  website=request.form.get('website'),
                  facebook_link=request.form.get('facebook_link'),
                  image_link=request.form.get('image_link'),
                  seeking_talent=True if request.form.get('seeking') == 'Yes' else False,
                  seeking_description=request.form.get('seeking_description'))

    # handling exceptions
    try:
        # on successful db insert, flash success
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        db.session.rollback()
        flash('Error! issue faced while trying to add ' + request.form['name'])
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using


    flash('Venue has been successfully deleted.')
    return redirect('/')


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database

    data = []
    # collect IDs and names of all artist from DB
    all_artists = db.session.query(Artist.id, Artist.name)
    # add to the data set
    for artist in all_artists:
        data.append({
            'id': artist[0],
            'name': artist[1]
        })

    # data = [{
    #     "id": 4,
    #     "name": "Guns N Petals",
    # }, {
    #     "id": 5,
    #     "name": "Matt Quevedo",
    # }, {
    #     "id": 6,
    #     "name": "The Wild Sax Band",
    # }]
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    data = []
    count = 0
    search_term = request.form.get('search_term')
    # ilike is used for case insensitive search results
    found_artists = db.session.query(Artist.id, Artist.name).filter(Artist.name.like('%' + search_term + '%')).all()

    if found_artists is not None:
        for artist in found_artists:
            data.append({
                'id': artist[0],
                'name': artist[1]
            })
        count = len(found_artists)

    response = {
        'count': count,
        'data': data
    }
    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    current_date = datetime.datetime.now()

    artist_details = db.session.query(Artist).get(artist_id)
    artist_shows = db.session.query(Shows).filter(Shows.artist_id == artist_id)

    # variables to be populated with shows details
    past_shows = []
    upcoming_shows = []
    upcoming_shows_count = 0
    past_shows_count = 0

    if artist_shows is not None:
        for show in artist_shows:
            if show.start_time > current_date:
                upcoming_shows.append({
                    'venue_id': show.venue_id,
                    'venue_name': show.venue.name,
                    'venue_image_link': show.venue.image_link,
                    'start_time': str(show.start_time)
                })
            else:
                past_shows.append({
                    'venue_id': show.venue_id,
                    'venue_name': show.venue.name,
                    'venue_image_link': show.venue.image_link,
                    'start_time': str(show.start_time)
                })
        upcoming_shows_count = len(upcoming_shows)
        past_shows_count = len(past_shows)

    # handle empty results
    if artist_details is not None:
        data = {
            'id': artist_details.id,
            'name': artist_details.name,
            'genres': artist_details.genres,
            'city': artist_details.city,
            'state': artist_details.state,
            'phone': artist_details.phone,
            'website': artist_details.website,
            'facebook_link': artist_details.facebook_link,
            'image_link': artist_details.image_link,
            'seeking_venue': artist_details.seeking_venue,
            'seeking_description': artist_details.seeking_description,
            'past_shows': past_shows,
            'upcoming_shows': upcoming_shows,
            'past_shows_count': past_shows_count,
            'upcoming_shows_count': upcoming_shows_count
        }
    else:
        flash('Error! Details on Artist with ID: ' + str(artist_id) + ' is not found.')
        return redirect('/artists')

    # data1 = {
    #     "id": 4,
    #     "name": "Guns N Petals",
    #     "genres": ["Rock n Roll"],
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "326-123-5000",
    #     "website": "https://www.gunsnpetalsband.com",
    #     "facebook_link": "https://www.facebook.com/GunsNPetals",
    #     "seeking_venue": True,
    #     "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    #     "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #     "past_shows": [{
    #         "venue_id": 1,
    #         "venue_name": "The Musical Hop",
    #         "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    #         "start_time": "2019-05-21T21:30:00.000Z"
    #     }],
    #     "upcoming_shows": [],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 0,
    # }
    # data2 = {
    #     "id": 5,
    #     "name": "Matt Quevedo",
    #     "genres": ["Jazz"],
    #     "city": "New York",
    #     "state": "NY",
    #     "phone": "300-400-5000",
    #     "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    #     "seeking_venue": False,
    #     "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #     "past_shows": [{
    #         "venue_id": 3,
    #         "venue_name": "Park Square Live Music & Coffee",
    #         "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #         "start_time": "2019-06-15T23:00:00.000Z"
    #     }],
    #     "upcoming_shows": [],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 0,
    # }
    # data3 = {
    #     "id": 6,
    #     "name": "The Wild Sax Band",
    #     "genres": ["Jazz", "Classical"],
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "432-325-5432",
    #     "seeking_venue": False,
    #     "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "past_shows": [],
    #     "upcoming_shows": [{
    #         "venue_id": 3,
    #         "venue_name": "Park Square Live Music & Coffee",
    #         "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #         "start_time": "2035-04-01T20:00:00.000Z"
    #     }, {
    #         "venue_id": 3,
    #         "venue_name": "Park Square Live Music & Coffee",
    #         "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #         "start_time": "2035-04-08T20:00:00.000Z"
    #     }, {
    #         "venue_id": 3,
    #         "venue_name": "Park Square Live Music & Coffee",
    #         "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #         "start_time": "2035-04-15T20:00:00.000Z"
    #     }],
    #     "past_shows_count": 0,
    #     "upcoming_shows_count": 3,
    # }
    # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    # query existing artist details from DB
    artist_details = db.session.query(Artist).get(artist_id)
    # pass the artist object to populate the Editing form with current values
    form = ArtistForm(obj=artist_details)
    data = {
        'id': artist_details.id,
        'name': artist_details.name
        # 'genres': artist_details.genres,
        # 'city': artist_details.city,
        # 'state': artist_details.state,
        # 'phone': artist_details.phone,
        # 'website': artist_details.website,
        # 'facebook_link': artist_details.facebook_link,
        # 'image_link': artist_details.image_link,
        # 'seeking_venue': artist_details.seeking_venue,
        # 'seeking_description': artist_details.seeking_description
    }
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=data)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    artist_details = db.session.query(Artist).get(artist_id)

    artist_details.name = request.form.get('name')
    artist_details.city = request.form.get('city')
    artist_details.state = request.form.get('state')
    artist_details.phone = request.form.get('phone')
    artist_details.genres = request.form.getlist('genres')
    artist_details.website = request.form.get('website')
    artist_details.facebook_link = request.form.get('facebook_link')
    artist_details.image_link = request.form.get('image_link')
    artist_details.seeking_venue = True if request.form.get('seeking') == 'Yes' else False
    artist_details.seeking_description = request.form.get('seeking_description')

    try:
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue_details = db.session.query(Venue).get(venue_id)
    # pass the venue object to populate the Editing form with current values
    form = VenueForm(obj=venue_details)
    data = {
        'id': venue_details.id,
        'name': venue_details.name
        # 'genres': venue_details.genres,
        # 'city': venue_details.city,
        # 'state': venue_details.state,
        # 'address': venue_details.address,
        # 'phone': venue_details.phone,
        # 'website': venue_details.website,
        # 'facebook_link': venue_details.facebook_link,
        # 'image_link': venue_details.image_link,
        # 'seeking_talent': venue_details.seeking_talent,
        # 'seeking_description': venue_details.seeking_description
    }
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=data)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    venue_details = db.session.query(Venue).get(venue_id)

    venue_details.name = request.form.get('name')
    venue_details.city = request.form.get('city')
    venue_details.state = request.form.get('state')
    venue_details.address = request.form.get('address')
    venue_details.phone = request.form.get('phone')
    venue_details.genres = request.form.getlist('genres')
    venue_details.website = request.form.get('website')
    venue_details.facebook_link = request.form.get('facebook_link')
    venue_details.image_link = request.form.get('image_link')
    venue_details.seeking_talent = True if request.form.get('seeking') == 'Yes' else False
    venue_details.seeking_description = request.form.get('seeking_description')

    try:
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    print(request.form)

    artist = Artist(name=request.form.get('name'),
                    city=request.form.get('city'),
                    state=request.form.get('state'),
                    phone=request.form.get('phone'),
                    genres=request.form.getlist('genres'),
                    website=request.form.get('website'),
                    facebook_link=request.form.get('facebook_link'),
                    image_link=request.form.get('image_link'),
                    seeking_venue=True if request.form.get('seeking') == 'Yes' else False,
                    seeking_description=request.form.get('seeking_description'))

    try:
        # on successful db insert, flash success
        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
        db.session.rollback()
        flash('Error! issue faced while trying to add ' + request.form['name'])
    finally:
        db.session.close()

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.

    data = []
    all_shows = db.session.query(Shows)
    # add to the data set with usage of relationship backref with Venue and Artist
    for show in all_shows:
        data.append({
            'venue_id': show.venue_id,
            'venue_name': show.venue.name,
            'artist_id': show.artist_id,
            'artist_name': show.artist.name,
            'artist_image_link': show.artist.image_link,
            'start_time': str(show.start_time)
        })

    # data = [{
    #     "venue_id": 1,
    #     "venue_name": "The Musical Hop",
    #     "artist_id": 4,
    #     "artist_name": "Guns N Petals",
    #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #     "start_time": "2019-05-21T21:30:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 5,
    #     "artist_name": "Matt Quevedo",
    #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #     "start_time": "2019-06-15T23:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-01T20:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-08T20:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-15T20:00:00.000Z"
    # }]
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    show = Shows(artist_id=request.form.get('artist_id'),
                 venue_id=request.form.get('venue_id'),
                 start_time=request.form.get('start_time'))

    try:
        # on successful db insert, flash success
        db.session.add(show)
        db.session.commit()
        flash('Show to be held in ' + request.form['start_time'] + ' was successfully listed!')
    except:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
        db.session.rollback()
        flash('Error! Show could not be listed.')
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
