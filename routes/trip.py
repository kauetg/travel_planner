import uuid

from flask import Blueprint, render_template, current_app, request, redirect, url_for, jsonify
from bson import ObjectId
from datetime import datetime
from .utils import convert_to_USD, icon_map
from .forms import TransportForm, AccommodationForm, ActivityForm, FoodForm

trip_bp = Blueprint('trip', __name__, url_prefix='/trip')


def get_form_and_template(category):
    return {
        "transportation": (TransportForm, "cards/add_transport.html"),
        "accommodation": (AccommodationForm, "cards/add_accommodation.html"),
        "activity": (ActivityForm, "cards/add_activity.html"),
        "food": (FoodForm, "cards/add_food.html"),
    }[category]


def serialize_trip(trip):
    trip['_id'] = str(trip['_id'])
    for activity in trip.get('activities', []):
        activity['id'] = str(activity['id'])
    return trip


@trip_bp.route("/<trip_id>")
def view_trip(trip_id):
    db = current_app.db
    trip = db.trips.find_one({"_id": ObjectId(trip_id)})
    trip["dates_formatted"] = [
        datetime.strptime(d, "%Y-%m-%d").strftime("%d-%b") for d in trip["dates"]
    ]
    categories = [
        {"label": "Things to do", "icon": "bi-clipboard-check", "category": "activity"},
        {"label": "Places to eat", "icon": "bi-fork-knife", "category": "food"},
        {"label": "Accommodation", "icon": "bi-house-door-fill", "category": "accommodation"},
        {"label": "Transportation", "icon": "bi-airplane-fill", "category": "transportation"},
    ]
    trip = serialize_trip(trip)
    return render_template("trip_detail.html", trip=trip, categories=categories, current_app=current_app)


@trip_bp.route("/<trip_id>/add_<category>", methods=["GET", "POST"])
def add_activity_by_category(trip_id, category):
    db = current_app.db
    trip = db.trips.find_one({"_id": ObjectId(trip_id)})
    if not trip:
        return "Trip not found", 404

    form_class, template = get_form_and_template(category)
    form = form_class(trip=trip)

    cost = float(form.cost.data) if form.cost.data else 0.0
    currency = form.currency.data
    type_ = form.type.data
    icon = icon_map.get(type_, "bi-geo")


    if form.validate_on_submit():
        activity = {
            "id": str(ObjectId()),
            "category": category,
            "title": form.title.data,
            "confirmed": form.confirmed.data,
            "cost": cost,
            "currency": currency,
            "cost_in_USD": convert_to_USD(cost, currency),
            "type": type_,
            "icon": icon,
            "photo": (
                form.departure_map_image.data if category == "transportation"
                else getattr(form, "photo", None).data if hasattr(form, "photo") else ""
            ),
            "address": getattr(form, "address", None).data if hasattr(form, "address") else "",
            "obs": getattr(form, "obs", None).data if hasattr(form, "obs") else "",
            "duration": getattr(form, "duration", None).data if hasattr(form, "duration") else "",
            "departure": getattr(form, "departure", None).data if hasattr(form, "departure") else "",
            "departure_lat": getattr(form, "departure_lat", None).data if hasattr(form, "departure_lat") else "",
            "departure_lon": getattr(form, "departure_lon", None).data if hasattr(form, "departure_lon") else "",
            "arrival": getattr(form, "arrival", None).data if hasattr(form, "arrival") else "",
            "arrival_lat": getattr(form, "arrival_lat", None).data if hasattr(form, "arrival_lat") else "",
            "arrival_lon": getattr(form, "arrival_lon", None).data if hasattr(form, "arrival_lon") else "",
        }

        # Remove campos None pra não salvar lixo
        activity = {k: v for k, v in activity.items() if v not in [None, ""]}

        db.trips.update_one(
            {"_id": ObjectId(trip_id)},
            {"$push": {"activities": activity}}
        )
        return redirect(url_for("trip.view_trip", trip_id=trip_id))

    return render_template(template, form=form, trip=trip)


