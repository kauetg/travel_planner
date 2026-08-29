import uuid

from flask import Blueprint, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from .utils import convert_to_USD, upload_image_to_cloudinary, DEFAULT_IMGS, ICON_MAP
from .access import get_trip_or_403
from flask import current_app, render_template
from bson import ObjectId
from datetime import datetime
from collections import defaultdict

trip_bp = Blueprint('trip', __name__, url_prefix='/trip')

def serialize_trip(trip):
    trip['_id'] = str(trip['_id'])
    if trip.get('leader_id'):
        trip['leader_id'] = str(trip['leader_id'])
    if trip.get('member_ids'):
        trip['member_ids'] = [str(uid) for uid in trip['member_ids']]
    if trip.get('from_plan_id'):
        trip['from_plan_id'] = str(trip['from_plan_id'])
    for activity in trip.get('activities', []):
        activity['id'] = str(activity['id'])
    return trip




@trip_bp.route("/<trip_id>")
@login_required
def view_trip(trip_id):
    db = current_app.db
    trip = get_trip_or_403(db, trip_id)

    # Formata as datas para exibição
    trip["dates_formatted"] = [
        datetime.strptime(d, "%Y-%m-%d").strftime("%d-%b") for d in trip["dates"]
    ]

    categories = [
  {'category': 'transportation', 'label': 'Transp', 'icon': 'bi-airplane-fill'},
  {'category': 'accommodation',  'label': 'Accomm',  'icon': 'bi-house-door-fill'},
  {'category': 'activity',       'label': 'Activities',     'icon': 'bi-camera-fill'},
  {'category': 'food',           'label': 'Food',           'icon': 'bi-cup-hot-fill'},
]

    # --- INICIO: cálculo de valores agregados ---
    total_usd = 0
    category_totals = defaultdict(float)
    category_daily = defaultdict(lambda: defaultdict(float))
    total_per_day = defaultdict(float)
    most_expensive_item = None
    max_cost = 0

    for act in trip.get("activities", []):
        cost = act.get("cost_in_USD", 0) or 0
        total_usd += cost
        cat = act.get("category", "other")
        category_totals[cat] += cost
        day = act.get("start_date", "N/A")
        category_daily[cat][day] += cost
        total_per_day[day] += cost
        # Item mais caro
        if cost > max_cost:
            max_cost = cost
            most_expensive_item = f"{act.get('title', '???')} ({cat})"

    # Médias por dia
    num_days = len(trip.get("dates", [])) or 1
    avg_per_day = round(total_usd / num_days, 2)
    category_avg = {cat: round(v / num_days, 2) for cat, v in category_totals.items()}

    # Preparando variáveis para template
    context = {
        "trip": trip,
        "categories": categories,
        "total_usd": round(total_usd,2),
        "avg_per_day": avg_per_day,
        "food_usd": round(category_totals.get("food",0),2),
        "food_avg": category_avg.get("food",0),
        "trans_usd": round(category_totals.get("transportation",0),2),
        "trans_avg": category_avg.get("transportation",0),
        "accom_usd": round(category_totals.get("accommodation",0),2),
        "accom_avg": category_avg.get("accommodation",0),
        "act_usd": round(category_totals.get("activity",0),2),
        "act_avg": category_avg.get("activity",0),
        "daily_category": category_daily,
        "total_category": category_totals,
        "total_per_day": total_per_day,
        "most_expensive_item": most_expensive_item,
        "current_app": current_app
    }
    # --- FIM: cálculo de valores agregados ---

    trip = serialize_trip(trip)
    return render_template("trip_detail.html", **context)






@trip_bp.route("/<trip_id>/delete/<activity_id>", methods=["POST"])
@login_required
def delete_activity(trip_id, activity_id):
    db = current_app.db
    get_trip_or_403(db, trip_id)

    result = db.trips.update_one(
        {"_id": ObjectId(trip_id)},
        {"$pull": {"activities": {"id": activity_id}}}
    )

    if result.modified_count == 0:
        return "Activity not found or not deleted", 404

    return redirect(url_for("trip.view_trip", trip_id=trip_id))





@trip_bp.route('/<trip_id>/add_link', methods=['POST'])
@login_required
def add_link(trip_id):
    db = current_app.db
    get_trip_or_403(db, trip_id)

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
@login_required
def delete_info(trip_id, info_id):
    db = current_app.db
    trip = get_trip_or_403(db, trip_id)

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
@login_required
def edit_trip_form(trip_id):
    db = current_app.db
    trip = get_trip_or_403(db, trip_id)
    return render_template("trip/_trip_form.html", trip=trip)


