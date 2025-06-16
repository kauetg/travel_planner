from flask import Blueprint
import requests
import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv

load_dotenv()

utils_bp = Blueprint('utils', __name__, url_prefix="/utils")

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

def upload_image_to_cloudinary(file):
    result = cloudinary.uploader.upload(file)
    return result.get("secure_url")




def get_location_data(location):
    api_key = os.getenv("OPENCAGE_API_KEY")
    url = "https://api.opencagedata.com/geocode/v1/json"
    params = {
        'q': location,
        'key': api_key,
        'language': 'en',   # nome dos países em inglês
        'pretty': 1
    }
    response = requests.get(url, params=params)
    data = response.json()

    if data['results']:
        result = data['results'][0]
        components = result['components']

        return {
            'lat': result['geometry']['lat'],
            'lng': result['geometry']['lng'],
            'country': components.get('country'),
            'country_code': components.get('country_code').upper()
        }
    else:
        return response
