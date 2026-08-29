import os

from flask import Blueprint, render_template, current_app, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from bson import ObjectId
from werkzeug.security import check_password_hash, generate_password_hash
from itsdangerous import URLSafeTimedSerializer, BadData

auth_bp = Blueprint('auth', __name__)

RESET_TOKEN_MAX_AGE = 600  # 10 minutes
OWNER_EMAILS = {"kauetg@gmail.com", "barbaracvilla@gmail.com"}


def _reset_serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt="password-reset")

login_manager = LoginManager()
login_manager.login_view = 'auth.login'


class User(UserMixin):
    def __init__(self, doc):
        self.id = str(doc["_id"])
        self.email = doc["email"]
        self.name = doc.get("name", "")


@login_manager.user_loader
def load_user(user_id):
    db = current_app.db
    doc = db.users.find_one({"_id": ObjectId(user_id)})
    return User(doc) if doc else None


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        db = current_app.db
        doc = db.users.find_one({"email": email})

        if doc and check_password_hash(doc["password_hash"], password):
            login_user(User(doc), remember=True)
            return redirect(url_for("home.index"))

        flash("Invalid email or password.")

    return render_template("auth/login.html")


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        code = request.form.get("code", "")
        db = current_app.db

        required_code = os.getenv("OWNER_RESET_CODE") if email in OWNER_EMAILS else os.getenv("RESET_CODE")
        if not required_code or code != required_code:
            flash("Invalid access code.")
            return render_template("auth/forgot_password.html")

        if not db.users.find_one({"email": email}):
            flash("No account found with that email.")
            return render_template("auth/forgot_password.html")

        token = _reset_serializer().dumps(email)
        return redirect(url_for("auth.reset_password", token=token))

    return render_template("auth/forgot_password.html")


@auth_bp.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    token = request.values.get("token", "")

    try:
        email = _reset_serializer().loads(token, max_age=RESET_TOKEN_MAX_AGE)
    except BadData:
        flash("This reset link is invalid or expired. Please try again.")
        return redirect(url_for("auth.forgot_password"))

    db = current_app.db
    if not db.users.find_one({"email": email}):
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")

        if not password or password != confirm:
            flash("Passwords do not match.")
            return render_template("auth/reset_password.html", token=token)

        db.users.update_one(
            {"email": email},
            {"$set": {"password_hash": generate_password_hash(password)}},
        )
        flash("Password updated. You can sign in now.")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", token=token)


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
