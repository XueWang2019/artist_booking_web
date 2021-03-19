#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from config import SQLALCHEMY_DATABASE_URI
from models import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

db.init_app(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database (Done)
app.config['SQLALCHEMY_DATABASE_URI']=SQLALCHEMY_DATABASE_URI


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"

  return babel.dates.format_datetime(date, format, locale='en')
app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')

def venues(): #Done
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  locations = set()
  venues = Venue.query.all()
  for venue in venues:
    locations.add((venue.city, venue.state))
  for location in locations:
    data.append({
      "city": location[0],
      "state": location[1],
      "venues": []
    })
  for venue in venues:
    num_upcoming_shows = 0
    shows = Show.query.filter_by(venue_id=venue.id).all()
    now = datetime.now()
    for show in shows:
      if show.start_time > now:
        num_upcoming_shows += 1
    for location in data:
      if venue.state == location['state'] and venue.city == location['city']:
        location['venues'].append({
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": num_upcoming_shows
        })
  return render_template('pages/venues.html', areas=data);
@app.route('/venues/search', methods=['POST'])
def search_venues(): #Done
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  new_results = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%')).all()
  data = []
  for result in new_results:
    data.append({
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": len(
        db.session.query(Show).filter(Show.venue_id == result.id).filter(Show.start_time > datetime.now()).all()),
    })

  response = {
    "count": len(new_results),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))





@app.route('/venues/<int:venue_id>')
def show_venue(venue_id): #Done
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id


 #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  venue_query = Venue.query.filter_by(id=venue_id).first_or_404()

  past_shows = db.session.query(Artist, Show).join(Show).join(Venue). \
    filter(
    Show.venue_id == venue_id,
    Show.artist_id == Artist.id,
    Show.start_time < datetime.now()
  ). \
    all()

  upcoming_shows = db.session.query(Artist, Show).join(Show).join(Venue). \
    filter(
    Show.venue_id == venue_id,
    Show.artist_id == Artist.id,
    Show.start_time > datetime.now()
  ). \
    all()

  data = {
    'id': venue_query.id,
    'city':venue_query.city,
    'state':venue_query.state,
    'address':venue_query.address,
    'phone':venue_query.phone,
    'facebook_link':venue_query.facebook_link,
    'website': venue_query.website,
    'past_shows': [{
      'artist_id': artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
    } for artist, show in past_shows],
    'upcoming_shows': [{
      'artist_id': artist.id,
      'artist_name': artist.name,
      'artist_image_link': artist.image_link,
      'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
    } for artist, show in upcoming_shows],
    'past_shows_count': len(past_shows),
    'upcoming_shows_count': len(upcoming_shows)}

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form(): #done
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission(): #done
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  #flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/


  form = VenueForm(request.form,meta={'csrf': False})
  if form.validate():
    try:
      new_venue = Venue(
        name=request.form['name'],
        city=request.form['city'],
        state=request.form['state'],
        phone=request.form['phone'],
        genres=request.form.getlist('genres'),
        address=request.form['address'],
        website=form.website.data,
        facebook_link=request.form['facebook_link'],
        image_link=request.form['image_link'],
        seeking_talent=form.seeking_talent.data,
        seeking_description=request.form['seeking_description']
        )

      db.session.add(new_venue)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except exc.SQLAlchemyError as e:
      print(e)
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
      db.session.rollback()
    finally:
      db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<int:venue_id>', methods=['POST'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  try:
    venue = Venue.query.filter_by(id=venue_id).first_or_404()
    current_session = db.object_session(venue)
    current_session.delete(venue)
    current_session.commit()
    flash('The venue has been removed together with all of its shows.')
    return render_template('pages/home.html')
  except ValueError:
    flash('It was not possible to delete this Venue')
  return redirect(url_for('venues'))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = db.session.query(Artist).all()
  return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():#Done
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  new_results = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).all()
  data = []
  for result in new_results:
    data.append({
      "id": result.id,
      "name": result.name
    })

  response = {
    "count": len(new_results),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id): #Done
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id


  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  #return render_template('pages/show_artist.html', artist=data)

  current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  artist_query = Artist.query.filter_by(id=artist_id).first_or_404()

  past_shows = db.session.query(Artist, Show).join(Show).join(Venue). \
    filter(
    Show.venue_id == Venue.id,
    Show.artist_id == artist_id,
    Show.start_time < datetime.now()
  ). \
    all()

  upcoming_shows = db.session.query(Artist, Show).join(Show).join(Venue). \
    filter(
    Show.venue_id == Venue.id,
    Show.artist_id == artist_id,
    Show.start_time > datetime.now()
  ). \
    all()

  data = {
    'id': artist_query.id,
    'city': artist_query.city,
    'state': artist_query.state,
    'phone': artist_query.phone,
    'facebook_link': artist_query.facebook_link,
    'website': artist_query.website,
    'past_shows': [{
      'artist_id': artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
    } for artist, show in past_shows],
    'upcoming_shows': [{
      'artist_id': artist.id,
      'artist_name': artist.name,
      'artist_image_link': artist.image_link,
      'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
    } for artist, show in upcoming_shows],
    'past_shows_count': len(past_shows),
    'upcoming_shows_count': len(upcoming_shows)}

  return render_template('pages/show_artist.html',artist=data)
