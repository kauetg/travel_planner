from flask import Blueprint, render_template, current_app, request, redirect, url_for
from flask_login import login_required, current_user
from bson import ObjectId
from bson.json_util import dumps
from datetime import datetime, timedelta
from .utils import upload_image_to_cloudinary
from .access import get_trip_or_403
from .finance import get_household_id, create_project_for_trip

home_bp = Blueprint('home', __name__)


def get_date_range(start, end):
    delta = end - start

    date_list = [
        (start + timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(delta.days + 1)
    ]
    return date_list


@home_bp.route("/")
@login_required
def index():
    db = current_app.db
    trips = list(db.trips.find({"member_ids": ObjectId(current_user.id)}).sort("start_date", -1))
    for trip in trips:
        trip["_id"] = str(trip["_id"])

    trips_json = dumps(trips)

    plans = list(db.plans.find({
        "member_ids": ObjectId(current_user.id),
        "converted_trip_id": None,
    }).sort("created_at", -1))
    for plan in plans:
        plan["_id"] = str(plan["_id"])

    return render_template("index.html", trips=trips, trips_json=trips_json, plans=plans)



@home_bp.route("/add", methods=["POST"])
@login_required
def add_or_update_trip():
    db = current_app.db

    trip_id = request.form.get("trip_id")
    if trip_id:
        get_trip_or_403(db, trip_id)
    name = request.form.get("name")
    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")
    location = request.form.get("location")
    lat = request.form.get("lat", "").strip()
    lng = request.form.get("lng", "").strip()
    country_name = request.form.get("country_name", "").strip()
    country_code = request.form.get("country_code", "").strip()
    instagram_url = request.form.get("instagram_url", "").strip()
    youtube_url = request.form.get("youtube_url", "").strip()
    rating = request.form.get("rating", "").strip()
    quote = request.form.get("quote", "").strip()
    image_file = request.files.get("image")

    start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
    end_datetime = datetime.strptime(end_date, "%Y-%m-%d")

    img_url = None
    if image_file and image_file.filename:
        img_url = upload_image_to_cloudinary(image_file)

    source_plan = None
    from_plan_id = request.form.get("from_plan_id", "").strip()
    if from_plan_id and not trip_id:
        source_plan = db.plans.find_one({
            "_id": ObjectId(from_plan_id),
            "member_ids": ObjectId(current_user.id),
        })

    update_data = {
        "name": name,
        "start_date": start_datetime,
        "end_date": end_datetime,
        "dates": get_date_range(start_datetime, end_datetime),
        "location": location,
        "year": start_datetime.year,
    }

    if lat and lng:
        update_data["lat"] = float(lat)
        update_data["lng"] = float(lng)
        update_data["country_name"] = country_name
        update_data["country_code"] = country_code

    if instagram_url:
        update_data["instagram_url"] = instagram_url
    if youtube_url:
        update_data["youtube_url"] = youtube_url
    if rating:
        update_data["rating"] = int(rating)
    if quote:
        update_data["quote"] = quote

    if img_url:
        update_data["img"] = img_url

    if trip_id:
        db.trips.update_one({"_id": ObjectId(trip_id)}, {"$set": update_data})
    else:
        plan_img = source_plan.get("img") if source_plan else None
        update_data["img"] = img_url or plan_img or "https://placehold.co/600x400"  # default fallback
        update_data["leader_id"] = ObjectId(current_user.id)
        update_data["member_ids"] = [ObjectId(current_user.id)]
        inserted = db.trips.insert_one(update_data)
        trip_id = str(inserted.inserted_id)

        if end_datetime >= datetime.now():
            household_id = get_household_id(current_app.finance_db, current_user.email)
            if household_id:
                project_id = create_project_for_trip(
                    current_app.finance_db, household_id, name, start_datetime, end_datetime
                )
                db.trips.update_one({"_id": inserted.inserted_id}, {"$set": {"finance_project_id": project_id}})

        if source_plan:
            db.plans.update_one(
                {"_id": source_plan["_id"]},
                {"$set": {"converted_trip_id": ObjectId(trip_id)}}
            )
            db.trips.update_one(
                {"_id": ObjectId(trip_id)},
                {"$set": {"from_plan_id": source_plan["_id"]}}
            )

    return redirect(url_for("trip.view_trip", trip_id=trip_id))
