from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, DecimalField, SelectField, TextAreaField, IntegerField, HiddenField
from wtforms.validators import DataRequired, Optional, URL, NumberRange
from .utils import currencies


class TransportForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    departure = StringField('Departure', validators=[DataRequired()])
    departure_lat = HiddenField()
    departure_lon = HiddenField()
    departure_map_image = HiddenField()
    arrival = StringField('Arrival', validators=[DataRequired()])
    arrival_lat = HiddenField()
    arrival_lon = HiddenField()
    arrival_map_image = HiddenField()
    cost = DecimalField("Cost", validators=[Optional(), NumberRange(min=0, message="Cost must be positive")])
    currency = SelectField("Currency", choices=[])  # define vazio aqui
    duration = IntegerField("Duration (h)",
                            validators=[Optional(), NumberRange(min=0, message="Duration must be positive")])
    confirmed = BooleanField('Confirmed')
    type = SelectField(
        "Transport Type",
        choices=[
            ("Plane", "Plane"),
            ("Boat", "Boat"),
            ("Bus", "Bus"),
            ("Car", "Rented Car"),
            ("Other", "Other"),
        ],
        validators=[Optional()]
    )

    def __init__(self, *args, **kwargs):
        self.trip = kwargs.pop('trip', None)
        super().__init__(*args, **kwargs)

        # Agora você pode acessar self.trip e preencher os choices
        if self.trip:
            self.currency.choices = currencies(self.trip["country_name"])


class AccommodationForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    cost = DecimalField('Cost', validators=[Optional()])
    duration = IntegerField('Number of Nights', validators=[Optional()])
    confirmed = BooleanField('Confirmed')
    currency = SelectField("Currency", choices=[])  # define vazio aqui
    type = SelectField(
        "Accomodation Type",
        choices=[
            ("Hotel", "Hotel"),
            ("Airbnb", "Airbnb"),
            ("Friends House", "Friends House"),
            ("Other", "Other"),
        ],
        validators=[Optional()]
    )

    def __init__(self, *args, **kwargs):
        self.trip = kwargs.pop('trip', None)
        super().__init__(*args, **kwargs)

        # Agora você pode acessar self.trip e preencher os choices
        if self.trip:
            self.currency.choices = currencies(self.trip["country_name"])


class ActivityForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    type = SelectField(
        "Activity Type",
        choices=[
            ("Tour", "Tour"),
            ("Dive", "Dive"),
            ("Museum", "Museum"),
            ("Hike", "Hike"),
            ("Other", "Other"),
        ],
        validators=[Optional()]
    )
    obs = TextAreaField('Observations', validators=[Optional()])
    cost = DecimalField('Cost', validators=[Optional()])
    currency = SelectField("Currency", choices=[])  # define vazio aqui
    confirmed = BooleanField('Confirmed')
    def __init__(self, *args, **kwargs):
        self.trip = kwargs.pop('trip', None)
        super().__init__(*args, **kwargs)

        # Agora você pode acessar self.trip e preencher os choices
        if self.trip:
            self.currency.choices = currencies(self.trip["country_name"])




class FoodForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    currency = SelectField("Currency", choices=[])  # define vazio aqui
    type = SelectField(
        "Activity Type",
        choices=[
            ("Full Meal", "Full Meal"),
            ("Snacks", "Snacks"),
            ("Desert", "Desert"),
        ],
        validators=[Optional()]
    )
    obs = TextAreaField('Observations', validators=[Optional()])
    cost = DecimalField('Cost', validators=[Optional()])
    confirmed = BooleanField('Confirmed')
    def __init__(self, *args, **kwargs):
        self.trip = kwargs.pop('trip', None)
        super().__init__(*args, **kwargs)

        # Agora você pode acessar self.trip e preencher os choices
        if self.trip:
            self.currency.choices = currencies(self.trip["country_name"])

