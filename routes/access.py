from flask import abort
from flask_login import current_user
from bson import ObjectId


def get_trip_or_403(db, trip_id, leader_only=False):
    trip = db.trips.find_one({"_id": ObjectId(trip_id)})
    if not trip:
        abort(404)

    user_oid = ObjectId(current_user.id)

    if leader_only:
        if trip.get("leader_id") != user_oid:
            abort(403)
    elif user_oid not in trip.get("member_ids", []):
        abort(403)

    return trip


def get_plan_or_403(db, plan_id, leader_only=False):
    plan = db.plans.find_one({"_id": ObjectId(plan_id)})
    if not plan:
        abort(404)

    user_oid = ObjectId(current_user.id)

    if leader_only:
        if plan.get("leader_id") != user_oid:
            abort(403)
    elif user_oid not in plan.get("member_ids", []):
        abort(403)

    return plan