@trip_bp.route("/<trip_id>/members", methods=["GET"])
@login_required
def members_modal(trip_id):
    db = current_app.db
    trip = get_trip_or_403(db, trip_id)

    members = list(db.users.find({"_id": {"$in": trip.get("member_ids", [])}}))
    for m in members:
        m["_id"] = str(m["_id"])

    is_leader = str(trip.get("leader_id")) == current_user.id
    return render_template(
        "trip/_modal_members.html",
        trip_id=str(trip["_id"]),
        members=members,
        is_leader=is_leader,
        leader_id=str(trip.get("leader_id")),
    )


@trip_bp.route("/<trip_id>/add_member", methods=["POST"])
@login_required
def add_member(trip_id):
    db = current_app.db
    get_trip_or_403(db, trip_id, leader_only=True)

    email = request.form.get("email", "").strip().lower()
    user = db.users.find_one({"email": email})
    if not user:
        return jsonify({"error": f"No account with email {email} yet. Create one first."}), 404

    db.trips.update_one(
        {"_id": ObjectId(trip_id)},
        {"$addToSet": {"member_ids": user["_id"]}}
    )
    return jsonify({"ok": True})


@trip_bp.route("/<trip_id>/remove_member", methods=["POST"])
@login_required
def remove_member(trip_id):
    db = current_app.db
    trip = get_trip_or_403(db, trip_id, leader_only=True)

    user_id = request.form.get("user_id", "")
    if user_id == str(trip.get("leader_id")):
        return jsonify({"error": "Can't remove the trip leader."}), 400

    db.trips.update_one(
        {"_id": ObjectId(trip_id)},
        {"$pull": {"member_ids": ObjectId(user_id)}}
    )
    return jsonify({"ok": True})


@trip_bp.route("/<trip_id>/delete", methods=["POST"])
@login_required
def delete_trip(trip_id):
    db = current_app.db
    trip = get_trip_or_403(db, trip_id, leader_only=True)

    result = db.trips.delete_one({"_id": ObjectId(trip_id)})

    if result.deleted_count == 0:
        return "Trip not found or could not be deleted", 404

    if trip.get("from_plan_id"):
        db.plans.update_one(
            {"_id": trip["from_plan_id"]},
            {"$set": {"converted_trip_id": None}}
        )

    return redirect(url_for("home.index"))


@trip_bp.route("/<trip_id>/add_activity", methods=["POST"])
@login_required
def add_activity(trip_id):
    db = current_app.db
    get_trip_or_403(db, trip_id)

    # ── Campos comuns ─────────────────────────────────
    category = request.form.get("category", "").strip()
    title = request.form.get("title", "").strip()

    if not category or not title:
        return jsonify({"error": "Title and category are required"}), 400

    type_ = request.form.get("type", "Other")
    cost = float(request.form.get("cost", 0) or 0)
    currency = request.form.get("currency", "USD")
    confirmed = request.form.get("confirmed") == "true"
    obs = request.form.get("obs", "").strip()
    start_date = request.form.get("start_date", "").strip()

    # ── Foto ──────────────────────────────────────────
    photo_file = request.files.get("photo")
    if photo_file and photo_file.filename:
        img_url = upload_image_to_cloudinary(photo_file)
    else:
        img_url = DEFAULT_IMGS.get(category, "/static/img/cards/default_activity.png")

    # ── Monta documento ───────────────────────────────
    activity = {
        "id": str(ObjectId()),
        "category": category,
        "title": title,
        "confirmed": confirmed,
        "cost": cost,
        "currency": currency,
        "cost_in_USD": convert_to_USD(cost, currency),
        "type": type_,
        "icon": ICON_MAP.get(type_, "bi-geo"),
        "obs": obs,
        "img": img_url,
        "start_date": start_date,
    }

    # ── Campos específicos por categoria ──────────────
    if category == "transportation":
        activity.update({
            "departure": request.form.get("departure", ""),
            "departure_lat": request.form.get("departure_lat", ""),
            "departure_lon": request.form.get("departure_lon", ""),
            "arrival": request.form.get("arrival", ""),
            "arrival_lat": request.form.get("arrival_lat", ""),
            "arrival_lon": request.form.get("arrival_lon", ""),
        })
    else:
        activity.update({
            "address": request.form.get("address", ""),
            "lat": request.form.get("lat", ""),
            "lon": request.form.get("lon", ""),
        })
        duration = int(request.form.get("duration", 0) or 0)
        if duration:
            activity["duration"] = duration

    # Remove strings vazias pra não salvar lixo
    activity = {k: v for k, v in activity.items() if v != ""}

    db.trips.update_one(
        {"_id": ObjectId(trip_id)},
        {"$push": {"activities": activity}}
    )

    return jsonify({"ok": True}), 200


