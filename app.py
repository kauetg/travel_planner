import click
from flask import Flask, send_from_directory
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash
from bson import ObjectId
from bson.errors import InvalidId

from routes.home import home_bp, get_date_range
from routes.trip import trip_bp
from routes.utils import utils_bp
from routes.auth import auth_bp, login_manager, OWNER_EMAILS
from routes.plans import plan_bp

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SESSION_COOKIE_NAME'] = 'travelplanner_session'

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
app.db = client["travel_planner"]
app.config["MAPBOX_PUBLIC_TOKEN"] = os.environ.get("MAPBOX_PUBLIC_TOKEN")
app.config["CARTO_API_KEY"] = os.environ.get("CARTO_API_KEY")

login_manager.init_app(app)

# Blueprints
app.register_blueprint(home_bp)
app.register_blueprint(trip_bp, url_prefix="/trip")
app.register_blueprint(utils_bp, url_prefix="/utils")
app.register_blueprint(auth_bp)
app.register_blueprint(plan_bp, url_prefix="/plan")


@app.route("/sw.js")
def service_worker():
    response = send_from_directory(app.static_folder, "sw.js")
    response.headers["Content-Type"] = "application/javascript"
    response.headers["Service-Worker-Allowed"] = "/"
    response.headers["Cache-Control"] = "no-cache"
    return response


@app.cli.command("create-user")
def create_user_command():
    """Create a user account: flask create-user"""
    import click
    email = click.prompt("Email").strip().lower()
    name = click.prompt("Name", default="", show_default=False)
    password = click.prompt("Password", hide_input=True, confirmation_prompt=True)

    if app.db.users.find_one({"email": email}):
        click.echo(f"A user with email {email} already exists.")
        return

    app.db.users.insert_one({
        "email": email,
        "name": name,
        "password_hash": generate_password_hash(password),
        "created_at": datetime.now(timezone.utc),
    })
    click.echo(f"Created user {email}.")


@app.cli.command("backfill-trips")
def backfill_trips_command():
    """Assign all trips without an owner to a given user: flask backfill-trips"""
    import click
    email = click.prompt("Owner email").strip().lower()
    user = app.db.users.find_one({"email": email})

    if not user:
        click.echo(f"No user found with email {email}. Create it first with 'flask create-user'.")
        return

    result = app.db.trips.update_many(
        {"leader_id": {"$exists": False}},
        {"$set": {"leader_id": user["_id"], "member_ids": [user["_id"]]}},
    )
    click.echo(f"Updated {result.modified_count} trip(s) to be owned by {email}.")


DATE_FORMATS = ("%d-%b-%Y", "%d/%m/%Y", "%Y-%m-%d")


def _parse_date(raw):
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    raise ValueError(f"'{raw}' doesn't match any of {DATE_FORMATS}")


@app.cli.command("import-trips-csv")
@click.argument("filename", default="trips.csv")
def import_trips_csv_command(filename):
    """Upsert trips from a CSV in /data: flask import-trips-csv [filename]"""
    import csv
    from pathlib import Path

    path = Path("data") / filename
    if not path.exists():
        click.echo(f"File not found: {path}")
        return

    owners = list(app.db.users.find({"email": {"$in": list(OWNER_EMAILS)}}))
    if len(owners) < 2:
        found = {o["email"] for o in owners}
        click.echo(f"Expected both owner accounts to exist, only found: {found or 'none'}. "
                   f"Create missing ones with 'flask create-user' first.")
        return
    member_ids = sorted((o["_id"] for o in owners), key=str)
    leader_id = member_ids[0]

    inserted = updated = skipped = 0
    warnings = []

    with path.open(newline="", encoding="utf-8-sig") as f:
        for i, row in enumerate(csv.DictReader(f), start=2):  # start=2: header is row 1
            name = (row.get("name") or "").strip()
            if not name:
                continue

            start_raw = (row.get("start_date") or "").strip()
            end_raw = (row.get("end_date") or "").strip()
            if not start_raw or not end_raw:
                warnings.append(f"row {i} ({name}): missing start_date or end_date, skipped")
                skipped += 1
                continue

            try:
                start_date = _parse_date(start_raw)
                end_date = _parse_date(end_raw)
            except ValueError as e:
                warnings.append(f"row {i} ({name}): bad date format ({e}), skipped")
                skipped += 1
                continue

            update_data = {
                "name": name,
                "start_date": start_date,
                "end_date": end_date,
                "dates": get_date_range(start_date, end_date),
                "location": (row.get("location") or "").strip(),
                "year": start_date.year,
                "img": (row.get("img") or "").strip() or "https://placehold.co/600x400",
                "leader_id": leader_id,
                "member_ids": member_ids,
            }

            lat, lng = (row.get("lat") or "").strip(), (row.get("lng") or "").strip()
            if lat and lng:
                update_data["lat"] = float(lat)
                update_data["lng"] = float(lng)
                update_data["country_name"] = (row.get("country_name") or "").strip()
                update_data["country_code"] = (row.get("country_code") or "").strip()

            for field in ("instagram_url", "youtube_url", "quote"):
                value = (row.get(field) or "").strip()
                if value:
                    update_data[field] = value

            rating = (row.get("rating") or "").strip()
            if rating:
                update_data["rating"] = int(rating)

            raw_id = (row.get("_id") or "").strip()
            if raw_id:
                try:
                    trip_id = ObjectId(raw_id)
                except InvalidId:
                    warnings.append(f"row {i} ({name}): invalid _id '{raw_id}', skipped")
                    skipped += 1
                    continue
                result = app.db.trips.update_one({"_id": trip_id}, {"$set": update_data}, upsert=True)
                if result.matched_count:
                    updated += 1
                else:
                    inserted += 1
            else:
                app.db.trips.insert_one(update_data)
                inserted += 1

    click.echo(f"Inserted {inserted}, updated {updated}, skipped {skipped}.")
    for w in warnings:
        click.echo(f"  - {w}")


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port)