from flask import Blueprint, render_template, current_app, request, redirect, url_for
from bson import ObjectId
from bson.json_util import dumps
from datetime import datetime, timedelta
from .utils import upload_image_to_cloudinary, get_location_data

home_bp = Blueprint('home', __name__)


def get_date_range(start, end):
    delta = end - start

    date_list = [
        (start + timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(delta.days + 1)
    ]
    return date_list


@home_bp.route("/")
def index():
    db = current_app.db
    trips = list(db.trips.find().sort("start_date", -1))
    for trip in trips:
        trip["_id"] = str(trip["_id"])

    trips_json = dumps(trips)

    return render_template("index.html", trips=trips, trips_json=trips_json)



@home_bp.route("/add", methods=["POST"])
def add_trip():
    db = current_app.db
    # Exemplo básico de dados coletados de um formulário
    name = request.form.get("name")
    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")
    location = request.form.get("location")
    image_filename = request.files.get("image")

    start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
    end_datetime = datetime.strptime(end_date, "%Y-%m-%d")

    location_info = get_location_data(location)


    print(image_filename)
    trip = {
        "name": name,
        "start_date": start_datetime,
        "end_date": end_datetime,
        "dates": get_date_range(start_datetime, end_datetime),
        "location": location,
        "img": upload_image_to_cloudinary(image_filename),
        "year": datetime.strptime(start_date, "%Y-%m-%d").year,
        "lat": location_info["lat"],
        "lng": location_info["lng"],
        "country_name": location_info["country"],
        "country_code": location_info["country_code"],


    }

    inserted = db.trips.insert_one(trip)
    trip_id = str(inserted.inserted_id)

    return redirect(url_for('trip.view_trip', trip_id=trip_id))
