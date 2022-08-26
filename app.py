#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from distutils.util import strtobool
import json
import dateutil.parser
import enum
from datetime import datetime
from pprint import pprint
import babel
import logging
from logging import Formatter, FileHandler

from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import Form
from flask_migrate import Migrate

from sqlalchemy import func

from forms import *
from models import db_connect, Venue, Artist, Show


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)

db = db_connect(app)

migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

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
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  today = datetime.now()
  venues = Venue.query.group_by(Venue.id, Venue.state, Venue.city).all()
  state_city = ''
  all_venues = []

  for venue in venues:
    print("Venue", venue)
    upcoming_shows = venue.shows.filter(Show.start_time > today).all()
    current_city_and_state = venue.city + venue.state

    if current_city_and_state != state_city:
      state_city = current_city_and_state
      all_venues.append({
        'city': venue.city,
        'state': venue.state,
        'venues': [{
          'id':venue.id,
          'name': venue.name,
          'num_upcoming_shows': len(upcoming_shows)
        }]
      })
    else:
      all_venues[len(all_venues) -1]['venues'].append({
        'name':venue.name,
        'id':venue.id,
        'num_upcoming_shows': len(upcoming_shows)
      })

  

 
  return render_template('pages/venues.html', areas=all_venues)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  today = datetime.now()
  search_term = request.form['search_term']
  results = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term))).all()
  my_response = {
    'count':len(results),
    'data': []
  }
  for result in results:
    upcoming_shows = result.shows.filter(Show.start_time > today).all()
    my_response['data'].append({
      'id': result.id,
      'name': result.name,
      'num_upcoming_shows': len(upcoming_shows)
    })

  print(my_response)

  return render_template('pages/search_venues.html', results=my_response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  today = datetime.now()
  venue_query = Venue.query.get(venue_id)
  pprint(dir(venue_query))

  if venue_query:
    
    past_shows = venue_query.shows.filter(Show.start_time < today).all()
    upcoming_shows = venue_query.shows.filter(Show.start_time > today).all()


    # pprint(dir(venue_query))
    # print(venue_query.__dict__)

    # Convert the show start_times to string format
    for show in past_shows:
      show.start_time = str(show.start_time)
    
    for show in upcoming_shows:
      show.start_time = str(show.start_time)

    # Get the venue data into a dictionary and make modifications
    venue = venue_query.__dict__
    venue['genres'] = json.loads(venue_query.genres)
    venue['past_shows'] = past_shows
    venue['upcoming_shows'] = upcoming_shows
    
      
  return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  form = VenueForm(request.form)
  error = False
  try:
    if form.validate():
      new_venue = Venue(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            address = form.address.data,
            phone=form.phone.data,
            genres=json.dumps(form.genres.data),
            facebook_link=form.facebook_link.data,
            image_link=form.image_link.data,
            website_link=form.website_link.data,
            seeking_talent=form.seeking_talent.data,
            seeking_description=form.seeking_description.data,
      )
      print(new_venue)
      db.session.add(new_venue)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    else:
      print("Error!")
      flash(form.errors)

  except Exception as e:
    error = True
    print(e)
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')

  finally:
    db.session.close()
  
  if not error:
    return render_template('pages/home.html')
  else:
    abort(400)



  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    error = False
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  
  except Exception as e:
    db.session.rollback()
    error = True
    print(e)

  finally:
    db.session.close()

  if not error:
    flash("Successfully deleted")
  else:
    abort(400)

  return redirect(url_for('index'))



  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  artists = Artist.query.all()

  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  today = datetime.now()
  search_term = request.form['search_term']
  results = Artist.query.filter(
      Artist.name.ilike('%{}%'.format(search_term))).all()
  my_response = {
      'count': len(results),
      'data': []
  }
  for result in results:
    upcoming_shows = result.shows.filter(Show.start_time > today).all()
    my_response['data'].append({
        'id': result.id,
        'name': result.name,
        'num_upcoming_shows': len(upcoming_shows)
    })

  return render_template('pages/search_artists.html', results=my_response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  today = datetime.today()
  artist_query = Artist.query.get(artist_id)

  if artist_query:

    #query show details for the artist
    
    past_shows = artist_query.shows.filter(Show.start_time < today).all()
    upcoming_shows = artist_query.shows.filter(Show.start_time > today).all()
    
    # Convert the show start_times to string format
    for show in past_shows:
      show.start_time = str(show.start_time)
    
    for show in upcoming_shows:
      show.start_time = str(show.start_time)

    #Artist object to display on front end
    artist = artist_query.__dict__

    artist['genres'] = artist_query.genres.split(',')
    artist['past_shows'] = past_shows
    artist['upcoming_shows'] = upcoming_shows

  return render_template('pages/show_artist.html', artist=artist)

#  UPDATE
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)



@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form)
  artist = Artist.query.get(artist_id)
  error = False
  try:
    if form.validate():
      artist.name=form.name.data
      artist.city=form.city.data
      artist.state=form.state.data
      artist.phone=form.phone.data
      artist.genres=json.dumps(form.genres.data)
      artist.facebook_link=form.facebook_link.data
      artist.image_link=form.image_link.data
      artist.website_link=form.website_link.data
      artist.seeking_venue=form.seeking_venue.data
      artist.seeking_description=form.seeking_description.data

      db.session.commit()
    
    else:
      print(form.errors)
  
  except Exception as e:
    print(e)
    db.session.rolback()
    error = True

  if not error:
    flash('Artist ' + request.form['name'] + ' was successfully Edited!')
  else:
    abort(400)

  return redirect(url_for('show_artist', artist_id=artist_id))



