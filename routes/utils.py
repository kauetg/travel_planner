from flask import Blueprint
import requests
import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv
import pycountry


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




def currencies(country_name):
    # Lista base que sempre será exibida
    all_currencies = ["USD","SGD", "MYR", "BRL", "EUR"]

    # Tenta descobrir a currency via pycountry
    country = pycountry.countries.get(name=country_name)
    currency_code = None
    if country:
        # Usamos o código alpha_2 para buscar a moeda
        try:
            country_alpha2 = country.alpha_2
            currency = pycountry.currencies.get(numeric=pycountry.countries.get(alpha_2=country_alpha2).numeric)
            if currency:
                currency_code = currency.alpha_3
        except:
            pass

    # Fallback manual por país (caso pycountry não consiga)
    manual_map = {
        "Singapore": "SGD",
        "Malaysia": "MYR",
        "Brazil": "BRL",
        "Thailand": "TBH",
        "United States": "USD",
        "Germany": "EUR",
    }
    currency_code = currency_code or manual_map.get(country_name)

    # Reorganiza a lista colocando a moeda do país em primeiro
    if currency_code:
        if currency_code in all_currencies:
            all_currencies.remove(currency_code)
        all_currencies = [currency_code] + all_currencies

    # Retorna no formato para o SelectField
    return [(c, c) for c in all_currencies]



def convert_to_USD(value, currency):
    if currency == "USD" or not value:
        return value
    try:
        url = f"https://open.er-api.com/v6/latest/{currency}"
        resp = requests.get(url)
        data = resp.json()
        rate = data["rates"].get("USD")
        return round(value * rate, 2) if rate else 0
    except:
        return 0

DEFAULT_IMGS = {
    "transportation": "/static/img/cards/default_transportation.png",
    "accommodation":  "/static/img/cards/default_accommodation.png",
    "activity":       "/static/img/cards/default_activity.png",
    "food":           "/static/img/cards/default_food.png",
}

ICON_MAP = {
    "Plane": "bi-airplane",
    "Boat": "bi-life-preserver",
    "Bus": "bi-bus-front",
    "Car": "bi-car-front",
    "Other": "bi-box",
    "Tour": "bi-person-walking",
    "Dive": "bi-droplet",
    "Museum": "bi-bank",
    "Hike": "bi-tree",
    "Full Meal": "bi-egg-fried",
    "Snacks": "bi-cup-straw",
    "Dessert": "bi-cup-hot",
    "Hotel": "bi-house-door-fill",
    "Airbnb": "bi-house-door-fill",
    "Friends House": "bi-house-door-fill",
}
