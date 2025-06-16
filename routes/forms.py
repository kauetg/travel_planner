from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, DecimalField, SelectField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Optional, URL, NumberRange


class TransportForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    departure = StringField('Departure', validators=[DataRequired()])
    arrival = StringField('Arrival', validators=[DataRequired()])


    cost = DecimalField("Cost", validators=[Optional(), NumberRange(min=0, message="Cost must be positive")])
    currency = SelectField("Currency", choices=[("SGD", "SGD"), ("USD", "USD"), ("MYR", "MYR")], default="SGD")
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

class AccommodationForm(FlaskForm):
    category = StringField('Category', default='Accommodation', render_kw={'readonly': True})
    title = StringField('Title', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    photo = StringField('Photo URL', validators=[Optional(), URL()])
    cost = DecimalField('Cost', validators=[Optional()])
    duration = StringField('Duration', validators=[Optional()])
    confirmed = BooleanField('Confirmed')

class ActivityForm(FlaskForm):
    category = SelectField(
        "Category",
        choices=[
            ("activity", "Things to do"),
            ("food", "Places to Eat "),
            ("accommodation", "Accommodation"),
            ("transportation", "Transportation"),

        ],
        validators=[Optional()]
    )

    title = StringField('Title', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    photo = StringField('Photo URL', validators=[Optional(), URL()])
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
    confirmed = BooleanField('Confirmed')

class FoodForm(FlaskForm):
    category = StringField('Category', default='Places to eat', render_kw={'readonly': True})
    title = StringField('Title', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    photo = StringField('Photo URL', validators=[Optional(), URL()])
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
