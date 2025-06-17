from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, DecimalField, SelectField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Optional, URL, NumberRange
from .utils import currencies


class TransportForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    departure = StringField('Departure', validators=[DataRequired()])
    arrival = StringField('Arrival', validators=[DataRequired()])
    cost = DecimalField("Cost", validators=[Optional(), NumberRange(min=0, message="Cost must be positive")])
    currency = SelectField("Currency", choices=[])  # define vazio aqui
    duration = IntegerField("Duration (h)",
                            validators=[Optional(), NumberRange(min=0, message="Duration must be positive")])
    confirmed = BooleanField('Confirmed')
    type = SelectField(
        "Transport Type",
        choices=[
            ("plane", "Plane"),
            ("boat", "Boat"),
            ("bus", "Bus"),
            ("car", "Rented Car"),
            ("other", "Other"),
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
            ("tour", "Tour"),
            ("hike", "Hike"),
            ("dive", "Dive"),
            ("museum", "Museum"),
            ("other", "Other"),
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
            ("meal", "Full Meal"),
            ("snack", "Snacks"),
            ("desert", "Desert"),
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

