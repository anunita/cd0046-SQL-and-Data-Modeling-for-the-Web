from datetime import datetime
from flask_wtf import FlaskForm as Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, AnyOf, URL, ValidationError
import re
from enums import Genre, State

def is_valid_phone(number):
    regex = re.compile(r'^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$')
    return regex.match(number)

class ShowForm(Form):
    artist_id = StringField(
        'artist_id'
    )
    venue_id = StringField(
        'venue_id'
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )

class VenueForm(Form):
    def validate_phone(self, field):
        if not is_valid_phone(field.data):
            raise ValidationError('Invalid phone.')
 
    def validate_genres(self, field):
        if not set(field.data).issubset(dict(Genre.choices()).keys()):
            raise ValidationError('Invalid genres.')
           
    def validate_state(self, field):
        if field.data not in dict(State.choices()).keys():
            raise ValidationError('Invalid state.')   
       
    def validate(self, **kwargs):
        # `**kwargs` to match the method's signature in the `FlaskForm` class.
        return super(VenueForm, self).validate(**kwargs)

    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=State.choices()
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone'
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        # TODO implement enum restriction
        'genres', validators=[DataRequired()],
        choices=Genre.choices()
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )
    website_link = StringField(
        'website_link'
    )

    seeking_talent = BooleanField( 'seeking_talent' )

    seeking_description = StringField(
        'seeking_description'
    )



class ArtistForm(Form):
    def validate_phone(self, field):
        if not is_valid_phone(field.data):
            raise ValidationError('Invalid phone.')

        
    def validate_genres(self, field):
        if not set(field.data).issubset(dict(Genre.choices()).keys()):
            raise ValidationError('Invalid genres.')
            
    def validate_state(self, field):
        if field.data not in dict(State.choices()).keys():
            raise ValidationError('Invalid state.')  
        
    def validate(self, **kwargs):
        # `**kwargs` to match the method's signature in the `FlaskForm` class.
        return super(ArtistForm, self).validate(**kwargs)

    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=State.choices()
    )
    phone = StringField(
        # TODO implement validation logic for state
        'phone'
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        choices=Genre.choices()
     )
    facebook_link = StringField(
        # TODO implement enum restriction
        'facebook_link', validators=[URL()]
     )

    website_link = StringField(
        'website_link'
     )

    seeking_venue = BooleanField( 'seeking_venue' )

    seeking_description = StringField(
            'seeking_description'
     )

