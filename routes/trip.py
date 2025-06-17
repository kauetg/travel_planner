from flask import Blueprint, render_template, current_app, request, redirect, url_for
from bson import ObjectId
from datetime import datetime
from .utils import convert_to_USD

from .forms import TransportForm, AccommodationForm, ActivityForm, FoodForm

trip_bp = Blueprint('trip', __name__, url_prefix='/trip')


@trip_bp.route("/<trip_id>")
def view_trip(trip_id):
    db = current_app.db
    trip = db.trips.find_one({"_id": ObjectId(trip_id)})
    trip["dates_formatted"] = [
        datetime.strptime(d, "%Y-%m-%d").strftime("%d-%b") for d in trip["dates"]
    ]
    categories = [
        {"label": "Things to do", "icon": "bi-ui-checks","category":"activity"},
        {"label": "Places to eat", "icon": "bi-fork-knife","category":"food"},
        {"label": "Accommodation", "icon": "bi-house-door-fill","category":"accommodation"},
        {"label": "Transportation", "icon": "bi-airplane-fill","category":"transportation"},
    ]
    return render_template("trip_detail.html", trip=trip, categories=categories)


@trip_bp.route("/<trip_id>/add_transportation", methods=["GET", "POST"])
def add_transport(trip_id):
    try:
        db = current_app.db
        trip = db.trips.find_one({"_id": ObjectId(trip_id)})
        if not trip:
            return "Trip not found", 404

        form = TransportForm(trip=trip)
        cost=float(form.cost.data) if form.cost.data else 0.0
        currency = form.currency.data


        if form.validate_on_submit():
            new_activity = {
                "id": str(ObjectId()),
                "category": 'transportation',
                "title": form.title.data,
                "confirmed": form.confirmed.data,
                "departure": form.departure.data,
                "arrival": form.arrival.data,
                "cost": cost,
                "currency": currency,
                "cost_in_USD": convert_to_USD(cost,currency),
                "duration": form.duration.data,
            }
            db.trips.update_one({"_id": ObjectId(trip_id)}, {"$push": {"activities": new_activity}})
            return redirect(url_for("trip.view_trip", trip_id=trip_id))

        return render_template("cards/add_transport.html", form=form, trip=trip)

    except Exception as e:
        return f"Erro: {e}", 500


@trip_bp.route("/<trip_id>/add_accommodation", methods=["GET", "POST"])
def add_accommodation(trip_id):
    db = current_app.db
    trip = db.trips.find_one({"_id": ObjectId(trip_id)})
    if not trip:
        return "Trip not found", 404

    form = AccommodationForm(trip=trip)
    cost = float(form.cost.data) if form.cost.data else 0.0
    currency = form.currency.data
    photo=""

    if form.validate_on_submit():
        new_activity = {
            "id": str(ObjectId()),
            "category": "accommodation",
            "title": form.title.data,
            "address": form.address.data,
            "confirmed": form.confirmed.data,
            "photo": photo,
            "cost": cost,
            "currency": currency,
            "cost_in_USD": convert_to_USD(cost, currency),
            "duration": form.duration.data,
        }
        db.trips.update_one({"_id": ObjectId(trip_id)}, {"$push": {"activities": new_activity}})
        return redirect(url_for("trip.view_trip", trip_id=trip_id))

    return render_template("cards/add_accommodation.html", form=form, trip=trip)



@trip_bp.route("/<trip_id>/add_activity", methods=["GET", "POST"])
def add_activity(trip_id):
    db = current_app.db
    trip = db.trips.find_one({"_id": ObjectId(trip_id)})
    if not trip:
        return "Trip not found", 404

    form = ActivityForm(trip=trip)
    photo=""
    cost = float(form.cost.data) if form.cost.data else 0.0
    currency = form.currency.data

    if form.validate_on_submit():
        new_activity = {
            "id": str(ObjectId()),
            "category":"activity",
            "title": form.title.data,
            "confirmed": form.confirmed.data,
            "address": form.address.data,
            "photo": photo,
            "cost": cost,
            "currency": currency,
            "cost_in_USD": convert_to_USD(cost, currency),
            "type": form.type.data,
            "obs": form.obs.data,
        }
        db.trips.update_one({"_id": ObjectId(trip_id)}, {"$push": {"activities": new_activity}})
        return redirect(url_for("trip.view_trip", trip_id=trip_id))

    return render_template("cards/add_activity.html", form=form, trip=trip)


@trip_bp.route("/<trip_id>/add_food", methods=["GET", "POST"])
def add_food(trip_id):
    db = current_app.db
    trip = db.trips.find_one({"_id": ObjectId(trip_id)})
    if not trip:
        return "Trip not found", 404

    form = FoodForm(trip=trip)
    cost = float(form.cost.data) if form.cost.data else 0.0
    currency = form.currency.data
    photo = ""
    if form.validate_on_submit():
        new_activity = {
            "id": str(ObjectId()),
            "category": "food",
            "title": form.title.data,
            "confirmed": form.confirmed.data,
            "address": form.address.data,
            "photo": photo,
            "currency": currency,
            "cost": cost,
            "cost_in_USD": convert_to_USD(cost, currency),
            "type": form.type.data,
            "obs": form.obs.data,
        }
        db.trips.update_one({"_id": ObjectId(trip_id)}, {"$push": {"activities": new_activity}})
        return redirect(url_for("trip.view_trip", trip_id=trip_id))

    return render_template("cards/add_food.html", form=form, trip=trip)

@trip_bp.route("/<trip_id>/activity/<activity_id>")
def view_activity(trip_id, activity_id):
    db = current_app.db
    trip = db.trips.find_one({"_id": ObjectId(trip_id)})
    if not trip:
        return "Trip not found", 404

    activity = next((a for a in trip.get("activities", []) if a["id"] == activity_id), None)
    if not activity:
        return "Activity not found", 404

    return render_template("cards/view_activity.html", activity=activity)