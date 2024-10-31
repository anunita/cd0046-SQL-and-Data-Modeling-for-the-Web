#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
import dateutil.parser
import babel
from flask import (
  Flask, 
  render_template, 
  request, 
  Response, 
  flash, 
  redirect, 
  url_for
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import os
import sys
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

#
# import models from models.py
# 
from models import db, Venue, Artist, Show

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

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

 data = []
 citystate = Venue.query.distinct(Venue.city, Venue.state).all()

 for citysta in citystate:
   venlist = Venue.query.filter_by(state=citysta.state).filter_by(city=citysta.city).all()
   ven_list = []
   for ven in venlist:
     upcom_shows= len(db.session.query(Show).filter(Show.venue_id==ven.id).filter(Show.start_time>datetime.now()).all())
     ven_list.append({
       "id": ven.id,
       "name": ven.name,
       "num_upcoming_shows": upcom_shows
     })
    
   data.append({
      "city": citysta.city,
      "state": citysta.state,
      "venues": ven_list
    })
 return render_template('pages/venues.html', areas=data);


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  search_str = request.form.get('search_term','')
  ven_search = Venue.query.filter(Venue.name.ilike('%' + search_str + '%')).all()
  count_search = len(ven_search)
  data = []

  for ven in ven_search:
    data.append({
      "id": ven.id,
      "name": ven.name,
      "num_upcoming_shows": len(db.session.query(Show).filter(Show.venue_id==ven.id).filter(Show.start_time>datetime.now()).all())
    })
  response={
    "count": count_search,
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  ven_details = Venue.query.filter(Venue.id == venue_id).all()
  
  # get the details of past show
  past_shows = db.session.query(Show).filter(Show.venue_id == venue_id).join(Artist).filter(Show.start_time<datetime.now()).all()
  past_showlist = []

  for past in past_shows:
    past_showlist.append({
      "artist_id": past.artist_id,
      "artist_name": past.artist.name,
      "artist_image_link": past.artist.image_link,
      "start_time": past.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })
# get the details of upcoming  show

  upcoming_shows = db.session.query(Show).filter(Show.venue_id == venue_id).join(Artist).filter(Show.start_time>datetime.now()).all()
  upcoming_showlist = []

  for upcom in upcoming_shows:
    upcoming_showlist.append({
      "artist_id": upcom.artist_id,
      "artist_name": upcom.artist.name,
      "artist_image_link": upcom.artist.image_link,
      "start_time": upcom.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

  data = {}

  for ven in ven_details:
    data.update({
      "id": ven.id,
      "name": ven.name,
      "genres": ven.genres,
      "address": ven.address,
      "city": ven.city,
      "state": ven.state,
      "phone": ven.phone,
      "website": ven.website,
      "facebook_link": ven.facebook_link,
      "seeking_talent": ven.seeking_talent,
      "seeking_description": ven.seeking_description,
      "image_link": ven.image_link,
      "past_shows": past_showlist,
      "upcoming_shows": upcoming_showlist,
      "past_shows_count": len(past_showlist),
      "upcoming_shows_count": len(upcoming_showlist)
    })

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
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  error = False
  form_v = VenueForm(request.form)
  
  if form_v.validate():
    try:
      add_ven = Venue(
        name=form_v.name.data,
        city=form_v.city.data,
        state=form_v.state.data,
        address=form_v.address.data,
        phone=form_v.phone.data,
        genres=form_v.genres.data,
        image_link=form_v.image_link.data,
        facebook_link=form_v.facebook_link.data,
        website=form_v.website_link.data,
        seeking_talent=form_v.seeking_talent.data, 
        seeking_description=form_v.seeking_description.data
      )
      db.session.add(add_ven)
      db.session.commit()
    except Exception as e:
      error = True
      db.session.rollback()
      print(f'Error: {e}')
      flash('Venue ' + request.form['name'] + ' could not be listed.')
    finally:
      db.session.close()
  else:
    error = True
    flash('Form validation failed. Please check your inputs and try again.')

  if not error:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  error = False
  try:
    ven_det = Venue.query.filter(Venue.id == venue_id).all()
    db.session.delete(ven_det)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  
  if error:
    flash('Venue ' + venue_id + ' could not be deleted.')
  else:
    flash('Venue ' + venue_id + ' was successfully deleted.')
  
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  data = []
  artst = db.session.query(Artist).all()

  for artist in artst:
    data.append({
      "id": artist.id,
      "name": artist.name
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  
  
  search_str = request.form.get('search_term','')
  art_search = Artist.query.filter(Artist.name.ilike('%' + search_str + '%')).all()
  count_search = len(art_search)
  data = []

  for art in art_search:
    data.append({
      "id": art.id,
      "name": art.name,
      "num_upcoming_shows": len(db.session.query(Show).filter(Show.artist_id==art.id).filter(Show.start_time>datetime.now()).all())
    })
  response={
    "count": count_search,
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

  artst_dets = Artist.query.filter(Artist.id == artist_id).all()
  
  # get the details of past show
  past_shows = db.session.query(Show).filter(Show.artist_id == artist_id).join(Venue).filter(Show.start_time<datetime.now()).all()
  past_showlist = []

  for past in past_shows:
    past_showlist.append({
      "venue_id": past.venue_id,
      "venue_name": past.venue.name,
      "venue_image_link": past.venue.image_link,
      "start_time": past.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })
  # get the details of upcoming  show

  upcoming_shows = db.session.query(Show).filter(Show.artist_id == artist_id).join(Venue).filter(Show.start_time>datetime.now()).all()
  upcoming_showlist = []

  for upcom in upcoming_shows:
    upcoming_showlist.append({
      "venue_id": upcom.venue_id,
      "venue_name": upcom.venue.name,
      "venue_image_link": upcom.venue.image_link,
      "start_time": upcom.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

  data = {}

  for art in artst_dets:
    data.update({
      "id": art.id,
      "name": art.name,
      "genres": art.genres,
      "city": art.city,
      "state": art.state,
      "phone": art.phone,
      "website": art.website,
      "facebook_link": art.facebook_link,
      "seeking_venue": art.seeking_venue,
      "seeking_description": art.seeking_description,
      "image_link": art.image_link,
      "past_shows": past_showlist,
      "upcoming_shows": upcoming_showlist,
      "past_shows_count": len(past_showlist),
      "upcoming_shows_count": len(upcoming_showlist)
    })

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = db.session.get(Artist, artist_id)
 
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.genres.data = artist.genres
  form.facebook_link.data = artist.facebook_link
  form.image_link.data = artist.image_link
  form.website_link.data = artist.website
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  error = False
  upd_art = db.session.get(Artist, artist_id)
  form_a = ArtistForm(request.form)

  if form_a.validate():
    try:
      upd_art.name = form_a.name.data
      upd_art.city = form_a.city.data
      upd_art.state = form_a.state.data
      upd_art.phone = form_a.phone.data
      upd_art.genres = form_a.genres.data
      upd_art.image_link = form_a.image_link.data
      upd_art.facebook_link = form_a.facebook_link.data  
      upd_art.website = form_a.website_link.data
      upd_art.seeking_venue = form_a.seeking_venue.data
      upd_art.seeking_description = form_a.seeking_description.data
      
      db.session.commit()
    except Exception as e:
        error = True
        db.session.rollback()
        print(f'Error: {e}')
        flash('Artist ' + request.form['name'] + ' could not be updated.')
    finally:
        db.session.close()
  else:
    error = True
    flash('Form validation failed. Please check your inputs and try again.')

  if not error:
    flash('Artist ' + request.form['name'] + ' was successfully updated!')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = db.session.get(Venue, venue_id)

  form.name.data = venue.name
  form.address.data = venue.address
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.genres.data = venue.genres
  form.facebook_link.data = venue.facebook_link
  form.image_link.data = venue.image_link
  form.website_link.data = venue.website
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False
  upd_ven = db.session.get(Venue, venue_id)
  form_v = VenueForm(request.form)

  if form_v.validate():
    try:
      upd_ven.name = form_v.name.data
      upd_ven.address = form_v.address.data
      upd_ven.city = form_v.city.data
      upd_ven.state = form_v.state.data
      upd_ven.phone = form_v.phone.data
      upd_ven.genres = form_v.genres.data
      upd_ven.image_link = form_v.image_link.data
      upd_ven.facebook_link = form_v.facebook_link.data  
      upd_ven.website = form_v.website_link.data
      upd_ven.seeking_talent = form_v.seeking_talent.data
      upd_ven.seeking_description = form_v.seeking_description.data
      
      db.session.commit()
    except Exception as e:
        error = True
        db.session.rollback()
        print(f'Error: {e}')
        flash('Venue ' + request.form['name'] + ' could not be updated.')
    finally:
        db.session.close()
  else:
    error = True
    flash('Form validation failed. Please check your inputs and try again.')

  if not error:
    flash('Venue ' + request.form['name'] + ' was successfully updated!')

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
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')

  error = False
  form_a = ArtistForm(request.form)
  
  if form_a.validate():
    try:
      add_art = Artist(
        name=form_a.name.data,
        city=form_a.city.data,
        state=form_a.state.data,
        phone=form_a.phone.data,
        genres=form_a.genres.data,
        image_link=form_a.image_link.data,
        facebook_link=form_a.facebook_link.data,
        website=form_a.website_link.data,
        seeking_venue=form_a.seeking_venue.data, 
        seeking_description=form_a.seeking_description.data
      )
      db.session.add(add_art)
      db.session.commit()
    except Exception as e:
      error = True
      db.session.rollback()
      print(f'Error: {e}')
      flash('Artist ' + request.form['name'] + ' could not be listed.')
    finally:
      db.session.close()
  else:
    error = True
    flash('Form validation failed. Please check your inputs and try again.')

  if not error:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.

  shows_data = db.session.query(Show).join(Artist).join(Venue).all()
  data = []
  
  for shows in shows_data:
    data.append({
      "venue_id": shows.venue_id,
      "venue_name": shows.venue.name,
      "artist_id": shows.artist_id,
      "artist_name": shows.artist.name, 
      "artist_image_link": shows.artist.image_link,
      "start_time": shows.start_time.strftime('%Y-%m-%d %H:%M:%S')
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

  # on successful db insert, flash success

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  error = False
  form_s = ShowForm(request.form)
  
  if form_s.validate():
    try: 
      add_show = Show(
        venue_id=form_s.venue_id.data,
        artist_id=form_s.artist_id.data,
        start_time=form_s.start_time.data
      )
      db.session.add(add_show)
      db.session.commit()
    except Exception as e:
      error = True
      db.session.rollback()
      print(f'Error: {e}')
      flash('Show could not be listed!')
    finally:
      db.session.close()
  else:
    error = True
    flash('Form validation failed. Please check your inputs and try again.')

  if not error:
    flash('Show was successfully listed!')

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
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
'''
