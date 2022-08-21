#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from distutils.util import strtobool
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import enum
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app) 
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#




class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(300))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500), nullable=True)
    shows = db.relationship('Show', backref='Venue', lazy='dynamic')



    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website_link = db.Column(db.String(300))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500), nullable=True)
    shows = db.relationship('Show', backref='Artist', lazy='dynamic')

    

class Show(db.Model):
  __tablename__ = 'Show'
  id = db.Column(db.Integer, primary_key = True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  start_time= db.Column(db.DATETIME, nullable=False)




  
  

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

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
  data = []

  for venue in venues:
    print("Venue", venue)
    upcoming_shows = venue.shows.filter(Show.start_time > today).all()
    if state_city == venue.city + venue.state:
      data[len(data) -1]['venues'].append({
        'id':venue.id,
        'name':venue.name,
        'num_upcoming_shows':len(upcoming_shows)
      })
    
    else:
      state_city = venue.city + venue.state
      data.append({
        'city':venue.city,
        'state':venue.state,
        'venues': [{
          'id':venue.id,
          'name':venue.name,
          'num_upcoming_shows': len(upcoming_shows)
        }]
      })

      print(data)

  # query = Show.query.join(Venue).with_entities(Venue.city, Venue.state, Venue.name, Venue.id, func.count(Venue.id)).group_by(Venue.city, Venue.state, Venue.name, Venue.id)
  # print(query)

  # results = {}
  # for city, state, name, id, count_1 in query:
  #   location = (city, state)
  #   if location not in results:
  #     results[location]= []

  #   results[location].append(({"id":id, "name":name, "num_upcoming_shows":count_1}))
  #   #print(results.keys)

 
  return render_template('pages/venues.html', areas=data)

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

  if venue_query:
    past_shows = []
    upcoming_shows = []
    
    shows = venue_query.shows
    # Get the show details
    for show in shows:
      show_info = {
        'artist_id':show.artist_id,
        'artist_name':show.Artist.name,
        'artist_image_link':show.Artist.image_link,
        'start_time':str(show.start_time)
      }
      
      # Compare today's date with the start time
      if show.start_time > today:
        upcoming_shows.append(show_info)
      else:
        past_shows.append(show_info)

    venue = {
      "id":venue_query.id,
      'name':venue_query.name,
      'genres':venue_query.genres.split(','),
      'address':venue_query.address,
      'city':venue_query.city,
      'state':venue_query.state,
      'phone': venue_query.phone,
      'website': venue_query.website_link,
      'facebook_link': venue_query.facebook_link,
      'seeking_talent': venue_query.seeking_talent,
      'seeking_description':venue_query.seeking_description,
      'image_link': venue_query.image_link,
      'past_shows': past_shows,
      'upcoming_shows':upcoming_shows,
    }
      
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

  print(my_response)

  return render_template('pages/search_artists.html', results=my_response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  today = datetime.today()
  artist_query = Artist.query.get(artist_id)

  if artist_query:
    past_shows = []
    upcoming_shows = []

    #query show details for the artist
    shows = artist_query.shows
    
    for show in shows:
      show_info = {
        'venue_id': show.venue_id,
        'venue_name': show.Venue.name,
        'venue_image_link': show.Venue.image_link,
        'start_time':str(show.start_time)
      }

      #add the show into the appropriate list
      if show.start_time > today:
        upcoming_shows.append(show_info)
      else:
        past_shows.append(show_info)
    
    # Create the artist object
    artist = {
      'id': artist_query.id,
      'name': artist_query.name,
      'genres': artist_query.genres.split(','),
      'city': artist_query.city,
      'state': artist_query.state,
      'phone': artist_query.phone,
      'website': artist_query.website_link,
      'facebook_link': artist_query.facebook_link,
      'seeking_venue': artist_query.seeking_venue,
      'seeking_description': artist_query.seeking_description,
      'image_link':artist_query.image_link,
      'past_shows': past_shows,
      'upcoming_shows': upcoming_shows
    }

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
