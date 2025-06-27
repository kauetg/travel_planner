from flask import Flask
from pymongo import MongoClient
from dotenv import load_dotenv
import os

from routes.home import home_bp
from routes.trip import trip_bp
from routes.utils import utils_bp

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
app.db = client["travel_planner"]
app.config["MAPBOX_PUBLIC_TOKEN"] = os.environ.get("MAPBOX_PUBLIC_TOKEN")



# Blueprints
app.register_blueprint(home_bp)
app.register_blueprint(trip_bp, url_prefix="/trip")
app.register_blueprint(utils_bp, url_prefix="/utils")

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)