@trip_bp.route("/<trip_id>/activity/<activity_id>", methods=["GET", "POST"])
def view_or_edit_activity(trip_id, activity_id):
    db = current_app.db
    trip = db.trips.find_one({"_id": ObjectId(trip_id)})
    if not trip:
        return "Trip not found", 404

    activity = next((a for a in trip.get("activities", []) if a["id"] == activity_id), None)
    if not activity:
        return "Activity not found", 404

    edit_mode = request.args.get("mode") == "edit"
    form_class, template = get_form_and_template(activity["category"])
    form = form_class(trip=trip, data=activity)

    if edit_mode and form.validate_on_submit():
        updated_activity = {
            **activity,
            "title": form.title.data,
            "confirmed": form.confirmed.data,
            "cost": float(form.cost.data) if form.cost.data else 0.0,
            "currency": form.currency.data,
            "cost_in_USD": convert_to_USD(float(form.cost.data or 0.0), form.currency.data),
            "type": form.type.data,
            "icon": icon_map[form.type.data],
        }

        if activity["category"] == "transportation":
            updated_activity["departure"] = form.departure.data
            updated_activity["arrival"] = form.arrival.data
            updated_activity["duration"] = form.duration.data
        elif activity["category"] == "accommodation":
            updated_activity["address"] = form.address.data
            updated_activity["duration"] = form.duration.data
        elif activity["category"] in ["activity", "food"]:
            updated_activity["address"] = form.address.data
            updated_activity["obs"] = form.obs.data

        db.trips.update_one(
            {"_id": ObjectId(trip_id)},
            {"$set": {"activities.$[elem]": updated_activity}},
            array_filters=[{"elem.id": activity_id}]
        )

        return redirect(url_for("trip.view_trip", trip_id=trip_id))

    return render_template(
        "cards/view_activity.html",
        form=form,
        trip=trip,
        activity=activity,
        edit_mode=edit_mode
    )


@trip_bp.route("/<trip_id>/delete/<activity_id>", methods=["POST"])
def delete_activity(trip_id, activity_id):
    db = current_app.db

    result = db.trips.update_one(
        {"_id": ObjectId(trip_id)},
        {"$pull": {"activities": {"id": activity_id}}}
    )

    if result.modified_count == 0:
        return "Activity not found or not deleted", 404

    return redirect(url_for("trip.view_trip", trip_id=trip_id))


@trip_bp.route('/<trip_id>/add_info_modal')
def add_info_modal(trip_id):
    return render_template('cards/add_info.html')


@trip_bp.route('/<trip_id>/add_link', methods=['POST'])
def add_link(trip_id):
    data = request.get_json()

    # Validação básica
    if not data or not data.get('title'):
        return jsonify({'error': 'Missing title'}), 400

    extra_info = {
        "id": str(uuid.uuid4()),  # gera ID único
        "title": data['title'],
        "url": data.get('url', ''),
        "obs": data.get('notes', ''),
        "confirmed": False  # você pode mudar isso depois com edição
    }

    # Adiciona ao array extra_infos
    db = current_app.db
    trips_collection = db.trips
    result = trips_collection.update_one(
        {"_id": ObjectId(trip_id)},
        {"$push": {"extra_infos": extra_info}}
    )

    if result.modified_count == 1:
        return jsonify({'message': 'Saved successfully'}), 200
    else:
        return jsonify({'error': 'Trip not found or not updated'}), 500


@trip_bp.route('/trip/<trip_id>/delete_info/<info_id>', methods=['POST'])
def delete_info(trip_id, info_id):
    db = current_app.db
    trip = db.trips.find_one({"_id": ObjectId(trip_id)})


    # Remove o item com o info_id
    original_count = len(trip['extra_infos'])
    trip['extra_infos'] = [
        info for info in trip.get('extra_infos', [])
        if str(info.get('id')) != str(info_id)
    ]

    if len(trip['extra_infos']) < original_count:
        result = db.trips.update_one(
            {"_id": ObjectId(trip_id)},
            {"$pull": {"extra_infos": {"id": info_id}}}
        )

    return redirect(url_for("trip.view_trip", trip_id=trip_id))

@trip_bp.route("/<trip_id>/edit", methods=["GET"])
def edit_trip_form(trip_id):
    db = current_app.db
    trip = db.trips.find_one({"_id": ObjectId(trip_id)})
    return render_template("_trip_form.html", trip=trip)

@trip_bp.route("/<trip_id>/delete", methods=["POST"])
def delete_trip(trip_id):
    db = current_app.db

    result = db.trips.delete_one({"_id": ObjectId(trip_id)})

    if result.deleted_count == 0:
        return "Trip not found or could not be deleted", 404

    return redirect(url_for("home.index"))