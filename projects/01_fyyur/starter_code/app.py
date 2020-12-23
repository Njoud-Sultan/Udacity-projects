# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

from sqlalchemy.types import ARRAY

import dateutil.parser
import babel
from flask import render_template, request, flash, redirect, url_for
from models import app, db, Venue, Artist, Shows
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

moment = Moment(app)
app.config.from_object('config')
db.init_app(app)


# ----------------------------------------------------------------------------#
# Models are in models.py
# ----------------------------------------------------------------------------#

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
    locations = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state)

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
    # venue_shows = db.session.query(Shows).filter(Shows.venue_id == venue_id)
    past_shows = db.session.query(Shows).join(Artist).filter(Shows.venue_id == venue_id,
                                                             Shows.start_time < current_date).all()
    upcoming_shows = db.session.query(Shows).join(Artist).filter(Shows.venue_id == venue_id,
                                                                 Shows.start_time > current_date).all()

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
            'past_shows': [{
                'artist_id': show.artist_id,
                'artist_name': show.artist.name,
                'artist_image_link': show.artist.image_link,
                'start_time': str(show.start_time)
            } for show in past_shows],
            'upcoming_shows': [{
                'artist_id': show.artist_id,
                'artist_name': show.artist.name,
                'artist_image_link': show.artist.image_link,
                'start_time': str(show.start_time)
            } for show in upcoming_shows],
            'past_shows_count': len(past_shows),
            'upcoming_shows_count': len(upcoming_shows)
        }
    else:
        flash('Error! Details on Venue with ID: ' + str(venue_id) + ' is not found.')
        return redirect('/venues')

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

    form = VenueForm(request.form)
    # create a new Venue object and add to the db
    venue = Venue(name=form.name.data,
                  city=form.city.data,
                  state=form.state.data,
                  address=form.address.data,
                  phone=form.phone.data,
                  genres=form.genres.data,
                  website=form.website.data,
                  facebook_link=form.facebook_link.data,
                  image_link=form.image_link.data,
                  seeking_talent=True if form.seeking.data == 'Yes' else False,
                  seeking_description=form.seeking_description.data)

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
    past_shows = db.session.query(Shows).join(Venue).filter(Shows.artist_id == artist_id,
                                                            Shows.start_time < current_date).all()
    upcoming_shows = db.session.query(Shows).join(Venue).filter(Shows.artist_id == artist_id,
                                                                Shows.start_time > current_date).all()

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
            'past_shows': [{
                'venue_id': show.venue_id,
                'venue_name': show.venue.name,
                'venue_image_link': show.venue.image_link,
                'start_time': str(show.start_time)
            } for show in past_shows],
            'upcoming_shows': [{
                'venue_id': show.venue_id,
                'venue_name': show.venue.name,
                'venue_image_link': show.venue.image_link,
                'start_time': str(show.start_time)
            } for show in upcoming_shows],
            'past_shows_count': len(past_shows),
            'upcoming_shows_count': len(upcoming_shows)
        }
    else:
        flash('Error! Details on Artist with ID: ' + str(artist_id) + ' is not found.')
        return redirect('/artists')

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

    form = ArtistForm(request.form)
    # create a new Venue object and add to the db
    artist = Artist(name=form.name.data,
                    city=form.city.data,
                    state=form.state.data,
                    phone=form.phone.data,
                    genres=form.genres.data,
                    website=form.website.data,
                    facebook_link=form.facebook_link.data,
                    image_link=form.image_link.data,
                    seeking_venue=True if form.seeking.data == 'Yes' else False,
                    seeking_description=form.seeking_description.data)

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

    form = ShowForm(request.form)
    show = Shows(artist_id=form.artist_id.data,
                 venue_id=form.venue_id.data,
                 start_time=form.start_time.data)

    try:
        # on successful db insert, flash success
        db.session.add(show)
        db.session.commit()
        flash('Show to be held in ' + request.form['start_time'] + ' is successfully listed!')
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