@trip_bp.route("/<trip_id>/activity/<activity_id>")
@login_required
def view_activity(trip_id, activity_id):
    db = current_app.db

    trip = get_trip_or_403(db, trip_id)
    activity = next((a for a in trip["activities"] if a["id"] == activity_id), None)

    # JSON para o edit pré-preenchido
    if request.args.get("format") == "json":
        return jsonify(activity)

    # HTML para o modal de view
    return render_template("trip/view_activity.html", activity=activity, trip=trip)


@trip_bp.route("/<trip_id>/activity/<activity_id>/confirm", methods=["POST"])
@login_required
def confirm_activity(trip_id, activity_id):
    db = current_app.db
    get_trip_or_403(db, trip_id)
    db.trips.update_one(
        {"_id": ObjectId(trip_id), "activities.id": activity_id},
        {"$set": {"activities.$.confirmed": True}}
    )
    return redirect(url_for('trip.view_trip', trip_id=trip_id))


@trip_bp.route("/<trip_id>/activity/<activity_id>/unconfirm", methods=["POST"])
@login_required
def unconfirm_activity(trip_id, activity_id):
    db = current_app.db
    get_trip_or_403(db, trip_id)
    db.trips.update_one(
        {"_id": ObjectId(trip_id), "activities.id": activity_id},
        {"$set": {"activities.$.confirmed": False}}
    )
    return redirect(url_for('trip.view_trip', trip_id=trip_id))


@trip_bp.route("/<trip_id>/update_activity/<activity_id>", methods=["POST"])
@login_required
def update_activity(trip_id, activity_id):
    db = current_app.db
    get_trip_or_403(db, trip_id)

    # monta o dict igual ao add_activity mas SEM novo id
    category = request.form.get("category", "").strip()
    type_ = request.form.get("type", "Other")
    cost = float(request.form.get("cost", 0) or 0)
    currency = request.form.get("currency", "USD")

    photo_file = request.files.get("photo")
    img_url = upload_image_to_cloudinary(photo_file) if photo_file and photo_file.filename else None

    update_fields = {
        "activities.$.title": request.form.get("title", "").strip(),
        "activities.$.type": type_,
        "activities.$.cost": cost,
        "activities.$.currency": currency,
        "activities.$.cost_in_USD": convert_to_USD(cost, currency),
        "activities.$.confirmed": request.form.get("confirmed") == "true",
        "activities.$.obs": request.form.get("obs", "").strip(),
        "activities.$.icon": ICON_MAP.get(type_, "bi-geo"),
        "activities.$.start_date": request.form.get("start_date", "").strip(),
    }

    if img_url:
        update_fields["activities.$.img"] = img_url

    if category == "transportation":
        update_fields.update({
            "activities.$.departure": request.form.get("departure", ""),
            "activities.$.departure_lat": request.form.get("departure_lat", ""),
            "activities.$.departure_lon": request.form.get("departure_lon", ""),
            "activities.$.arrival": request.form.get("arrival", ""),
            "activities.$.arrival_lat": request.form.get("arrival_lat", ""),
            "activities.$.arrival_lon": request.form.get("arrival_lon", ""),
        })
    else:
        update_fields.update({
            "activities.$.address": request.form.get("address", ""),
            "activities.$.lat": request.form.get("lat", ""),
            "activities.$.lon": request.form.get("lon", ""),
        })
        duration = int(request.form.get("duration", 0) or 0)
        if duration:
            update_fields["activities.$.duration"] = duration

    db.trips.update_one(
        {"_id": ObjectId(trip_id), "activities.id": activity_id},
        {"$set": update_fields}
    )

    return jsonify({"ok": True}), 200


# Aloca — chamada quando solta o drag
@trip_bp.route("/<trip_id>/activity/<activity_id>/assign", methods=["POST"])
@login_required
def assign_activity(trip_id, activity_id):
    db = current_app.db
    get_trip_or_403(db, trip_id)
    date = request.json.get("date")
    db.trips.update_one(
        {"_id": ObjectId(trip_id), "activities.id": activity_id},
        {"$set": {"activities.$.start_date": date}}
    )
    return jsonify({"ok": True})

# Desaloca — chamada pelo X
@trip_bp.route("/<trip_id>/activity/<activity_id>/unassign", methods=["POST"])
@login_required
def unassign_activity(trip_id, activity_id):
    db = current_app.db
    get_trip_or_403(db, trip_id)
    db.trips.update_one(
        {"_id": ObjectId(trip_id), "activities.id": activity_id},
        {"$unset": {"activities.$.start_date": ""}}
    )
    return jsonify({"ok": True})