@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm(request.form)
  venue = Venue.query.get(venue_id)

  return render_template('forms/edit_venue.html', form=form, venue=venue)
  # TODO: populate form with values from venue with ID <venue_id>
  

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  venue = Venue.query.get(venue_id)
  error = False
  try:
    if form.validate():
      venue.name = form.name.data
      venue.city = form.city.data
      venue.state = form.state.data
      venue.phone = form.phone.data
      venue.genres = json.dumps(form.genres.data)
      venue.facebook_link = form.facebook_link.data
      venue.image_link = form.image_link.data
      venue.website_link = form.website_link.data
      venue.seeking_talent = form.seeking_talent.data
      venue.seeking_description = form.seeking_description.data

      db.session.commit()

      flash('Venue ' + request.form['name'] + ' was successfully Edited!')
    else:
      error = True
      print(form.errors)
  except Exception as e:
    error = True
    db.session.rollback()
    print(e)

  if not error:
    return redirect(url_for('show_venue', venue_id=venue_id))
  else:
    abort(400)
  

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():

  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

  error = False
  form = ArtistForm(request.form)
  print("Started...")
  try:
    if form.validate():
      print("Valid")

      new_artist = Artist(
          name=form.name.data,
          city=form.city.data,
          state=form.state.data,
          phone=form.phone.data,
          genres=json.dumps(form.genres.data),
          facebook_link=form.facebook_link.data,
          image_link=form.image_link.data,
          website_link=form.website_link.data,
          seeking_venue=form.seeking_venue.data,
          seeking_description=form.seeking_description.data,
      )

    
      print(new_artist)
      db.session.add(new_artist)
      db.session.commit()

      flash('Artist ' + request.form['name'] + ' was successfully listed!')
      
    else:
      print("error")
      flash(form.errors)
      
  except Exception as e:
    error = True
    print(e)
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')

  finally:
    db.session.close()
  if not error:
    return render_template('pages/home.html')
  else:
    abort(400)


  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows_query = Show.query.all()

  shows = []

  for show in shows_query:
    shows.append({
      'venue_id': show.venue_id,
      'venue_name': show.Venue.name,
      'artist_id':show.artist_id,
      'artist_name':show.Artist.name,
      'artist_image_link':show.Artist.image_link,
      'start_time':str(show.start_time)
    })

  return render_template('pages/shows.html', shows=shows)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
 

  error = False
  form = ShowForm()
  try:
    if form.validate():
      print(request.form['artist_id'])
      print(request.form['venue_id'])
      print(form.start_time.data)

      print("Valid")
      new_show = Show(
          artist_id=request.form['artist_id'],
          venue_id=request.form['venue_id'],
          start_time=form.start_time.data,
      )

      db.session.add(new_show)
      db.session.commit()

      flash('Show was successfully listed!')

    else:
      print("error")

  except Exception as e:
    error = True
    print(e)
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')

  finally:
    db.session.close()
  
  if not error:
    return render_template('pages/home.html')
  
  else:
    abort(400)

 # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  

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
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
