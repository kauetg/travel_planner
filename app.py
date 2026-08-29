from flask import Flask, send_from_directory
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash

from routes.home import home_bp
from routes.trip import trip_bp
from routes.utils import utils_bp
from routes.auth import auth_bp, login_manager
from routes.plans import plan_bp

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

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


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port)