#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.filter_by(id=artist_id).all()[0]
  form = ArtistForm(
    name=artist.name,
    city = artist.city,
    state = artist.state,
    phone = artist.phone,
    genres = artist.genres,
    website = artist.website,
    facebook_link = artist.facebook_link,
    image_link = artist.image_link,
    seeking_talent = artist.seeking_talent,
    seeking_description = artist.seeking_description
  )

  # TODO: populate form with fields from artist with ID <artist_id>
  #return render_template('forms/edit_artist.html', form=form, artist=artist)
  return render_template('forms/edit_artist.html', form=form)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  form = request.form.to_dict(True)
  genres = request.form.getlist('genres')
  seeking_venue = bool(request.form.get('seeking_venue'))
  try:
    artist = Artist.query.get(artist_id)
    artist.genres = []
    artist.name = form['name']
    artist.genres = list(map(lambda genre: Genre(name=genre), genres))
    artist.city = form['city']
    artist.state = form['state']
    artist.phone = form['phone']
    artist.website = form['website']
    artist.facebook_link = form['facebook_link']
    artist.seeking_venue = seeking_venue
    artist.seeking_description = form['seeking_description']
    artist.image_link = form['image_link']
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    flash('An error occurred. Artist ' + form['name'] + ' could not be updated.')
  finally:
    # DONE: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    if not error:
      db.session.close()
      flash('Artist ' + form['name'] + ' was successfully updated!')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

  venue = Venue.query.filter_by(id=venue_id).all()[0]
  form = VenueForm(
    name=venue.name,
    city=venue.city,
    state=venue.state,
    phone=venue.phone,
    genres=venue.genres,
    website=venue.website,
    facebook_link=venue.facebook_link,
    image_link=venue.image_link,
    seeking_talent=venue.seeking_talent,
    seeking_description=venue.seeking_description
  )

  # TODO: populate form with values from venue with ID <venue_id>
  #return render_template('forms/edit_venue.html', form=form, venue=venue)
  return render_template('forms/edit_venue.html', form=form)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  error = False
  form = request.form.to_dict(True)
  genres = request.form.getlist('genres')
  seeking_venue = bool(request.form.get('seeking_venue'))
  try:
    venue = Venue.query.get(venue_id)
    venue.genres = []
    venue.name = form['name']
    venue.genres = list(map(lambda genre: Genre(name=genre), genres))
    venue.city = form['city']
    venue.state = form['state']
    venue.phone = form['phone']
    venue.website = form['website']
    venue.facebook_link = form['facebook_link']
    venue.seeking_venue = seeking_venue
    venue.seeking_description = form['seeking_description']
    venue.image_link = form['image_link']
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    flash('An error occurred. Artist ' + form['name'] + ' could not be updated.')
  finally:
    # DONE: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    if not error:
      db.session.close()
      flash('Artist ' + form['name'] + ' was successfully updated!')

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

  # on successful db insert, flash success
  #flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  form = ArtistForm(request.form, meta={'csrf': False})
  try:
      new_artist = Artist(
        name=request.form['name'],
        city=request.form['city'],
        state=request.form['state'],
        phone=request.form['phone'],
        genres=request.form.getlist('genres'),
        website=form.website.data,
        facebook_link=request.form['facebook_link'],
        image_link=request.form['image_link'],
        seeking_talent=form.seeking_talent.data,
        seeking_description=request.form['seeking_description']
      )

      db.session.add(new_artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except exc.SQLAlchemyError as e:
      print(e)
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
      db.session.rollback()
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
  shows = Show.query.order_by(Show.start_time.desc()).all()
  for show in shows:
    venue = Venue.query.filter_by(id=show.venue_id).first_or_404()
    artist = Artist.query.filter_by(id=show.artist_id).first_or_404()
    data.extend([{
      "venue_id": venue.id,
      "venue_name": venue.name,
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
    }])

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

  # on successful db insert, flash success
  #flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  form = ShowForm()
  try:
    added_show = Show(
      artist_id=form.artist_id.data,
      venue_id=form.venue_id.data,
      start_time=form.start_time.data,
    )
    db.session.add(added_show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    db.session.rollback()
    flash('An error occurred. show could not be listed.')
  finally:
    db.session.close()
    return render_template('pages/home.html')
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

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
